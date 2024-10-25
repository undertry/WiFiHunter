import subprocess

# Función para detener procesos que puedan estar interfiriendo con wlan0
def stop_network_services():
    try:
        # Detener NetworkManager
        subprocess.run(['sudo', 'systemctl', 'stop', 'NetworkManager'], check=True)
        # Detener wpa_supplicant
        subprocess.run(['sudo', 'killall', 'wpa_supplicant'], check=True)
        print(f"NetworkManager y wpa_supplicant detenidos.")

        # Matar procesos que interfieran (como dhclient)
        subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], check=True)
        print("Procesos que interfieren (como dhclient) detenidos.")
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al detener procesos: {e}")

# Función para habilitar el modo monitor en la interfaz de red
def enable_monitor_mode(interface):
    try:
        stop_network_services()  # Detener servicios que usen la interfaz
        print(f"Habilitando modo monitor en {interface}...")

        # Usar airmon-ng para poner wlan0 en modo monitor (crea wlan0mon)
        subprocess.run(['sudo', 'airmon-ng', 'start', interface], check=True)
        print(f"{interface} está ahora en modo monitor (wlan0mon).")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al habilitar modo monitor: {e}")

# Función para deshabilitar el modo monitor (restaurar a modo gestionado)
def disable_monitor_mode(interface):
    try:
        print(f"Restaurando {interface} a modo gestionado...")

        # Usar airmon-ng para detener el modo monitor (elimina wlan0mon)
        subprocess.run(['sudo', 'airmon-ng', 'stop', f'{interface}mon'], check=True)

        # Reiniciar NetworkManager después de terminar
        subprocess.run(['sudo', 'systemctl', 'start', 'NetworkManager'], check=True)
        print(f"{interface} está ahora en modo gestionado y NetworkManager reiniciado.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al deshabilitar modo monitor: {e}")
