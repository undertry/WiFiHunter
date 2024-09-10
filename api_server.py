import wifi_scan
import device_scan
import subprocess
import os
import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

WIFI_JSON_FILE = 'json/wifi_networks.json'
NMAP_JSON_FILE = 'json/nmap_scan_results.json'
DEVICE_JSON_FILE = 'json/matched_devices.json'

# Configuración básica de logging
#logging.basicConfig(filename='json/device_scan.log', level=logging.INFO)

#@app.route('/test', methods=['GET'])
#def test():
#    return jsonify({"message": "Conexión exitosa"})

#@app.route('/create-status-file', methods=['GET'])
#def create_status_file():
#    try:
        # Ruta del archivo a crear
#        file_path = "/home/kali/Documents/nvs_project/api_status.txt"
        
        # Crear el archivo como señal de que la API está funcionando
#        with open(file_path, "w") as file:
#            file.write("API is running")
        
#        return jsonify({"message": "Status file created"}), 200
#    except Exception as e:
#        return jsonify({"error": str(e)}), 500

# Ruta para configurar el modo de escaneo y la duración
@app.route('/set-scan-mode', methods=['POST'])
def set_scan_mode():
    # Obtener los datos JSON enviados en la solicitud POST
    data = request.json
    
    # Validar si los datos JSON existen y contienen los campos 'mode' y 'duration'
    if not data or 'mode' not in data or 'duration' not in data:
        # Si no se recibe 'mode' o 'duration', se devuelve un mensaje de error y un código 400
        return jsonify({'error': 'No mode or duration data received'}), 400

    # Obtener el valor del modo de escaneo y la duración desde el JSON recibido
    scan_mode = data['mode'].lower()  # Convertir el modo a minúsculas para normalizar el valor
    duration = data['duration']

    # Validar que el modo de escaneo sea uno de los modos permitidos
    if scan_mode not in ['quick', 'intermediate', 'deep']:
        # Si el modo es inválido, devolver un mensaje de error y un código 400
        return jsonify({'error': 'Invalid mode selected'}), 400

    # Especificar la ruta y el nombre del archivo JSON donde se guardará el modo y la duración
    mode_file = 'json/scan_mode.json'
    
    # Abrir el archivo JSON en modo escritura para guardar los datos
    with open(mode_file, 'w') as f:
        # Guardar el modo y la duración en formato JSON con indentación para mejor legibilidad
        json.dump({'mode': scan_mode, 'duration': duration}, f, indent=4)

    # Devolver un mensaje de éxito y un código 200
    return jsonify({'message': f'Scan mode set to {scan_mode} with duration {duration} seconds'}), 200


# Ruta para escanear redes WiFi y devolver los resultados en formato JSON
@app.route('/scan', methods=['GET'])
def scan():
    # Verificar si existe un archivo JSON con los resultados de un escaneo previo
    if os.path.exists(WIFI_JSON_FILE):
        # Si existe, abrir el archivo en modo lectura
        with open(WIFI_JSON_FILE, 'r') as json_file:
            # Cargar los datos de redes WiFi desde el archivo JSON
            networks = json.load(json_file)
    else:
        # Si no existe el archivo JSON, realizar un nuevo escaneo de redes WiFi
        # Se llama a la función `scan_wifi` del módulo `wifi_scan` para escanear redes en la interfaz 'wlan0'
        csv_file = wifi_scan.scan_wifi('wlan0')
        
        # Verificar si el escaneo fue exitoso y se generó un archivo CSV con los resultados
        if csv_file:
            # Parsear los datos CSV para extraer la información de las redes WiFi
            wifi_networks = wifi_scan.parse_csv(csv_file)
            
            # Guardar los resultados del escaneo en un archivo CSV para referencia futura
            wifi_scan.save_to_csv(wifi_networks, output_file='csv/wifi_networks.csv')
            
            # Guardar los resultados también en un archivo JSON para fácil acceso en futuros llamados a la ruta
            with open(WIFI_JSON_FILE, 'w') as json_file:
                json.dump(wifi_networks, json_file, indent=4)
            
            # Almacenar los resultados del escaneo en la variable `networks`
            networks = wifi_networks
        else:
            # Si el escaneo falla, devolver un mensaje de error
            networks = {"error": "No se pudo realizar el escaneo."}

    # Devolver los datos de redes WiFi en formato JSON con un código de estado 200
    return jsonify(networks), 200

# Ruta para obtener la lista de dispositivos emparejados
@app.route('/devices', methods=['GET'])
def get_matched_devices():
    # Verificar si existe un archivo JSON con los datos de los dispositivos emparejados
    if os.path.exists(DEVICE_JSON_FILE):
        # Si el archivo existe, abrirlo en modo lectura
        with open(DEVICE_JSON_FILE, 'r') as json_file:
            # Cargar la lista de dispositivos desde el archivo JSON
            devices = json.load(json_file)
    else:
        # Si el archivo no existe, devolver un mensaje de error
        devices = {"error": "El archivo de dispositivos emparejados no existe."}

    # Retornar los datos de los dispositivos en formato JSON con un código de estado 200
    return jsonify(devices), 200


# Ruta para guardar la red seleccionada en un archivo JSON
@app.route('/save-network', methods=['POST'])
def save_network():
    # Obtener los datos JSON enviados en la solicitud POST
    data = request.json

    # Validar que se hayan recibido datos; si no, retornar un error 400
    if not data:
        return jsonify({'error': 'No data received'}), 400

    # Verificar si la carpeta 'json' existe; si no, crearla
    if not os.path.exists('json'):
        os.makedirs('json')

    # Guardar los datos recibidos en un archivo JSON dentro de la carpeta 'json'
    with open('json/respuesta.json', 'w') as f:
        # Almacenar el JSON recibido en 'respuesta.json' con formato legible (indentado)
        json.dump(data, f, indent=4)

    # Devolver una respuesta indicando que la red se guardó correctamente
    return jsonify({'message': 'Network saved successfully'}), 200


# Ruta para obtener información de puertos y servicios desde un archivo de resultados de Nmap
@app.route('/nmap/ports-services', methods=['GET'])
def get_ports_services():
    # Verificar si el archivo JSON de resultados de Nmap existe
    if os.path.exists(NMAP_JSON_FILE):
        # Si el archivo existe, abrirlo en modo lectura
        with open(NMAP_JSON_FILE, 'r') as json_file:
            # Cargar los datos de Nmap desde el archivo JSON
            nmap_data = json.load(json_file)

        # Verificar si `nmap_data` es una lista y tiene al menos un elemento
        # (esto podría suceder si el archivo JSON contiene una lista de resultados)
        if isinstance(nmap_data, list) and len(nmap_data) > 0:
            # Si es una lista, seleccionamos el primer elemento
            nmap_data = nmap_data[0]

        # Extraer la información relevante en un diccionario `response_data`
        response_data = {
            "ip": nmap_data.get("ip", "N/A"),                # IP del dispositivo escaneado, o "N/A" si no se encuentra
            "mac": nmap_data.get("mac", "N/A"),              # Dirección MAC, o "N/A" si no se encuentra
            "ports_services": nmap_data.get("ports_services", []),  # Lista de puertos y servicios
            "os_info": nmap_data.get("os_info", "N/A")       # Información del sistema operativo, o "N/A" si no se encuentra
        }
        
        # Retornar los datos relevantes en formato JSON con un código de éxito 200
        return jsonify(response_data), 200
    else:
        # Si el archivo no existe, devolver un mensaje de error con un código 404
        return jsonify({"error": "Nmap scan result not found."}), 404



@app.route('/start-wifi-scan', methods=['POST'])
def start_wifi_scan():
    try:
        logging.info("Iniciando escaneo de WiFi.")
        # Ejecutar airodump con permisos de root
        subprocess.check_call(['sudo', 'python3', '/home/kali/nvs_project/wifi_scan.py'])
        logging.info("Escaneo de WiFi completado.")
        return jsonify({"message": "Escaneo de WiFi iniciado correctamente"}), 200
    except subprocess.CalledProcessError as e:
        error_message = f"Error al iniciar el escaneo de WiFi: {e}"
        logging.error(error_message)
        return jsonify({"message": error_message}), 500

# Ruta para obtener las vulnerabilidades detectadas en el escaneo de Nmap
@app.route('/nmap/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    # Verificar si el archivo JSON de resultados de Nmap existe
    if os.path.exists(NMAP_JSON_FILE):
        # Si el archivo existe, abrirlo en modo lectura
        with open(NMAP_JSON_FILE, 'r') as json_file:
            # Cargar los datos de Nmap desde el archivo JSON
            nmap_data = json.load(json_file)

        # Si `nmap_data` es una lista con al menos un elemento, obtener el primero
        if isinstance(nmap_data, list) and len(nmap_data) > 0:
            nmap_data = nmap_data[0]

        # Crear una lista para almacenar todas las vulnerabilidades encontradas
        vulnerabilities = []

        # Obtener la lista de puertos y servicios
        ports_services = nmap_data.get("ports_services", [])
        
        # Recorrer cada puerto y servicio para extraer vulnerabilidades
        for port_service in ports_services:
            # Obtener la lista de vulnerabilidades asociadas a cada puerto/servicio
            port_vulnerabilities = port_service.get("vulnerabilities", [])
            # Añadir todas las vulnerabilidades de este puerto a la lista principal
            vulnerabilities.extend(port_vulnerabilities)

        # Devolver las vulnerabilidades encontradas en formato JSON y un código 200
        return jsonify({"vulnerabilities": vulnerabilities}), 200
    else:
        # Si el archivo no existe, devolver un mensaje de error y un código 404
        return jsonify({"error": "Nmap scan result not found."}), 404



if __name__ == "__main__":
    if not os.path.exists('csv'):
        os.makedirs('csv')

    app.run(host='0.0.0.0', port=5000)
