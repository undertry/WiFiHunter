import subprocess

def stop_network_services():
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', 'NetworkManager'], check=True)
        subprocess.run(['sudo', 'killall', 'wpa_supplicant'], check=True)
        print(f"NetworkManager y wpa_supplicant stopped.")

        subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], check=True)
        print("Interfering processes (such as dhclient) stopped.")
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error when stopping processes: {e}")

def enable_monitor_mode(interface):
    try:
        stop_network_services()  
        print(f"Enabling monitor mode in {interface}...")

        subprocess.run(['sudo', 'airmon-ng', 'start', interface], check=True)
        print(f"{interface} is now in monitor mode (wlan0mon)")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error when enabling monitor mode: {e}")

def disable_monitor_mode(interface):
    try:
        print(f"Restoring {interface} to managed mode...")

        subprocess.run(['sudo', 'airmon-ng', 'stop', f'{interface}mon'], check=True)

        subprocess.run(['sudo', 'systemctl', 'start', 'NetworkManager'], check=True)
        print(f"{interface} is now in managed mode and NetworkManager is restarted.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error when disabling monitor mode: {e}")
