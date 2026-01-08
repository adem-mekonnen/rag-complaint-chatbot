import pyarrow.parquet as pq

file_path = "data/raw/complaint_embeddings-001.parquet"

try:
    parquet_file = pq.ParquetFile(file_path)
    print("✅ Columns found in file:")
    print(parquet_file.schema.names)
except Exception as e:
    print(f"Error: {e}")