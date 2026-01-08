# src/data_loader.py
import pandas as pd
import re
import os

# Define the products we care about
TARGET_PRODUCTS = {
    "Credit card": "Credit Card",
    "Credit card or prepaid card": "Credit Card",
    "Prepaid card": "Credit Card",
    "Payday loan, title loan, or personal loan": "Personal Loan",
    "Consumer Loan": "Personal Loan",
    "Payday loan": "Personal Loan",
    "Checking or savings account": "Savings Account",
    "Bank account or service": "Savings Account",
    "Money transfer, virtual currency, or money service": "Money Transfer",
    "Money transfers": "Money Transfer"
}

def get_raw_stats(filepath):
    """
    Reads only the 'Product' and 'Consumer complaint narrative' columns 
    in chunks to generate statistics without crashing RAM.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")

    print(f"Scanning raw data at {filepath} for statistics...")
    
    product_counts = pd.Series(dtype=int)
    total_rows = 0
    missing_narratives = 0
    
    # We only read these two columns to save memory
    usecols = ['Product', 'Consumer complaint narrative']
    
    # Process in chunks of 100,000 rows
    chunksize = 100000
    
    try:
        for chunk in pd.read_csv(filepath, usecols=usecols, chunksize=chunksize, low_memory=False, on_bad_lines='skip'):
            # Count products
            counts = chunk['Product'].value_counts()
            product_counts = product_counts.add(counts, fill_value=0)
            
            # Count missing narratives
            missing_narratives += chunk['Consumer complaint narrative'].isnull().sum()
            total_rows += len(chunk)
            
            print(f"Processed {total_rows} rows...", end='\r')
            
    except Exception as e:
        print(f"\nError reading stats: {e}")
        return None, None, None

    print(f"\nScan complete. Total rows: {total_rows}")
    return product_counts.sort_values(ascending=False), total_rows, missing_narratives

def clean_narrative(text):
    """Helper to clean text string."""
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'x{2,}', '', text) # Remove anonymization
    text = text.replace("i am writing to file a complaint", "")
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^\w\s\.]', '', text) 
    return text.strip()

def load_and_process_in_chunks(filepath):
    """
    Loads the dataset in chunks, filters for target products, 
    removes missing narratives, and cleans text ON THE FLY.
    This prevents Out of Memory errors.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
    
    print("Starting chunked processing (Filter -> Clean -> Accumulate)...")
    
    processed_chunks = []
    chunksize = 50000  # Smaller chunk size for heavier processing
    total_processed = 0
    
    # Define columns to load (skip irrelevant ones to save RAM)
    # Note: CFPB column names can vary slightly, but these are standard
    usecols = ['Complaint ID', 'Product', 'Issue', 'Company', 'Consumer complaint narrative']
    
    try:
        reader = pd.read_csv(filepath, usecols=usecols, chunksize=chunksize, low_memory=False, on_bad_lines='skip')
        
        for i, chunk in enumerate(reader):
            # 1. Drop rows with missing narratives immediately
            chunk = chunk.dropna(subset=['Consumer complaint narrative'])
            
            if chunk.empty:
                continue
                
            # 2. Filter for target products immediately
            chunk = chunk[chunk['Product'].isin(TARGET_PRODUCTS.keys())].copy()
            
            if chunk.empty:
                continue

            # 3. Map categories
            chunk['product_category'] = chunk['Product'].map(TARGET_PRODUCTS)
            
            # 4. Clean text
            chunk['cleaned_narrative'] = chunk['Consumer complaint narrative'].apply(clean_narrative)
            
            # 5. Filter short text
            chunk['word_count'] = chunk['cleaned_narrative'].apply(lambda x: len(str(x).split()))
            chunk = chunk[chunk['word_count'] >= 5]
            
            # Store processed chunk
            processed_chunks.append(chunk)
            
            total_processed += len(chunk)
            print(f"Processed chunk {i+1}. Collected {total_processed} valid rows so far...", end='\r')
            
        print("\nCombining chunks...")
        if not processed_chunks:
            raise ValueError("No data found after filtering! Check your CSV or product names.")
            
        final_df = pd.concat(processed_chunks, ignore_index=True)
        print(f"Done! Final dataset shape: {final_df.shape}")
        return final_df
        
    except Exception as e:
        print(f"\nError in processing: {e}")
        # If specific columns fail, try loading everything (risky but fallback)
        print("Tip: Check if 'Complaint ID' or 'Product' columns exist in your CSV.")
        raise e

if __name__ == "__main__":
    # Test execution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    raw_path = os.path.join(project_root, "data", "raw", "complaints.csv")
    processed_path = os.path.join(project_root, "data", "processed", "filtered_complaints.csv")
    
    # Run stats
    get_raw_stats(raw_path)
    
    # Run processing
    df = load_and_process_in_chunks(raw_path)
    
    # Save
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"Saved to {processed_path}")