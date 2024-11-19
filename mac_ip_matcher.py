import json
import subprocess
import re
import glob
import os
import csv
import time

def get_latest_csv_file(directory='csv'):
    csv_files = glob.glob(os.path.join(directory, 'devices.csv'))
    if not csv_files:
        raise FileNotFoundError("No CSV files were found in the directory.")
    
    latest_file = max(csv_files, key=os.path.getctime)
    return latest_file

def read_connected_devices_from_csv(csv_file):
    stations = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        capture = False
        for row in csv_reader:
            if len(row) > 0 and row[0].strip() == 'Station MAC':
                capture = True
                continue

            if capture and len(row) > 0 and row[0].strip():  
                mac_address = row[0].strip()  
                if mac_address:
                    stations.append({
                        'station': mac_address
                    })
    return stations

def arp_scan():
    command = ['sudo', 'arp-scan', '--localnet', '--retry=3']
    time.sleep(3)   
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def normalize_mac(mac):
    return mac.lower().replace("-", ":").strip()

def compare_mac_addresses(csv_devices, arp_output):
    matched_devices = []

    for line in arp_output.splitlines():
        if re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line):
            arp_mac = normalize_mac(line.split()[1])
            arp_ip = line.split()[0]

            for device in csv_devices:
                csv_mac = normalize_mac(device['station'])

                if csv_mac == arp_mac:
                    matched_device = {
                        'mac_address': csv_mac,
                        'ip_address': arp_ip
                    }
                    matched_devices.append(matched_device)

    return matched_devices

def save_matched_devices(matched_devices, output_file='json/matched_devices.json'):
    with open(output_file, 'w') as json_file:
        json.dump(matched_devices, json_file, indent=4)
    print(f"Matches stored in {output_file}.")

def main():
    try:
        latest_csv = get_latest_csv_file()
        print(f"Last CSV file: {latest_csv}")
        
        csv_devices = read_connected_devices_from_csv(latest_csv)

        arp_output = arp_scan()
        print("Arp-scan output:", arp_output)          

        matched_devices = compare_mac_addresses(csv_devices, arp_output)

        if matched_devices:
            print(f"{len(matched_devices)} matches were found.")
            save_matched_devices(matched_devices)
        else:
            print("No matches were found.")
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
