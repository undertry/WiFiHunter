import json
import subprocess
import re
import glob
import os
import csv
import time

# Función para obtener el último archivo CSV generado
def get_latest_csv_file(directory='csv'):
    csv_files = glob.glob(os.path.join(directory, 'devices.csv'))
    if not csv_files:
        raise FileNotFoundError("No se encontraron archivos CSV en el directorio.")
    
    # Obtener el archivo CSV más reciente
    latest_file = max(csv_files, key=os.path.getctime)
    return latest_file

# Función para leer el último archivo CSV y obtener las MAC de las estaciones conectadas
def read_connected_devices_from_csv(csv_file):
    stations = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        capture = False
        for row in csv_reader:
            # Detectar la sección de estaciones conectadas en el CSV
            if len(row) > 0 and row[0].strip() == 'Station MAC':
                capture = True
                continue

            if capture and len(row) > 0 and row[0].strip():  # Si estamos en la sección correcta
                mac_address = row[0].strip()  # MAC de la estación
                if mac_address:
                    stations.append({
                        'station': mac_address
                    })
    return stations

# Función para ejecutar arp-scan y obtener los dispositivos de la red local
def arp_scan():
    command = ['sudo', 'arp-scan', '--localnet', '--retry=3']
    time.sleep(3)   
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

# Normalizar la dirección MAC (para eliminar problemas de formato)
def normalize_mac(mac):
    return mac.lower().replace("-", ":").strip()

# Función para comparar las MAC del archivo CSV con las de arp-scan
def compare_mac_addresses(csv_devices, arp_output):
    matched_devices = []

    # Normalizar las direcciones MAC de arp-scan a minúsculas
    for line in arp_output.splitlines():
        if re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line):
            arp_mac = normalize_mac(line.split()[1])
            arp_ip = line.split()[0]

            # Comparar con las MAC del archivo CSV (también en formato normalizado)
            for device in csv_devices:
                csv_mac = normalize_mac(device['station'])

                if csv_mac == arp_mac:
                    matched_device = {
                        'mac_address': csv_mac,
                        'ip_address': arp_ip
                    }
                    matched_devices.append(matched_device)

    return matched_devices

# Guardar las coincidencias en un nuevo archivo JSON
def save_matched_devices(matched_devices, output_file='json/matched_devices.json'):
    with open(output_file, 'w') as json_file:
        json.dump(matched_devices, json_file, indent=4)
    print(f"Coincidencias guardadas en {output_file}.")

# Función principal
def main():
    try:
        # Obtener el último archivo CSV
        latest_csv = get_latest_csv_file()
        print(f"Último archivo CSV: {latest_csv}")
        
        # Leer dispositivos conectados del archivo CSV
        csv_devices = read_connected_devices_from_csv(latest_csv)

        # Ejecutar arp-scan y obtener la salida
        arp_output = arp_scan()
        print("Salida de arp-scan:", arp_output)  # Para depuración        

        # Comparar direcciones MAC
        matched_devices = compare_mac_addresses(csv_devices, arp_output)

        if matched_devices:
            print(f"Se encontraron {len(matched_devices)} coincidencias.")
            # Guardar las coincidencias en un archivo JSON
            save_matched_devices(matched_devices)
        else:
            print("No se encontraron coincidencias.")
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
