import csv
import json
import os

wifi_csv_file = 'csv/wifi_networks.csv'
wifi_json_file = 'json/wifi_networks.json'

device_csv_file = 'csv/device-01.csv'
device_json_file = 'json/connected_devices.json'

def csv_to_json_wifi(csv_filepath, json_filepath):
    wifi_networks = []

    try:
        if not os.path.exists(csv_filepath):
            print(f"CSV file not found: {csv_filepath}")
            return

        with open(csv_filepath, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                wifi_network = {
                    "BSSID": row.get("BSSID", "").strip(),
                    "ESSID": row.get("ESSID", "").strip(),
                    "Signal": row.get("Signal", "").strip(),
                    "Channel": row.get("Channel", "").strip(),
                    "Encryption": row.get("Encryption", "").strip()
                }
                wifi_networks.append(wifi_network)

        with open(json_filepath, mode='w') as json_file:
            json.dump(wifi_networks, json_file, indent=4)

        print(f"WiFi network data converted to JSON and stored in: {json_filepath}")

    except Exception as e:
        print(f"Error converting CSV to JSON: {e}")

def csv_to_json_devices(csv_filepath, json_filepath):
    devices = []

    try:
        if not os.path.exists(csv_filepath):
            print(f"CSV file not found: {csv_filepath}")
            return

        with open(csv_filepath, mode='r') as file:
            csv_reader = csv.reader(file)
            capture = False
            for row in csv_reader:
                if len(row) > 0 and row[0].strip() == 'Station MAC':
                    capture = True
                    continue

                if capture and len(row) > 0 and row[0].strip():  
                    mac_address = row[0].strip()  
                    if mac_address:  
                        device_info = {
                            'station': mac_address,
                            'bssid': row[5].strip()  
                        }
                        devices.append(device_info)

        with open(json_filepath, mode='w') as json_file:
            json.dump(devices, json_file, indent=4)

        print(f"Connected device data converted to JSON and stored in: {json_filepath}")

    except Exception as e:
        print(f"Error converting CSV to JSON: {e}")

if __name__ == "__main__":
    csv_to_json_wifi(wifi_csv_file, wifi_json_file)

    csv_to_json_devices(device_csv_file, device_json_file)
