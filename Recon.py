import pandas as pd
import numpy as np
import io
import os

# ==============================================================================
# 1. SETUP: Create dummy data files for a reproducible example
# ==============================================================================
def create_dummy_files():
    """Creates the two CSV data files required for the script."""
    # OCR Data with Japanese characters
    ocr_csv_data = """銘柄,発行日,発行価格,募入額,pdf_name
JP1024561Q15,30-04-10,99.981,"5,041",doc1.pdf
JP1024561Q15,30-04-10,99.981,"5,041",doc2.pdf
JP1024561Q16,01-05-15,100.01,"2,500",doc3.pdf
JP1024561Q17,02-06-20,99.5,"1,000",doc4.pdf
JP1024561Q18,04-07-25,99.8,"3,000",doc5.pdf
JP1024561Q99,31-01-01,,"1,234",doc6.pdf
JP1024561Q20,02-08-30,101.2,"4,500",doc7.pdf
JP1024561Q23,05-09-01,100.0,"5,000",doc8.pdf
"""

    # X-one Data
    xone_csv_data = """Isin Code,Value Date,Product Price,Notional,Counterparty Name
JP1024561Q15,10/04/18,99.981,5041000000,AUCTION BO
JP1024561Q15,10/04/18,99.981,"5,041,000,000",AUCTION BO
JP1024561Q16,15/05/89,100.01,2500000000,AUCTION BO
JP1024561Q17,20/06/90,99.50001,1000000000,AUCTION BO
JP1024561Q18,25/07/92,99.8,3000000001,AUCTION BO
JP1024561Q30,11/11/19,100.0,7000000000,AUCTION BO
JP1024561Q31,12/12/20,100.0,8000000000,SOME OTHER CP
"""
    # Use utf-8-sig to handle potential BOM and ensure Japanese characters are read correctly
    with open("ocr_data.csv", "w", encoding="utf-8-sig") as f:
        f.write(ocr_csv_data)

    with open("xone_data.csv", "w", encoding="utf-8-sig") as f:
        f.write(xone_csv_data)

    print("Dummy data files 'ocr_data.csv' and 'xone_data.csv' created.")


# ==============================================================================
# 2. HELPER FUNCTION: Date conversion for OCR data
# ==============================================================================
def convert_japanese_date(date_str):
    """
    Converts a Japanese date string "YY-MM-DD" to Gregorian "YYYY-MM-DD".
    Assumes a simplified conversion rule where YYYY = 1988 + YY.
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return None
        yy, mm, dd = parts
        gregorian_year = 1988 + int(yy)
        return f"{gregorian_year}-{mm}-{dd}"
    except (ValueError, TypeError):
        return None


# ==============================================================================
# 3. MAIN RECONCILIATION LOGIC
# ==============================================================================
def run_reconciliation():
    """Main function to execute the reconciliation process."""
    # --- OCR Data Preprocessing ---
    print("\n--- Preprocessing OCR Data ---")
    df_ocr = pd.read_csv("ocr_data.csv")
    print(f"Loaded {len(df_ocr)} rows from OCR data.")

    # 1. Convert Issuance Date
    df_ocr['発行日_converted_str'] = df_ocr['発行日'].apply(convert_japanese_date)
    df_ocr['発行日_converted'] = pd.to_datetime(df_ocr['発行日_converted_str'], errors='coerce')

    # 2. Convert and Filter Price
    df_ocr['発行価格'] = pd.to_numeric(df_ocr['発行価格'], errors='coerce')
    original_rows = len(df_ocr)
    df_ocr.dropna(subset=['発行価格'], inplace=True)
    print(f"Dropped {original_rows - len(df_ocr)} rows with null price.")

    # 3. Drop 2023 Records
    original_rows = len(df_ocr)
    df_ocr = df_ocr[df_ocr['発行日_converted'].dt.year != 2023]
    print(f"Dropped {original_rows - len(df_ocr)} records from year 2023.")

    # 4. Clean and Scale Notional
    df_ocr['募入額_scaled'] = df_ocr['募入額'].astype(str).str.replace(',', '', regex=False)
    df_ocr['募入額_scaled'] = pd.to_numeric(df_ocr['募入額_scaled'], errors='coerce') * 1_000_000

    # 5. Retain All Rows (achieved by not aggregating)
    print(f"OCR data preprocessed. {len(df_ocr)} rows remaining.")

    # --- X-one Data Preprocessing ---
    print("\n--- Preprocessing X-one Data ---")
    df_xone = pd.read_csv("xone_data.csv")
    print(f"Loaded {len(df_xone)} rows from X-one data.")

    # 1. Filter Records
    original_rows = len(df_xone)
    df_xone = df_xone[df_xone['Counterparty Name'] == "AUCTION BO"].copy()
    print(f"Filtered by 'Counterparty Name', {len(df_xone)} rows remaining.")

    # 2. Convert Dates
    df_xone['Value Date'] = pd.to_datetime(df_xone['Value Date'], format='%d/%m/%y', errors='coerce')

    # 3. Clean Notional
    df_xone['Notional'] = df_xone['Notional'].astype(str).str.replace(',', '', regex=False)
    df_xone['Notional'] = pd.to_numeric(df_xone['Notional'], errors='coerce')

    # 4. Convert Price
    df_xone['Product Price'] = pd.to_numeric(df_xone['Product Price'], errors='coerce')
    print(f"X-one data preprocessed. {len(df_xone)} rows remaining.")

    # --- DEBUGGING OUTPUT (PART 1) ---
    DEBUG_KEY = "JP1024561Q15"
    print(f"\n--- DEBUG: OCR values for key '{DEBUG_KEY}' before merge ---")
    debug_ocr_sample = df_ocr[df_ocr['銘柄'] == DEBUG_KEY]
    print(debug_ocr_sample[['銘柄', '発行日_converted', '募入額', '募入額_scaled']])

    # --- Reconciliation Logic ---
    print("\n--- Performing Reconciliation ---")

    # 1. Join (Merge) the Data
    merged_df = pd.merge(
        df_ocr,
        df_xone,
        how='outer',
        left_on=['銘柄', '発行日_converted'],
        right_on=['Isin Code', 'Value Date'],
        indicator=True
    )
    # The many-to-many join creates all possible pairings for matching keys.
    # For key JP1024561Q15, 2 OCR rows x 2 X-one rows = 4 merged rows.
    print(f"Outer join resulted in {len(merged_df)} total rows.")
    
    # --- DEBUGGING OUTPUT (PART 2) ---
    print(f"\n--- DEBUG: Merged data for key '{DEBUG_KEY}' ---")
    debug_merged_sample = merged_df[
        (merged_df['銘柄'] == DEBUG_KEY) | (merged_df['Isin Code'] == DEBUG_KEY)
    ]
    print(debug_merged_sample[[
        '銘柄', 'Isin Code', '発行価格', 'Product Price',
        '募入額_scaled', 'Notional', '_merge'
    ]])


    # 2. Numeric Comparisons
    # Use rtol=0 to rely solely on absolute tolerance as per requirements.
    # np.isclose returns False for NaN comparisons, which is the desired behavior.
    merged_df['price_match'] = np.isclose(
        merged_df['発行価格'],
        merged_df['Product Price'],
        atol=1e-6,
        rtol=0
    )
    merged_df['notional_match'] = np.isclose(
        merged_df['募入額_scaled'],
        merged_df['Notional'],
        atol=1e-2,
        rtol=0
    )

    # 3. Record Classification
    # Fully Matched
    matched_mask = (merged_df['_merge'] == 'both') & \
                   (merged_df['price_match']) & \
                   (merged_df['notional_match'])
    matched_records = merged_df[matched_mask]

    # Mismatched Breaks
    mismatched_mask = (merged_df['_merge'] == 'both') & \
                      (~merged_df['price_match'] | ~merged_df['notional_match'])
    mismatched_breaks = merged_df[mismatched_mask]

    # Unmatched OCR
    unmatched_ocr_mask = merged_df['_merge'] == 'left_only'
    unmatched_ocr = merged_df[unmatched_ocr_mask]

    # Unmatched X-one
    unmatched_xone_mask = merged_df['_merge'] == 'right_only'
    unmatched_xone = merged_df[unmatched_xone_mask]

    print("\n--- Reconciliation Summary ---")
    print(f"Fully Matched Records: {len(matched_records)}")
    print(f"Mismatched Breaks:     {len(mismatched_breaks)}")
    print(f"Unmatched OCR Records:   {len(unmatched_ocr)}")
    print(f"Unmatched X-one Records: {len(unmatched_xone)}")

    # --- Export Results ---
    output_filename = "reconciliation_results.xlsx"
    print(f"\n--- Exporting results to '{output_filename}' ---")
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='Merged_Data', index=False)
        matched_records.to_excel(writer, sheet_name='Matched', index=False)
        mismatched_breaks.to_excel(writer, sheet_name='Mismatched_Breaks', index=False)
        unmatched_ocr.to_excel(writer, sheet_name='Unmatched_OCR', index=False)
        unmatched_xone.to_excel(writer, sheet_name='Unmatched_X-one', index=False)

    print("Export complete.")

    # --- Cleanup ---
    os.remove("ocr_data.csv")
    os.remove("xone_data.csv")
    print("\nCleaned up dummy data files.")


if __name__ == "__main__":
    create_dummy_files()
    run_reconciliation()