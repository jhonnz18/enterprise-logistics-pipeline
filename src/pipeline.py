import concurrent.futures
import polars as pl
import json
import logging
import sys
import datetime
from typing import List, Dict, Any

# ==============================================================================
# CONFIGURACIÓN DEL LOGGING ESTRUCTURADO EN JSON
# ==============================================================================
class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "component": "LogisticsDataPipeline",
            "module": record.module
        }
        if hasattr(record, "extra_data"):
            log_payload["metadata"] = record.extra_data
        return json.dumps(log_payload)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JSONFormatter())

logger = logging.getLogger("EnterprisePipeline")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# ==============================================================================
# CORE DEL PIPELINE CON REGLAS DE DATA QUALITY
# ==============================================================================
class LogisticsDataPipeline:
    def __init__(self, truck_ids: List[str]):
        self.truck_ids: List[str] = truck_ids
        self.raw_telemetry: List[Dict[str, Any]] = []

    def fetch_truck_telemetry(self, truck_id: str) -> List[Dict[str, Any]]:
        """Simula extracción concurrente inyectando intencionalmente algunos datos corruptos para probar QA."""
        logger.info(f"Initiating telemetric extraction stream", extra={"extra_data": {"truck_id": truck_id}})
        
        # Simulación de transmisión normal para la flota
        stream_data = [
            {"truck_id": truck_id, "route_id": f"R-10{truck_id[:3]}_1", "duration_hours": 4.0, "delivery_stops": 2, "status": "ONLINE"}
        ]
        
        # Inyectamos datos corruptos controlados para demostrar que las reglas de gobierno funcionan
        if truck_id == "TRUCK_01":
            # Caso 1: Registro duplicado idéntico de red
            stream_data.append({"truck_id": truck_id, "route_id": f"R-10{truck_id[:3]}_1", "duration_hours": 4.0, "delivery_stops": 2, "status": "ONLINE"})
        elif truck_id == "TRUCK_02":
            # Caso 2: Registro con anomalía matemática (duración negativa por fallo de sensor)
            stream_data.append({"truck_id": truck_id, "route_id": "R-ERROR_2", "duration_hours": -5.5, "delivery_stops": 1, "status": "MALFUNCTION"})
        elif truck_id == "TRUCK_03":
            # Caso 3: Registro huérfano (ID de camión vacío)
            stream_data.append({"truck_id": " ", "route_id": "R-ORPHAN_3", "duration_hours": 2.0, "delivery_stops": 3, "status": "UNKNOWN"})
            
        return stream_data

    def execute_concurrent_extraction(self) -> None:
        logger.info("Spawning concurrent thread pool workers for fleet ingestion", extra={"extra_data": {"fleet_size": len(self.truck_ids)}})
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.fetch_truck_telemetry, t_id): t_id for t_id in self.truck_ids}
            for future in concurrent.futures.as_completed(futures):
                truck_id = futures[future]
                try:
                    self.raw_telemetry.extend(future.result())
                except Exception as exc:
                    logger.error(f"Execution failure during dynamic extraction", extra={"extra_data": {"truck_id": truck_id, "error": str(exc)}})

    def transform_and_save(self, output_path: str) -> None:
        if not self.raw_telemetry:
            logger.warning("Pipeline execution halted: Raw data stream is empty")
            return
            
        logger.info("Invoking Polars engine for memory-mapped structural transformations")
        df_raw = pl.DataFrame(self.raw_telemetry)
        initial_rows = df_raw.height

        # ----------------------------------------------------------------------
        # CAPA DE GOBIERNO DE DATOS (DATA QUALITY & CLEANSING)
        # ----------------------------------------------------------------------
        # Regla 1: Limpieza de IDs vacíos o nulos
        df_clean = df_raw.filter(
            pl.col("truck_id").is_not_null() & (pl.col("truck_id").str.strip_chars() != "")
        )
        
        # Regla 2: Filtro de sanidad operacional (Duraciones lógicas mayores a 0)
        df_clean = df_clean.filter(
            (pl.col("duration_hours") > 0.0) & (pl.col("delivery_stops") >= 0)
        )
        
        # Regla 3: Deduplicación estricta por llaves de negocio operacionales
        df_clean = df_clean.unique(subset=["truck_id", "route_id"], keep="first")
        
        final_rows = df_clean.height
        purged_records = initial_rows - final_rows
        
        logger.info(
            "Data Quality processing complete", 
            extra={"extra_data": {"initial_records": initial_rows, "clean_records": final_rows, "purged_records": purged_records}}
        )

        # Persistencia final en formato Parquet comprimido
        df_clean.write_parquet(output_path, compression="snappy")
        logger.info("Analytical targets successfully committed to production storage Layer", extra={"extra_data": {"target_path": output_path}})

if __name__ == "__main__":
    FLEET = ["TRUCK_01", "TRUCK_02", "TRUCK_03", "TRUCK_04"]
    pipeline = LogisticsDataPipeline(FLEET)
    pipeline.execute_concurrent_extraction()
    pipeline.transform_and_save("data/truck_metrics.parquet")