OUTPUT_CSV="$(pwd)/${1}_${2}_networks.csv"

# Escaneo con airodump-ng
sudo timeout "$3" airodump-ng wlan0 --output-format csv -w /tmp/wifi_scan

# Procesar resultados y guardar columnas relevantes
awk -F ',' 'NR>2 && NF>14 {print $1","$2","$4","$6","$7","$8","$14}' /tmp/wifi_scan-01.csv > "$OUTPUT_CSV"

# Agregar encabezados al archivo CSV
sed -i '1iBSSID,PWR,CH,ENC,CIPHER,AUTH,SSID' "$OUTPUT_CSV"

# Mensaje final
echo "Escaneo completado. Resultados guardados en: $OUTPUT_CSV"
