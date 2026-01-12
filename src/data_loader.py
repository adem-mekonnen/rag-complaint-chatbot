# src/data_loader.py
import pandas as pd
import re
import os

def load_raw_data(filepath):
    """
    Loads the raw CSV dataset with robust error handling.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}. Please check the path.")
    
    print(f"Loading data from {filepath}...")
    
    try:
        # Use on_bad_lines='skip' to handle malformed rows if any exist
        return pd.read_csv(filepath, low_memory=False, on_bad_lines='skip')
    except Exception as e:
        print(f"Standard load failed: {e}")
        print("Attempting robust load with python engine...")
        # Fallback to python engine which is slower but more robust
        return pd.read_csv(filepath, low_memory=False, engine='python', on_bad_lines='skip')

def preprocess_complaints(df):
    """
    Filters and cleans the complaint data.
    1. Filters for 5 specific product categories.
    2. Removes rows with missing narratives.
    3. Cleans text (lowercase, remove PII placeholders).
    """
    print("Starting preprocessing...")
    
    # 1. Define Target Products & Mapping
    product_map = {
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
    
    # Filter dataset based on whether the 'Product' column matches our target keys
    df_filtered = df[df['Product'].isin(product_map.keys())].copy()
    
    # Create a clean 'product_category' column
    df_filtered['product_category'] = df_filtered['Product'].map(product_map)
    
    # 2. Remove records with empty narratives
    initial_count = len(df_filtered)
    df_filtered = df_filtered.dropna(subset=['Consumer complaint narrative'])
    print(f"Dropped {initial_count - len(df_filtered)} rows with missing narratives.")

    # 3. Text Cleaning Function
    def clean_narrative(text):
        if not isinstance(text, str): return ""
        text = text.lower()
        
        # Remove "XX" anonymization placeholders
        text = re.sub(r'x{2,}', '', text) 
        
        # Remove standard boilerplate text
        text = text.replace("i am writing to file a complaint", "")
        
        # Remove newlines and weird spacing
        text = re.sub(r'\n', ' ', text)
        
        # Keep basic punctuation
        text = re.sub(r'[^\w\s\.]', '', text) 
        
        return text.strip()

    # Apply cleaning
    df_filtered['cleaned_narrative'] = df_filtered['Consumer complaint narrative'].apply(clean_narrative)
    
    # 4. Filter out very short complaints
    df_filtered['word_count'] = df_filtered['cleaned_narrative'].apply(lambda x: len(str(x).split()))
    df_filtered = df_filtered[df_filtered['word_count'] >= 5]
    
    print(f"Preprocessing complete. Final shape: {df_filtered.shape}")
    return df_filtered

if __name__ == "__main__":
    # Test script execution
    # This block allows running the script directly: python src/data_loader.py
    
    # Determine the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Construct absolute paths
    raw_path = os.path.join(project_root, "data", "raw", "complaints.csv")
    processed_path = os.path.join(project_root, "data", "processed", "filtered_complaints.csv")
    
    print(f"Project Root: {project_root}")
    print(f"Looking for data at: {raw_path}")
    
    try:
        # Load and process
        df = load_raw_data(raw_path)
        clean_df = preprocess_complaints(df)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        
        # Save results
        clean_df.to_csv(processed_path, index=False)
        print(f"Success! Processed data saved to {processed_path}")
        
    except Exception as e:
        print(f"Error during execution: {e}")