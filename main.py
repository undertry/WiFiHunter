import subprocess
import time
import requests

def run_script(script_name):
    """Ejecuta un script de Python"""
    return subprocess.Popen(['python3', script_name])

def run_script_and_wait(script_name):
    """Ejecuta un script de Python y espera a que termine"""
    subprocess.run(['python3', script_name])

def wait_for_api_response(url, max_attempts=10, wait_time=5):
    """Espera una respuesta exitosa de la API en la URL proporcionada"""
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        
        attempts += 1
        time.sleep(wait_time)

    return None

def main():
    # Paso 1: Iniciar el API server
    api_server = run_script('api_server.py')
    print("API server iniciado...")

    time.sleep(5)  # Darle unos segundos para que la API esté lista

    # Paso 2: Escanear redes WiFi
    print("Ejecutando escaneo de redes WiFi...")
    run_script_and_wait('wifi_scan.py')

    # Paso 3: Convertir los resultados del escaneo WiFi a JSON
    print("Convirtiendo redes WiFi a JSON...")
    run_script_and_wait('csv_to_json.py')

    # Paso 4: Esperar a que el usuario seleccione una red a través de la API
    print("Esperando selección de red del usuario...")
    selected_network = wait_for_api_response('http://127.0.0.1:5000/selected-network')

    if selected_network:
        print(f"Red seleccionada: {selected_network['essid']}")
    else:
        print("Error: No se seleccionó ninguna red.")
        api_server.terminate()
        return

    # Paso 5: Escanear dispositivos en la red seleccionada
    print("Escaneando dispositivos en la red seleccionada...")
    run_script_and_wait('device_scan.py')

    # Paso 6: Convertir los resultados del escaneo de dispositivos a JSON
    print("Convirtiendo dispositivos escaneados a JSON...")
    run_script_and_wait('csv_to_json.py')

    # Paso 7: Ejecutar MAC-IP matcher
    print("Ejecutando MAC-IP matcher...")
    run_script_and_wait('mac_ip_matcher.py')

    # Paso 8: Ejecutar escaneo Nmap
    print("Ejecutando escaneo Nmap...")
    run_script_and_wait('nmap_scanner.py')

    # El servidor API sigue corriendo indefinidamente, puedes detenerlo manualmente si es necesario.
    print("Proceso completado. El servidor API sigue en ejecución.")
    api_server.wait()

if __name__ == "__main__":
    main()
