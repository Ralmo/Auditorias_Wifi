# Verificar parámetros
if [ "$#" -ne 3 ]; then echo "Uso: $0 <edificio> <piso> <duracion>"; exit 1; fi

# Parámetros
EDIFICIO=$1 PISO=$2 DURACION=$3 FECHA=$(date "+%Y-%m-%d_%H-%M-%S")
ARCHIVO="wifi_audit_${EDIFICIO}_${PISO}_${FECHA}.csv"

# Cabecera del CSV
echo "BSSID,First time seen,Last time seen,Channel,Speed,Privacy,Cipher,Authentication,Power,Beacons,IV,ID-Length,ESSID" > $ARCHIVO

# Escaneo
INTERFAZ=$(iw dev | grep Interface | awk '{print $2}')
sudo airodump-ng --output-format csv --write /tmp/wifi_scan --band abg $INTERFAZ & 
sleep $DURACION
sudo pkill -2 airodump-ng

# Guardar resultados
if [ -f "/tmp/wifi_scan-01.csv" ]; then
    tail -n +3 /tmp/wifi_scan-01.csv | awk -F, '{
        # Aseguramos que cada campo esté bien extraído
        print $1","$2","$3","$4","$5","$6","$7","$8","$9","$10","$11","$12","$13","$14
    }' >> $ARCHIVO
    rm /tmp/wifi_scan-01.csv
    echo "Escaneo completado. Resultados en: $ARCHIVO"
else
    echo "Error: No se encontró el archivo de escaneo."
fi
