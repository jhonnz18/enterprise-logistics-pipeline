import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import polars as pl

# Configure Structured Enterprise Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("LogisticsDataPipeline")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())}.000Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "component": "LogisticsDataPipeline",
            "module": "pipeline"
        }
        if hasattr(record, "metadata"):
            log_object["metadata"] = record.metadata
        return json.dumps(log_object)

for handler in logger.handlers:
    handler.setFormatter(JSONFormatter())
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(JSONFormatter())
    logger.addHandler(ch)

def extract_telemetry_stream(truck_id: str) -> dict:
    """
    Simulates concurrent, high-density telemetry ingestion streams from fleet hardware.
    Includes controlled structural anomalies to test upstream Data Governance enforcement.
    """
    extra_records = {
        "TRUCK_01": [
            {"truck_id": "TRUCK_01", "route_id": "R-10TRU_1", "duration_hours": 4.0, "delivery_stops": 4, "status": "ONLINE", "coordinates": "4.6282, -74.1542"},
            {"truck_id": "TRUCK_01", "route_id": "R-10TRU_1", "duration_hours": 4.0, "delivery_stops": 4, "status": "ONLINE", "coordinates": "4.6282, -74.1542"} # Network Duplicate
        ],
        "TRUCK_02": [
            {"truck_id": "TRUCK_02", "route_id": "R-10TRU_2", "duration_hours": 4.0, "delivery_stops": 4, "status": "ONLINE", "coordinates": "4.6748, -74.0543"}
        ],
        "TRUCK_03": [
            {"truck_id": "TRUCK_03", "route_id": "R-10TRU_3", "duration_hours": -5.5, "delivery_stops": 2, "status": "ONLINE", "coordinates": "4.6104, -74.1375"}, # Sensor Metric Anomaly (Negative)
            {"truck_id": "TRUCK_03", "route_id": "R-10TRU_3", "duration_hours": 4.0, "delivery_stops": 4, "status": "ONLINE", "coordinates": "4.6104, -74.1375"}
        ],
        "TRUCK_04": [
            {"truck_id": None, "route_id": "R-ERROR_4", "duration_hours": 1.2, "delivery_stops": 1, "status": "DOWN", "coordinates": "4.6912, -74.0321"}, # Structural Orphan Payload (No ID)
            {"truck_id": "TRUCK_04", "route_id": "R-10TRU_4", "duration_hours": 4.0, "delivery_stops": 4, "status": "ONLINE", "coordinates": "4.6912, -74.0321"}
        ]
    }
    
    logger.info(f"Initiating telemetric extraction stream", extra={"metadata": {"truck_id": truck_id}})
    time.sleep(0.05)
    return extra_records.get(truck_id, [])

def run_governed_pipeline():
    """
    Main orchestration engine execution. Parallelizes stream ingestion, executes
    vectorized multi-rule data cleansing using Polars, and commits production targets.
    """
    fleet = ["TRUCK_01", "TRUCK_02", "TRUCK_03", "TRUCK_04"]
    logger.info("Spawning concurrent thread pool workers for fleet ingestion", extra={"metadata": {"fleet_size": len(fleet)}})
    
    raw_payloads = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(extract_telemetry_stream, fleet)
        for batch in results:
            raw_payloads.extend(batch)
            
    logger.info("Invoking Polars engine for memory-mapped structural transformations")
    
    # Ingest into memory dataframe mapping native technical constraints
    df_raw = pl.DataFrame(raw_payloads, schema={
        "truck_id": pl.String,
        "route_id": pl.String,
        "duration_hours": pl.Float64,
        "delivery_stops": pl.Int64,
        "status": pl.String,
        "coordinates": pl.String
    })
    
    initial_count = df_raw.height
    
    # Dynamic Governance Cleansing Rules Evaluation
    df_clean = (
        df_raw
        .filter(pl.col("truck_id").is_not_null())  # Rule 1: Purge Orphan Payloads
        .filter(pl.col("duration_hours") > 0.0)    # Rule 2: Exclude Negative Anomalies
        .unique(subset=["truck_id", "route_id"])    # Rule 3: Enforce Network Deduplication
    )
    
    clean_count = df_clean.height
    purged_count = initial_count - clean_count
    
    # Persist optimized Parquet layer
    df_clean.write_parquet("data/truck_metrics.parquet", compression="snappy")
    
    logger.info("Data Quality processing complete", extra={"metadata": {
        "initial_records": initial_count,
        "clean_records": clean_count,
        "purged_records": purged_count
    }})
    logger.info("Analytical targets successfully committed to production storage Layer", extra={"metadata": {
        "target_path": "data/truck_metrics.parquet"
    }})

if __name__ == "__main__":
    run_governed_pipeline()
