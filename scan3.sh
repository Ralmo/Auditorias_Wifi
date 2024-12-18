# Verificar si la interfaz wlan0 existe y está activa
if ! ip link show wlan0 > /dev/null 2>&1; then
    echo "Error: La interfaz wlan0 no existe o no está activa."
    exit 1
fi

# Verificar número de parámetros
if [ "$#" -ne 3 ]; then
    echo "Error: Número incorrecto de parámetros."
    echo "Uso correcto: ./script.sh <edificio> <piso> <tiempo_escaneo>"
    exit 1
fi

# Verificar que el tiempo de escaneo sea un número válido
if ! echo "$3" | grep -qE '^[0-9]+$'; then
    echo "Error: El parámetro de tiempo debe ser un número entero positivo."
    echo "Uso correcto: ./script.sh <edificio> <piso> <tiempo_escaneo>"
    exit 1
fi

OUTPUT_CSV="$(pwd)/${1}_${2}_networks.csv"

# Escaneo con airodump-ng
echo "Iniciando escaneo... Tiempo: $3 segundos."
sudo timeout "$3" airodump-ng wlan0 --output-format csv -w /tmp/wifi_scan

# Procesar resultados y guardar columnas relevantes
awk -F ',' 'NR>2 && NF>14 {print $1","$2","$3","$4","$5","$6","$7","$8","$9","$10","$11","$12","$13","$14}' /tmp/wifi_scan-01.csv > "$OUTPUT_CSV"

# Agregar encabezados al archivo CSV
echo "BSSID,First time seen,Last time seen,Channel,Speed,Privacy,Cipher,Authentication,Power,Beacons,IV,ID-Length,ESSID" | cat - "$OUTPUT_CSV" > temp && mv temp "$OUTPUT_CSV"

# Mensaje final
echo "Escaneo completado. Resultados guardados en: $OUTPUT_CSV"
