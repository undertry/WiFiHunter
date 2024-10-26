import subprocess
import csv
import os
from monitor_mode import enable_monitor_mode, disable_monitor_mode

# Función para ejecutar airodump-ng y capturar la salida
def run_airodump(interface, output_file, scan_duration):
    print(f"Iniciando escaneo de redes WiFi en {interface}mon durante {scan_duration} segundos...")
    try:
        airodump_command = [
            'sudo', 'airodump-ng', '--write-interval', '1', '--write', output_file, '--output-format', 'csv',
            f'{interface}mon'
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

# Función para encontrar el archivo CSV más reciente de airodump-ng
def get_latest_airodump_csv(output_file_prefix):
    directory = os.path.dirname(output_file_prefix)
    base_filename = os.path.basename(output_file_prefix)
    
    # Buscar todos los archivos con el prefijo dado y terminación en '.csv'
    csv_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.csv')]
    
    if not csv_files:
        return None
    
    # Ordenar los archivos por el sufijo numérico para obtener el más reciente
    csv_files.sort(key=lambda f: int(f.split('-')[-1].split('.')[0]), reverse=True)
    
    return os.path.join(directory, csv_files[0])

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

# Función principal
def main((scan_duration=30):
    interface = 'wlan0'

    print(f"Modo de escaneo seleccionado: {scan_duration} segundos")  # <-- Mensaje de verificación

    # Definir las rutas de salida en la carpeta csv
    csv_folder = 'csv'
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    
    output_file_prefix = os.path.join(csv_folder, 'wifi_networks')
    output_file_csv = f'{output_file_prefix}.csv'

    try:
        # Habilitar modo monitor
        enable_monitor_mode(interface)

        # Ejecutar el escaneo de redes
        run_airodump(interface, output_file_prefix, scan_duration)

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


if __name__ == "__main__":
    main()
