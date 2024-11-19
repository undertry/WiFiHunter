import subprocess
import csv
import os
import json

wifi_csv_file = 'csv/wifi_networks.csv'
wifi_json_file = 'json/wifi_networks.json'

def get_scan_duration():
    mode_file = 'json/scan_mode.json'
    if os.path.exists(mode_file):
        with open(mode_file, 'r') as f:
            data = json.load(f)
            return data.get('duration', 30)  
    return 30  

def run_airodump(interface, output_file):
    scan_duration = get_scan_duration()  
    print(f"Starting WiFi network scanning in {interface}mon by {scan_duration} seconds...")

    try:
        airodump_command = [
            'sudo', 'airodump-ng', '--write-interval', '1', '--write', output_file, '--output-format', 'csv', f'{interface}mon'
        ]
        process = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        process.wait(timeout=scan_duration)
        
        process.terminate()
        stdout, stderr = process.communicate()
        if stderr:
            print(f"Errores:\n{stderr.decode()}")
        else:
            print("Scanning completed.")
    except subprocess.TimeoutExpired:
        process.terminate()
        print("Scan time completed.")
    except Exception as e:
        print(f"An error occurred while executing airodump-ng: {e}")

def get_latest_airodump_csv(output_file_prefix):
    directory = os.path.dirname(output_file_prefix)
    base_filename = os.path.basename(output_file_prefix)

    csv_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.csv')]

    if not csv_files:
        return None

    valid_csv_files = []
    for f in csv_files:
        try:
            int(f.split('-')[-1].split('.')[0])
            valid_csv_files.append(f)
        except ValueError:
            continue  

    if not valid_csv_files:
        return None  

    valid_csv_files.sort(key=lambda f: int(f.split('-')[-1].split('.')[0]), reverse=True)

    return os.path.join(directory, valid_csv_files[0])

def parse_airodump_csv(input_file, output_file):
    fields = ['BSSID', 'ESSID', 'Signal', 'Channel', 'Encryption']
    wifi_networks = []

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) > 14 and row[0] != "BSSID":  
                try:
                    bssid = row[0].strip()
                    essid = row[13].strip()
                    signal = row[8].strip()
                    channel = row[3].strip()
                    encryption = row[5].strip()

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

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(wifi_networks)

    print(f"WiFi network data stored in {output_file}")

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

def main():
    interface = 'wlan0'

    csv_folder = 'csv'
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    
    output_file_prefix = os.path.join(csv_folder, 'wifi_networks')
    output_file_csv = f'{output_file_prefix}.csv'

    try:
        run_airodump(interface, output_file_prefix)

        latest_csv_file = get_latest_airodump_csv(output_file_prefix)
        if latest_csv_file:
            print(f"Analyzing the most recent file: {latest_csv_file}")
            parse_airodump_csv(latest_csv_file, output_file_csv)
        else:
            print(f" Error: No airodump-ng output files found.")

    except Exception as e:
        print(f"An error occurred during scanning: {e}")

    csv_to_json_wifi(wifi_csv_file, wifi_json_file)

if __name__ == "__main__":
    main()
