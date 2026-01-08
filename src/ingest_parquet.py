import pandas as pd
import os
import pyarrow.parquet as pq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import gc

# Paths
PARQUET_PATH = "data/raw/complaint_embeddings-001.parquet"
VECTOR_STORE_DIR = "vector_store_full"

def get_text_column(columns):
    # Updated list to include 'document'
    candidates = ['document', 'text', 'narrative', 'consumer_complaint_narrative', 'complaint_text', 'body']
    for c in candidates:
        if c in columns:
            return c
    return None

def build_vector_store_from_parquet():
    print(f"Checking file at {PARQUET_PATH}...")
    
    if not os.path.exists(PARQUET_PATH):
        print(f"Error: File not found at {PARQUET_PATH}")
        return

    # 1. Inspect Schema
    try:
        pf = pq.ParquetFile(PARQUET_PATH)
        available_cols = pf.schema.names
        print(f"Columns found: {available_cols}")
        
        text_col = get_text_column(available_cols)
        if not text_col:
            print("❌ Error: Could not identify the text column. Please check column names.")
            return
        print(f"✅ Using '{text_col}' as the text column.")
        
        # We only load necessary columns to save RAM
        # We explicitly exclude 'embedding' if it exists to save memory
        # We include relevant metadata columns
        cols_to_read = [text_col, 'complaint_id', 'product', 'issue', 'company']
        # Filter to only keep columns that actually exist in the file
        cols_to_read = [c for c in cols_to_read if c in available_cols]
        
    except Exception as e:
        print(f"Error inspecting file: {e}")
        return

    # 2. Initialize Embeddings & Vector Store
    print("Initializing embedding model...")
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print(f"Initializing Vector Store at {VECTOR_STORE_DIR}...")
    
    # If directory exists, we append to it. Chroma handles persistence automatically.
    vector_db = Chroma(
        persist_directory=VECTOR_STORE_DIR,
        embedding_function=embedding_function,
        collection_name="complaints_rag_full"
    )

    # 3. Stream Processing
    # Process 5,000 rows in batches of 500 to keep memory low
    TOTAL_LIMIT = 5000 
    BATCH_SIZE = 500
    current_count = 0
    
    print(f"Streaming max {TOTAL_LIMIT} rows...")

    try:
        for batch in pf.iter_batches(batch_size=BATCH_SIZE, columns=cols_to_read):
            df_batch = batch.to_pandas()
            
            documents = []
            for _, row in df_batch.iterrows():
                # Get text content safely
                text = str(row.get(text_col, ''))
                if not text.strip() or text.lower() == 'nan':
                    continue

                # Build metadata safely
                metadata = {
                    "complaint_id": str(row.get('complaint_id', 'N/A')),
                    "product": str(row.get('product', 'Unknown')),
                    "issue": str(row.get('issue', 'Unknown')),
                    "company": str(row.get('company', 'Unknown'))
                }
                documents.append(Document(page_content=text, metadata=metadata))

            if documents:
                vector_db.add_documents(documents)
                current_count += len(documents)
                print(f"  Indexed {current_count} documents...", end="\r")

            # Memory cleanup
            del df_batch
            del documents
            gc.collect()

            if current_count >= TOTAL_LIMIT:
                break
        
        print(f"\n✅ Success! Indexed {current_count} documents.")

    except Exception as e:
        print(f"\n❌ Processing failed: {e}")

if __name__ == "__main__":
    build_vector_store_from_parquet()