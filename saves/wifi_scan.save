import subprocess
import csv
import os
import json

# Rutas de los archivos CSV y JSON para las redes WiFi
wifi_csv_file = 'csv/wifi_networks.csv'
wifi_json_file = 'json/wifi_networks.json'
# Función para cargar la duración del escaneo directamente del JSON
def get_scan_duration():
    mode_file = 'json/scan_mode.json'
    if os.path.exists(mode_file):
        with open(mode_file, 'r') as f:
            data = json.load(f)
            return data.get('duration', 30)  # 30 segundos como valor predeterminado
    return 30  # Valor predeterminado si el archivo no existe

# Función para ejecutar airodump-ng y capturar la salida
def run_airodump(interface, output_file):
    scan_duration = get_scan_duration()  # Obtener la duración según el modo
    print(f"Iniciando escaneo de redes WiFi en {interface}mon por {scan_duration} segundos...")

    try:
        airodump_command = [
            'sudo', 'airodump-ng', '--write-interval', '1', '--write', output_file, '--output-format', 'csv', f'{interface}mon'
        ]
        process = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Ejecutar el escaneo durante el tiempo determinado
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

# Función para encontrar el archivo CSV más reciente de airodump-ng
def get_latest_airodump_csv(output_file_prefix):
    directory = os.path.dirname(output_file_prefix)
    base_filename = os.path.basename(output_file_prefix)

    # Buscar todos los archivos con el prefijo dado y terminación en '.csv'
    csv_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.csv')]

    if not csv_files:
        return None

    # Filtrar archivos que contengan sufijos numéricos y omitir otros
    valid_csv_files = []
    for f in csv_files:
        try:
            # Intentar extraer el sufijo numérico para ordenar
            int(f.split('-')[-1].split('.')[0])
            valid_csv_files.append(f)
        except ValueError:
            continue  # Ignorar archivos sin sufijo numérico

    if not valid_csv_files:
        return None  # No hay archivos válidos

    # Ordenar los archivos por el sufijo numérico para obtener el más reciente
    valid_csv_files.sort(key=lambda f: int(f.split('-')[-1].split('.')[0]), reverse=True)

    return os.path.join(directory, valid_csv_files[0])

# Función para analizar el archivo CSV generado por airodump-ng
def parse_airodump_csv(input_file, output_file):
    fields = ['BSSID', 'ESSID', 'Signal', 'Channel', 'Encryption']
    wifi_networks = []

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 14 and row[0] != "BSSID":  # Evitar las cabeceras y filas incompletas
                try:
                    bssid = row[0].strip()
                    essid = row[13].strip()
                    signal = row[8].strip()
                    channel = row[3].strip()
                    encryption = row[5].strip()

                    # Agregar solo las redes con ESSID válido
                    if essid:
                        wifi_networks.append({
                            'BSSID': bssid,
                            'ESSID': essid,
                            'Signal': signal,
                            'Channel': channel,
                            'Encryption': encryption
                        })
                except IndexError:
                    continue

    # Sobrescribir el archivo CSV con los datos esenciales
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(wifi_networks)

    print(f"Datos de redes WiFi guardados en {output_file}")

def csv_to_json_wifi(csv_filepath, json_filepath):
    wifi_networks = []

    try:
        # Comprobar si el archivo CSV existe
        if not os.path.exists(csv_filepath):
            print(f"No se encontró el archivo CSV: {csv_filepath}")
            return

        # Leer el archivo CSV
        with open(csv_filepath, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Filtrar y estructurar los datos relevantes
                wifi_network = {
                    "BSSID": row.get("BSSID", "").strip(),
                    "ESSID": row.get("ESSID", "").strip(),
                    "Signal": row.get("Signal", "").strip(),
                    "Channel": row.get("Channel", "").strip(),
                    "Encryption": row.get("Encryption", "").strip()
                }
                wifi_networks.append(wifi_network)

        # Escribir los datos en formato JSON
        with open(json_filepath, mode='w') as json_file:
            json.dump(wifi_networks, json_file, indent=4)

        print(f"Datos de redes WiFi convertidos a JSON y guardados en: {json_filepath}")

    except Exception as e:
        print(f"Error al convertir el CSV a JSON: {e}")

# Función principal
def main():
    interface = 'wlan0'

    # Definir las rutas de salida en la carpeta csv
    csv_folder = 'csv'
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    
    output_file_prefix = os.path.join(csv_folder, 'wifi_networks')
    output_file_csv = f'{output_file_prefix}.csv'

    try:
        # Ejecutar el escaneo de redes
        run_airodump(interface, output_file_prefix)

        # Obtener el archivo CSV más reciente de airodump-ng
        latest_csv_file = get_latest_airodump_csv(output_file_prefix)
        if latest_csv_file:
            print(f"Analizando archivo más reciente: {latest_csv_file}")
            # Analizar y extraer los datos esenciales
            parse_airodump_csv(latest_csv_file, output_file_csv)
        else:
            print(f"Error: No se encontraron archivos de salida de airodump-ng.")

    except Exception as e:
        print(f"Ocurrió un error durante el escaneo: {e}")

 # Convertir el CSV de redes WiFi a JSON
    csv_to_json_wifi(wifi_csv_file, wifi_json_file)

if __name__ == "__main__":
    main()
