import subprocess
import csv
import os
import json

# Rutas de los archivos CSV y JSON
devices_csv_file = 'csv/devices.csv'
devices_json_file = 'json/devices.json'
selected_network_file = 'json/response.json'

def get_scan_duration():
    mode_file = 'json/scan_mode.json'
    if os.path.exists(mode_file):
        with open(mode_file, 'r') as f:
            data = json.load(f)
            return data.get('duration', 30)  # 30 segundos como predeterminado
    return 30  # Valor predeterminado si no existe el archivo

def get_selected_network():
    if os.path.exists(selected_network_file):
        with open(selected_network_file, 'r') as f:
            return json.load(f)
    else:
        print(f"No se encontró el archivo de red seleccionada: {selected_network_file}")
        return None

def run_airodump_on_selected_network(interface, output_file):
    selected_network = get_selected_network()
    if not selected_network:
        print("No se seleccionó ninguna red para escanear.")
        return

    bssid = selected_network.get('bssid')
    channel = selected_network.get('channel')

    if not bssid or not channel:
        print("Faltan datos de BSSID o canal en la red seleccionada.")
        return

    scan_duration = get_scan_duration()
    print(f"Iniciando escaneo de dispositivos en la red {bssid} (canal {channel}) por {scan_duration} segundos...")

    try:
        airodump_command = [
            'sudo', 'airodump-ng', '--write-interval', '1', '--bssid', bssid,
            '--channel', channel, '--write', output_file, '--output-format', 'csv', f'{interface}mon'
        ]
        process = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait(timeout=scan_duration)
        process.terminate()
        stdout, stderr = process.communicate()
        if stderr:
            print(f"Errores:\n{stderr.decode()}")
        else:
            print("Escaneo completado.")
    except subprocess.TimeoutExpired:
        process.terminate()
        print("Tiempo de escaneo terminado.")
    except Exception as e:
        print(f"Ocurrió un error al ejecutar airodump-ng: {e}")

def parse_airodump_csv(input_file, output_file):
    # Campos para dispositivos conectados
    fields_devices = ['Station MAC', 'Power', 'Frames', 'BSSID']
    connected_devices = []

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        in_stations_section = False

        for row in reader:
            # Detectar inicio de la sección de dispositivos conectados
            if len(row) > 0 and row[0] == 'Station MAC':
                in_stations_section = True
                continue

            # Procesar dispositivos conectados
            if in_stations_section and len(row) > 6:
                connected_devices.append({
                    'Station MAC': row[0].strip(),
                    'Power': row[3].strip(),
                    'Frames': row[4].strip(),
                    'BSSID': row[5].strip()
                })

    # Guardar datos de dispositivos en el CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields_devices)
        writer.writeheader()
        for device in connected_devices:
            writer.writerow(device)

    print(f"Datos de dispositivos conectados guardados en {output_file}")

    # Convertir los datos a JSON y guardarlos
    output_json = {"Connected Devices": connected_devices}
    with open(devices_json_file, 'w') as json_file:
        json.dump(output_json, json_file, indent=4)

    print(f"Datos de dispositivos conectados convertidos a JSON y guardados en: {devices_json_file}")

def get_latest_airodump_csv(output_file_prefix):
    # Obtener la carpeta y el prefijo del nombre de archivo
    directory = os.path.dirname(output_file_prefix)
    base_filename = os.path.basename(output_file_prefix)

    # Buscar todos los archivos con el prefijo y extensión '.csv'
    csv_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.csv')]

    if not csv_files:
        return None  # No hay archivos CSV

    # Filtrar archivos que contienen sufijos numéricos al final
    valid_csv_files = [f for f in csv_files if f.split('-')[-1].split('.')[0].isdigit()]

    if not valid_csv_files:
        return None  # No hay archivos válidos con sufijos numéricos

    # Ordenar archivos para obtener el más reciente basado en el sufijo numérico
    valid_csv_files.sort(key=lambda f: int(f.split('-')[-1].split('.')[0]), reverse=True)

    # Retornar la ruta del archivo CSV más reciente
    return os.path.join(directory, valid_csv_files[0])

def main():
    interface = 'wlan0'
    csv_folder = 'csv'
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    output_file_prefix = os.path.join(csv_folder, 'devices')
    output_file_csv = f'{output_file_prefix}.csv'

    try:
        # Ejecutar el escaneo de dispositivos en la red seleccionada
        run_airodump_on_selected_network(interface, output_file_prefix)

        # Obtener y procesar el archivo CSV más reciente
        latest_csv_file = get_latest_airodump_csv(output_file_prefix)
        if latest_csv_file:
            print(f"Analizando archivo más reciente: {latest_csv_file}")
            parse_airodump_csv(latest_csv_file, output_file_csv)
        else:
            print(f"Error: No se encontraron archivos de salida de airodump-ng.")
    except Exception as e:
        print(f"Ocurrió un error durante el escaneo: {e}")

if __name__ == "__main__":
    main()
