import pandas as pd
import streamlit as st
import re

DATA_PATH = "parts_data.csv"

def clean_numeric_value(val):
    """
    Extracts number(s) from a string.
    If multiple numbers are separated by '/', returns a list of floats.
    Otherwise returns a single float or None.
    """
    if pd.isna(val) or val == "":
        return None
    val_str = str(val).strip()
    if val_str == "":
        return None
        
    # Check for Slash Separator
    if '/' in val_str:
        # Filter out empty strings to handle '93/' or '/93' typos as single values if applicable
        # However, we must be careful about preserving position if intention is dual.
        # But for 'Single Mold', a trailing slash is a common typo.
        # Hybrid Approach: Split, but if adjacent parts are empty, be smart?
        # Simpler: Split. If we have exactly 1 non-empty and the rest are empty, treat as scalar.
        
        parts = val_str.split('/')
        
        # Parse all
        results = []
        for p in parts:
            match = re.search(r"(\d+(\.\d+)?)", p)
            if match:
                try: results.append(float(match.group(1)))
                except: results.append(None)
            else:
                results.append(None)
        
        # If result is like [93.0, None], check if original string was just '93/' (Trailing slash typo)
        # or if it was '93/ ' 
        # Heuristic: If we have multiple Nones, it's messy.
        
        # New Logic: Filter valid numbers. 
        valid_nums = [x for x in results if x is not None]
        
        # If only 1 valid number exists, AND the user didn't explicitly use a placeholder like '0' or '-'?
        # Regex search meant we only found digits.
        # If val_str was "93/", results=[93.0, None]. valid=[93.0].
        # If we return scalar 93.0, we fix duplicate issue.
        # If val_str was "/95", results=[None, 95.0]. valid=[95.0]. Returns 95.0 Scalar.
        # Does anyone intentionally write "/95" for Dual Mode (Left only)?
        # Context: User said "Single Mold".
        
        if len(valid_nums) == 1:
            return valid_nums[0]
            
        # If 0 valid nums, return None
        if not valid_nums:
            return None
            
        # If > 1 valid nums (e.g. 93/95), return list
        return results

    # Standard Single Value Case
    match = re.search(r"(\d+(\.\d+)?)", val_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

@st.cache_data(ttl=60)
def load_data():
    """
    Loads parts data from CSV and cleans numeric columns.
    """
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        st.error(f"Cannot find {DATA_PATH}. Please ensure the file exists.")
        return pd.DataFrame()

    # Rename columns to match internal logic (User changed CSV headers)
    rename_map = {
        '標準重量(g)': '重量',
        '重量上限(g)': '重量上限',
        '重量下限(g)': '重量下限',
        '標準長度(mm)': '標準長度',
        '長度上限(mm)': '長度上限',
        '長度下限(mm)': '長度下限',
        '異常履歷寫真1': '異常履歷寫真' # Map first defect image to legacy col
    }
    df.rename(columns=rename_map, inplace=True)

    # Ensure required columns exist
    if '原料編號' not in df.columns:
        df['原料編號'] = '' # Default empty if missing
    
    # Columns that need cleaning
    numeric_cols = ['重量', '重量上限', '重量下限', '標準長度', '長度上限', '長度下限']
    
    # We want to keep original display strings but also have clean numeric values for logic
    # Let's create new internal columns for calculation
    for col in numeric_cols:
        if col in df.columns:
            df[f'clean_{col}'] = df[col].apply(clean_numeric_value)
            
    # Fill NaN in clean columns with 0 or proper default if needed, 
    # but for length, 0 or None means "Hidden", so None is good.
    
    return df

def get_filtered_data(df, car_model=None, part_number=None):
    """
    Filters dataframe based on selection.
    """
    filtered = df.copy()
    if car_model:
        filtered = filtered[filtered['車型'] == car_model]
    if part_number:
        filtered = filtered[filtered['品番'] == part_number]
    return filtered
