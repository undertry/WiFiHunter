import wifi_scan
import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

WIFI_JSON_FILE = 'json/wifi_networks.json'
NMAP_JSON_FILE = 'json/nmap_scan_results.json'

# Ruta para guardar el modo y la duración seleccionados
@app.route('/set-scan-mode', methods=['POST'])
def set_scan_mode():
    data = request.json
    if not data or 'mode' not in data or 'duration' not in data:
        return jsonify({'error': 'No mode or duration data received'}), 400

    scan_mode = data['mode'].lower()
    duration = data['duration']

    # Validar que el modo sea válido
    if scan_mode not in ['rapido', 'intermedio', 'profundo']:
        return jsonify({'error': 'Invalid mode selected'}), 400

    # Guardar el modo y la duración en un archivo JSON
    mode_file = 'json/scan_mode.json'
    with open(mode_file, 'w') as f:
        json.dump({'mode': scan_mode, 'duration': duration}, f, indent=4)

    return jsonify({'message': f'Scan mode set to {scan_mode} with duration {duration} seconds'}), 200

# Ruta para escanear redes WiFi y devolver los resultados
@app.route('/scan', methods=['GET'])
def scan():
    if os.path.exists(WIFI_JSON_FILE):
        with open(WIFI_JSON_FILE, 'r') as json_file:
            networks = json.load(json_file)
    else:
        csv_file = wifi_scan.scan_wifi('wlan0')
        if csv_file:
            wifi_networks = wifi_scan.parse_csv(csv_file)
            wifi_scan.save_to_csv(wifi_networks, output_file='csv/wifi_networks.csv')
            with open(WIFI_JSON_FILE, 'w') as json_file:
                json.dump(wifi_networks, json_file, indent=4)
            networks = wifi_networks
        else:
            networks = {"error": "No se pudo realizar el escaneo."}

    return jsonify(networks), 200

# Ruta para guardar la red seleccionada
@app.route('/save-network', methods=['POST'])
def save_network():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received'}), 400

    # Verifica si la carpeta 'json' existe, si no, la crea
    if not os.path.exists('json'):
        os.makedirs('json')

    # Guarda el archivo en la carpeta 'json'
    with open('json/respuesta.json', 'w') as f:
        json.dump(data, f, indent=4)

    return jsonify({'message': 'Network saved successfully'}), 200

@app.route('/nmap/ports-services', methods=['GET'])
def get_ports_services():
    if os.path.exists(NMAP_JSON_FILE):
        with open(NMAP_JSON_FILE, 'r') as json_file:
            nmap_data = json.load(json_file)
        
        # Si nmap_data es una lista, obtenemos el primer elemento
        if isinstance(nmap_data, list) and len(nmap_data) > 0:
            nmap_data = nmap_data[0]

        response_data = {
            "ip": nmap_data.get("ip", "N/A"),
            "mac": nmap_data.get("mac", "N/A"),
            "ports_services": nmap_data.get("ports_services", []),
            "os_info": nmap_data.get("os_info", "N/A")
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Nmap scan result not found."}), 404

@app.route('/nmap/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    if os.path.exists(NMAP_JSON_FILE):
        with open(NMAP_JSON_FILE, 'r') as json_file:
            nmap_data = json.load(json_file)

        # Verificar si nmap_data es una lista y obtener el primer elemento
        if isinstance(nmap_data, list) and len(nmap_data) > 0:
            nmap_data = nmap_data[0]

        # Extraer vulnerabilidades de cada puerto
        vulnerabilities = []
        ports_services = nmap_data.get("ports_services", [])
        for port_service in ports_services:
            port_vulnerabilities = port_service.get("vulnerabilities", [])
            vulnerabilities.extend(port_vulnerabilities)

        return jsonify({"vulnerabilities": vulnerabilities}), 200
    else:
        return jsonify({"error": "Nmap scan result not found."}), 404



if __name__ == "__main__":
    if not os.path.exists('csv'):
        os.makedirs('csv')

    app.run(host='0.0.0.0', port=5000)
