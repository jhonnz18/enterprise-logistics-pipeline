    import time
import requests
import polyline
import random

# Base URL pública y gratuita de OSRM (OpenStreetMap)
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

def obtener_geometria_ruta(origen, destino):
    """
    Consume la API de OSRM para calcular el itinerario óptimo por calles.
    Devuelve una lista de tuplas (Latitud, Longitud) decodificadas.
    """
    # OSRM requiere el formato: longitud,latitud;longitud,latitud
    coordenadas_format = f"{origen[1]},{origen[0]};{destino[1]},{destino[0]}"
    url = f"{OSRM_BASE_URL}/{coordenadas_format}?overview=full&geometries=polyline"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("routes"):
                geometria_encriptada = data["routes"][0]["geometry"]
                # Decodifica la línea en coordenadas legibles por Python
                return polyline.decode(geometria_encriptada)
        print(f"⚠️ No se pudo obtener ruta de OSRM. Status code: {response.status_code}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red al conectar con OSRM: {e}")
        return []

def transmitir_telemetria(truck_id, lat, lon, stop_number, status):
    """
    PUNTO DE INTEGRACIÓN: Aquí es donde tu backend se conecta con tu pipeline.
    Sustituye este print por la función que escribe en tu Google Sheets o Parquet.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"📡 [{timestamp}] {truck_id} | Estado: {status} | Parada Actual: {stop_number}/4 | GPS: ({lat:.5f}, {lon:.5f})")
    
    # Ejemplo de payload listo para enviar a tu Google Sheets API existente:
    # payload = {"timestamp": timestamp, "truck_id": truck_id, "status": status, "lat": lat, "lon": lon, "stops": stop_number}
    # tu_modulo_sheets.insertar_fila(payload)

def ejecutar_itinerario_camion(truck_id, paradas_bogota):
    """
    Simula el ciclo completo del camión recorriendo secuencialmente sus 4 paradas asignadas.
    """
    print(f"\n🚚 [DESPACHO ASIGNADO] Iniciando operaciones para el {truck_id}...")
    paradas_completadas = 0
    
    # Recorremos los puntos definidos en el itinerario
    for i in range(len(paradas_bogota) - 1):
        origen = paradas_bogota[i]
        destino = paradas_bogota[i+1]
        
        # 1. Calcular trayecto por avenidas usando la API
        camino_calles = obtener_geometria_ruta(origen, destino)
        
        if not camino_calles:
            print(f"💥 Abortando tramo para {truck_id} por fallo en el motor de mapas.")
            continue
            
        # 2. El camión se empieza a mover hacia la siguiente parada (Estado: IN_TRANSIT)
        for punto in camino_calles:
            lat, lon = punto
            transmitir_telemetria(truck_id, lat, lon, paradas_completadas, "IN_TRANSIT")
            time.sleep(1) # Frecuencia de envío del sensor (1 segundo para testing rápido)
            
        # 3. El camión entra al radio geográfico del destino (Estado: ARRIVED)
        paradas_completadas += 1
        lat_final, lon_final = destino
        transmitir_telemetria(truck_id, lat_final, lon_final, paradas_completadas, "ARRIVED")
        
        print(f"📦 [HITO] {truck_id} llegó con éxito a la parada #{paradas_completadas}. Descargando mercancía...")
        time.sleep(3) # Simula el tiempo muerto de descarga en la bahía
        
    # 4. Al completar el itinerario completo de 4 paradas (Estado: COMPLETED)
    transmitir_telemetria(truck_id, lat_final, lon_final, paradas_completadas, "COMPLETED")
    print(f"🏁 [OPERACIÓN FINALIZADA] {truck_id} completó su itinerario de {paradas_completadas} paradas.")

# === ESCENARIO DE PRUEBA OPERATIVA (BOGOTÁ) ===
if __name__ == "__main__":
    # Definimos coordenadas reales de puntos de control logísticos clave en Bogotá (Lat, Lon)
    # Ejemplo: Ruta Multi-stop saliendo del Peaje Sur hacia Centrales de Abasto y Distribución Norte
    ITINERARIO_NORTESUR = [
        (4.5910, -74.1430),  # Origen: Zona de acopio Autopista Sur / Bosa
        (4.6155, -74.1530),  # Parada 1: Central de Abastos (Kennedy)
        (4.6420, -74.1240),  # Parada 2: Zona Industrial (Puente Aranda)
        (4.6760, -74.1380),  # Parada 3: Centros Logísticos (Fontibón)
        (4.7110, -74.1130)   # Parada 4/Destino Final: Portales de Carga (Engativá / Suba)
    ]
    
    # Ejecutamos la simulación para un vehículo de la flota
    ejecutar_itinerario_camion("TRUCK_01", ITINERARIO_NORTESUR)