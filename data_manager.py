import pandas as pd
import streamlit as st
import re

DATA_PATH = "parts_data.csv"

def clean_numeric_value(val):
    """
    Extracts the first floating point or integer number from a string.
    Returns None if no number found.
    """
    if pd.isna(val) or val == "":
        return None
    val_str = str(val).strip()
    if val_str == "":
        return None
        
    # Regex to find numbers, handling decimals
    match = re.search(r"(\d+(\.\d+)?)", val_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

@st.cache_data
def load_data():
    """
    Loads parts data from CSV and cleans numeric columns.
    """
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        st.error(f"Cannot find {DATA_PATH}. Please ensure the file exists.")
        return pd.DataFrame()

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
