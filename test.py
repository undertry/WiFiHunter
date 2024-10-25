from monitor_mode import enable_monitor_mode, disable_monitor_mode

def main():
    interface = 'wlan0'

    try:
        enable_monitor_mode(interface)  # Poner wlan0 en modo monitor
    except Exception as e:
        print(f"Ocurrió un error al habilitar el modo monitor: {e}")
        return

    input("Presiona Enter para restaurar el modo gestionado...")

    try:
        disable_monitor_mode(interface)  # Restaurar wlan0 a modo gestionado
    except Exception as e:
        print(f"Ocurrió un error al deshabilitar el modo monitor: {e}")

if __name__ == "__main__":
    main()
