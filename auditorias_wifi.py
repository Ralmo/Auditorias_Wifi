import csv
import subprocess
from datetime import datetime
import time

def listar_interfaces():
    """Lista las interfaces Wi-Fi disponibles y devuelve una lista de sus nombres."""
    try:
        print("[+] Listando interfaces Wi-Fi disponibles...")  # Muestra mensaje indicando que se están listando las interfaces.
        result = subprocess.check_output(["airmon-ng"], text=True).strip().split("\n")  # Ejecuta airmon-ng para listar interfaces y obtiene la salida.
        interfaces = []  # Lista donde se almacenarán las interfaces Wi-Fi disponibles.
        for line in result:  # Itera por cada línea de la salida de airmon-ng.
            if line.startswith("phy"):  # Verifica si la línea comienza con "phy", que es el prefijo de las interfaces Wi-Fi.
                parts = line.split()  # Divide la línea en partes.
                if len(parts) >= 2:
                    interfaces.append(parts[1])  # Agrega el nombre de la interfaz (segunda columna) a la lista.
        return interfaces  # Devuelve la lista de interfaces disponibles.
    except Exception as e:
        print(f"[-] Error al listar interfaces: {e}")  # En caso de error, muestra un mensaje de error.
        return []  # Retorna una lista vacía si ocurre un error.

def enable_monitor_mode(interface):
    """Habilita el modo monitor en la interfaz seleccionada."""
    try:
        print(f"[+] Habilitando modo monitor en {interface}...")  # Muestra mensaje indicando que se habilitará el modo monitor.
        subprocess.run(["airmon-ng", "start", interface], check=True)  # Ejecuta airmon-ng para habilitar el modo monitor.
        return f"{interface}mon"  # Devuelve el nombre de la interfaz con "mon" agregado al final (indicando que está en modo monitor).
    except subprocess.CalledProcessError:
        print("[-] Error al habilitar modo monitor.")  # Muestra mensaje de error si falla la habilitación.
        return None  # Devuelve None si ocurre un error.

def disable_monitor_mode(interface):
    """Deshabilita el modo monitor en la interfaz."""
    try:
        print(f"[+] Deshabilitando modo monitor en {interface}...")  # Muestra mensaje indicando que se deshabilitará el modo monitor.
        subprocess.run(["airmon-ng", "stop", interface], check=True)  # Ejecuta airmon-ng para deshabilitar el modo monitor.
    except subprocess.CalledProcessError:
        print("[-] Error al deshabilitar modo monitor.")  # Muestra mensaje de error si falla la deshabilitación.

def scan_wifi(interface):
    """Escanea redes Wi-Fi y guarda los datos en un archivo CSV hasta que el usuario decida detenerlo."""
    output_file = f"scan-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"  # Crea un nombre de archivo único para el escaneo usando la fecha y hora actual.
    try:
        print("[+] Iniciando escaneo Wi-Fi...")  # Muestra mensaje indicando que se inicia el escaneo.
        process = subprocess.Popen(  # Ejecuta el escaneo en segundo plano usando airodump-ng.
            ["airodump-ng", "--output-format", "csv", "--write", output_file, interface],
            stdout=subprocess.DEVNULL,  # Redirige la salida estándar a DEVNULL (sin mostrar en consola).
            stderr=subprocess.DEVNULL  # Redirige los errores a DEVNULL (sin mostrar en consola).
        )
        
        print("[+] Escaneo en curso. Presiona 'Enter' para detener el escaneo.")  # Informa al usuario que puede detener el escaneo presionando Enter.
        
        # Espera hasta que el usuario presione Enter para detener el escaneo
        input("Presiona 'Enter' para detener el escaneo...")  # El programa se pausa hasta que el usuario presiona Enter.
        process.terminate()  # Termina el proceso de escaneo cuando el usuario presiona Enter.
        
        print(f"[+] Escaneo detenido. Resultados guardados temporalmente en: {output_file}")  # Informa que el escaneo se detuvo y los resultados se guardaron.
        
    except Exception as e:
        print(f"[-] Error inesperado: {e}")  # Muestra un mensaje de error si ocurre un problema inesperado.
    return output_file  # Devuelve el nombre del archivo donde se guardaron los resultados del escaneo.

def parse_csv(input_csv, output_csv):
    """Procesa el archivo CSV de airodump-ng y guarda los datos relevantes en un nuevo archivo CSV."""
    try:
        print("[+] Procesando datos capturados...")  # Muestra mensaje indicando que se están procesando los datos capturados.
        with open(input_csv, "r") as infile:  # Abre el archivo CSV generado por airodump-ng.
            reader = csv.reader(infile)  # Crea un lector CSV para iterar sobre las filas del archivo.
            networks = []  # Lista para almacenar las redes Wi-Fi procesadas.
            in_network_section = False  # Variable para controlar cuando se está en la sección de redes.
            for row in reader:  # Itera sobre cada fila del archivo CSV.
                if len(row) == 0:  # Si la fila está vacía, la ignora.
                    continue
                if row[0] == "BSSID":  # Si encuentra la cabecera "BSSID", indica que empieza la sección de redes.
                    in_network_section = True
                    continue
                if in_network_section and row[0] == "":  # Si encuentra una línea vacía después de los datos de las redes, termina la sección.
                    break
                if in_network_section:  # Si está en la sección de redes, procesa la información.
                    bssid = row[0].strip()  # Obtiene el BSSID de la red.
                    ssid = row[13].strip() if len(row) > 13 else "Desconocido"  # Obtiene el SSID de la red, o "Desconocido" si no está presente.
                    auth = row[5].strip() if len(row) > 5 else "Desconocido"  # Obtiene el tipo de autenticación, o "Desconocido" si no está presente.
                    networks.append({"BSSID": bssid, "SSID": ssid, "Autenticación": auth})  # Agrega los datos de la red a la lista.
        
        with open(output_csv, "w", newline="") as outfile:  # Abre un nuevo archivo CSV para guardar los datos procesados.
            writer = csv.DictWriter(outfile, fieldnames=["BSSID", "SSID", "Autenticación"])  # Crea un escritor CSV.
            writer.writeheader()  # Escribe la cabecera en el archivo.
            writer.writerows(networks)  # Escribe las redes Wi-Fi procesadas en el archivo.
        print(f"[+] Datos procesados y guardados en: {output_csv}")  # Informa que los datos se han guardado correctamente.
    except Exception as e:
        print(f"[-] Error al procesar datos: {e}")  # Muestra mensaje de error si ocurre un problema al procesar los datos.

def main():
    interfaces = listar_interfaces()  # Llama a la función para listar las interfaces Wi-Fi disponibles.
    if not interfaces:  # Si no se encuentran interfaces disponibles, muestra un mensaje y termina el programa.
        print("[-] No se encontraron interfaces Wi-Fi disponibles.")
        return

    print("\n[+] Interfaces Wi-Fi disponibles:")  # Muestra las interfaces Wi-Fi disponibles.
    for i, iface in enumerate(interfaces):  # Muestra las interfaces con un índice numerado.
        print(f"  [{i}] {iface}")
    
    try:
        choice = int(input("\nSelecciona el número de la interfaz que deseas usar: "))  # Solicita al usuario seleccionar una interfaz.
        if choice < 0 or choice >= len(interfaces):  # Verifica que la opción seleccionada sea válida.
            print("[-] Opción inválida.")
            return
        selected_interface = interfaces[choice]  # Asigna la interfaz seleccionada.
    except ValueError:  # Si el usuario ingresa algo que no es un número
