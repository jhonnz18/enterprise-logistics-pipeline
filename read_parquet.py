import polars as pl

# Leer el archivo Parquet generado por el contenedor
df = pl.read_parquet("data/truck_metrics.parquet")

print("📊 ESTRUCTURA DEL DATAFRAME (ESQUEMA):")
print(df.schema)

print("\n🚚 REGISTROS PROCESADOS:")
print(df)