import os
import json
import requests
from datetime import date
from dotenv import load_dotenv

# Carga explícitamente el archivo .env
load_dotenv()

API_KEY = os.getenv("AEMET_API_KEY")
URL_ORIGEN = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/2006/aniofin/2006/estacion/8416/"

def obtener_datos_aemet() -> list[dict]:
    """Realiza el flujo de dos pasos de AEMET correctamente."""
    params = {
        "api_key": API_KEY
    }

    print("1. Solicitando enlace temporal a AEMET...")
    resp_inicial = requests.get(URL_ORIGEN, params=params, timeout=30)

    print(f"Código HTTP recibido: {resp_inicial.status_code}")
    print(f"Texto recibido de la API: {repr(resp_inicial.text[:300])}")

    if resp_inicial.status_code != 200:
        print(f"Error HTTP: {resp_inicial.status_code} - {resp_inicial.text}")
        return []

    try:
        resultado_inicial = resp_inicial.json()
    except json.JSONDecodeError:
        print("❌ Error: La respuesta de AEMET no es un JSON válido (viene vacía o en HTML).")
        return []

    if resultado_inicial.get("estado") != 200:
        print(f"Error en la API de AEMET: {resultado_inicial.get('descripcion')}")
        return []

    url_temporal = resultado_inicial.get("datos")

    if not url_temporal:
        print("No se ha podido obtener la URL de descarga temporal.")
        return []

    print("2. Descargando los datos reales desde la URL temporal...")
    resp_datos = requests.get(url_temporal, timeout=30)
    resp_datos.raise_for_status()

    registros = resp_datos.json()

    if isinstance(registros, list):
        return registros

    return []

if __name__ == "__main__":
    registros = obtener_datos_aemet()

    if registros:
        fecha = date.today().isoformat()
        ruta_salida = f"data/raw/dataset_{fecha}.json"

        os.makedirs("data/raw", exist_ok=True)

        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)

        print(f"Ingesta completada: {len(registros)} registros guardados en {ruta_salida}")
    else:
        print("La API no devolvió ningún registro.")