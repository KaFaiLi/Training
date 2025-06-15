# File: comprehensive_reconciliation.py
import pandas as pd
import numpy as np
import os

def convert_japanese_date(date_str):
    """
    Converts a Japanese-style date string "YY-MM-DD" to a Gregorian date string "YYYY-MM-DD".
    Returns None if the format is invalid.
    """
    if not isinstance(date_str, str) or len(date_str.split('-')) != 3:
        return None
    try:
        parts = date_str.split('-')
        jp_year, month, day = int(parts[0]), parts[1], parts[2]
        if int(month) > 12: return None
        gregorian_year = jp_year + 2018
        return f"{gregorian_year}-{month}-{day}"
    except (ValueError, IndexError):
        return None

def run_reconciliation(ocr_file_path, xone_file_path, output_file_path):
    """
    Performs a comprehensive reconciliation and generates a detailed report
    with four output sheets: Matched, Mismatched Breaks, Unmatched OCR, and Unmatched X-one.
    """
    print("\n--- Starting Comprehensive Reconciliation Process ---")

    # --- Step 1: Load and Prepare OCR Data ---
    print("1. Processing OCR data...")
    df_ocr = pd.read_excel(ocr_file_path, dtype={'銘柄': str})
    df_ocr['ocr_record_id'] = range(len(df_ocr))
    df_ocr['発行日_converted'] = df_ocr['発行日'].apply(convert_japanese_date)
    df_ocr['発行日_converted'] = pd.to_datetime(df_ocr['発行日_converted'], errors='coerce')
    df_ocr['発行価格'] = pd.to_numeric(df_ocr['発行価格'], errors='coerce')
    df_ocr['募入額_scaled'] = df_ocr['募入額'].astype(str).str.replace(',', '', regex=False)
    df_ocr['募入額_scaled'] = pd.to_numeric(df_ocr['募入額_scaled'], errors='coerce') * 1_000_000
    
    # --- Step 2: Load and Prepare X-one Data ---
    print("2. Processing X-one data...")
    df_xone = pd.read_excel(xone_file_path, dtype={'Isin Code': str})
    df_xone['xone_record_id'] = range(len(df_xone))
    df_xone_filtered = df_xone[df_xone['Counterparty Name'] == 'AUCTION BOJ'].copy()
    print(f"   Filtered X-one data from {len(df_xone)} to {len(df_xone_filtered)} records.")
    
    df_xone_filtered['Value Date'] = pd.to_datetime(df_xone_filtered['Value Date'], format='%d/%m/%y', errors='coerce')
    df_xone_filtered['Notional'] = df_xone_filtered['Notional'].astype(str).str.replace('[, ]', '', regex=True)
    df_xone_filtered['Notional'] = pd.to_numeric(df_xone_filtered['Notional'], errors='coerce')
    df_xone_filtered['Product Price'] = pd.to_numeric(df_xone_filtered['Product Price'], errors='coerce')

    # --- Step 3: Merge Datasets using an OUTER join ---
    print("3. Merging datasets to identify all matches and breaks...")
    merged_df = pd.merge(
        df_ocr, df_xone_filtered,
        how='outer',
        left_on=['銘柄', '発行日_converted'],
        right_on=['Isin Code', 'Value Date'],
        indicator=True
    )

    # --- Step 4: Categorize Records ---
    print("4. Categorizing records based on merge status...")
    unmatched_ocr = merged_df[merged_df['_merge'] == 'left_only'].copy()
    unmatched_xone = merged_df[merged_df['_merge'] == 'right_only'].copy()
    candidates = merged_df[merged_df['_merge'] == 'both'].copy()

    # --- Step 5: Perform Numeric Comparisons on Candidates ---
    print("5. Performing numeric comparisons...")
    if not candidates.empty:
        price_tolerance, notional_tolerance = 1e-6, 1e-2
        candidates['price_match'] = np.isclose(candidates['発行価格'], candidates['Product Price'], atol=price_tolerance)
        candidates['notional_match'] = np.isclose(candidates['募入額_scaled'], candidates['Notional'], atol=notional_tolerance)
        candidates['overall_match'] = candidates['price_match'] & candidates['notional_match']
        
        matched_records = candidates[candidates['overall_match'] == True]
        mismatched_breaks = candidates[candidates['overall_match'] == False]
    else:
        matched_records = pd.DataFrame(columns=candidates.columns)
        mismatched_breaks = pd.DataFrame(columns=candidates.columns)

    print("\n--- RECONCILIATION SUMMARY ---")
    print(f"  - Fully Matched Records: {len(matched_records)}")
    print(f"  - Mismatched Breaks (Key match, value fail): {len(mismatched_breaks)}")
    print(f"  - Unmatched OCR Records (In OCR, not X-one): {len(unmatched_ocr)}")
    print(f"  - Unmatched X-one Records (In X-one, not OCR): {len(unmatched_xone)}")
    print("------------------------------")

    # --- Step 6: Prepare final output columns ---
    ocr_cols = ['ocr_record_id', 'pdf_name', '発行価格', '募入額', '銘柄', '発行日']
    xone_cols = ['xone_record_id', 'Counterparty Name', 'Isin Code', 'Value Date', 'Notional', 'Product Price']
    
    # --- Step 7: Export to a multi-sheet Excel file ---
    print(f"\n6. Exporting detailed results to '{output_file_path}'...")
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        matched_records.to_excel(writer, sheet_name='Matched', index=False)
        mismatched_breaks.to_excel(writer, sheet_name='Mismatched_Breaks', index=False)
        unmatched_ocr[ocr_cols].to_excel(writer, sheet_name='Unmatched_OCR', index=False)
        unmatched_xone[xone_cols].to_excel(writer, sheet_name='Unmatched_Xone', index=False)
        
    print("\n--- Reconciliation Process Complete ---")

if __name__ == "__main__":
    OCR_FILE = 'ocr_data.xlsx'
    XONE_FILE = 'xone_data.xlsx'
    OUTPUT_FILE = 'reconciliation_report.xlsx'

    if not (os.path.exists(OCR_FILE) and os.path.exists(XONE_FILE)):
        print(f"ERROR: Test files not found. Please run the data generation script first.")
    else:
        run_reconciliation(
            ocr_file_path=OCR_FILE,
            xone_file_path=XONE_FILE,
            output_file_path=OUTPUT_FILE
        )