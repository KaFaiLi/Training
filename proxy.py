# File: generate_comprehensive_test_data.py
import pandas as pd

def create_comprehensive_test_files():
    """
    Generates comprehensive dummy Excel files ('ocr_data.xlsx' and 'xone_data.xlsx')
    with a wide variety of matching, non-matching, and edge case scenarios.
    """
    print("--- Creating Comprehensive Dummy Data Files for Robust Testing ---")

    # OCR Data with various scenarios
    ocr_data = {
        'pdf_name': ['doc-01-perfect.pdf', 'doc-02-price-fail.pdf', 'doc-03-notional-fail.pdf', 'doc-04-both-fail.pdf', 'doc-05-ocr-orphan.pdf', 'doc-06-bad-amount.pdf', 'doc-07-bad-date.pdf', 'doc-08a-many-many.pdf', 'doc-08b-many-many.pdf', 'doc-09-duplicate.pdf', 'doc-10-tolerance-edge.pdf'],
        '発行価格': [99.85, 99.75, 101.50, 95.00, 99.99, 100.00, 100.00, 98.20, 98.30, 99.85, 99.75001],
        '募入額': ['2,500', '1,800', '4,000', '3,200', '1,000', 'TBD', '5,000', '6,000', '7,000', '2,500', '1,800'],
        '銘柄': ['JP_PERFECT_MATCH', 'JP_PRICE_FAIL', 'JP_NOTIONAL_FAIL', 'JP_BOTH_FAIL', 'JP_OCR_ORPHAN', 'JP_BAD_OCR_DATA_1', 'JP_BAD_OCR_DATA_2', 'JP_MANY_MANY', 'JP_MANY_MANY', 'JP_PERFECT_MATCH', 'JP_TOLERANCE_EDGE'],
        '発行日': ['06-10-05', '06-10-10', '06-10-15', '06-10-20', '06-11-01', '06-11-05', '06-25-11', '07-01-10', '07-01-10', '06-10-05', '06-10-12'],
        '払込期日': ['N/A']*11
    }
    df_ocr = pd.DataFrame(ocr_data)

    # X-one Data with corresponding scenarios
    xone_data = {
        'Counterparty Name': ['AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'OTHER BANK', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ', 'AUCTION BOJ'],
        'Counterparty Trading Name': ['BOJ']*12,
        'Value Date': ['05/10/24', '10/10/24', '15/10/24', '20/10/24', '25/10/24', '30/10/24', '05/11/24', '10/01/25', '10/01/25', '05/10/24', '12/10/24', 'INVALID'],
        'Notional': ['2,500,000,000', '1,800,000,000', '4,000,000,100', '3,250,000,000', 'N/A', '9,999,999,999', 'N/A', '6,000,000,000', '7,000,000,000', '2,500,000,000', '1,800,000,000', '1,111,111,111'],
        'Product Price': [99.85, 99.70, 101.50, 94.00, 100.0, 99.90, 100.00, 98.20, 98.35, 99.85, 99.75000, 100.0],
        'Isin Code': ['JP_PERFECT_MATCH', 'JP_PRICE_FAIL', 'JP_NOTIONAL_FAIL', 'JP_BOTH_FAIL', 'JP_FILTER_ME', 'JP_XONE_ORPHAN', 'JP_BAD_OCR_DATA_1', 'JP_MANY_MANY', 'JP_MANY_MANY', 'JP_PERFECT_MATCH', 'JP_TOLERANCE_EDGE', 'JP_BAD_XONE_DATA']
    }
    df_xone = pd.DataFrame(xone_data)

    try:
        df_ocr.to_excel('ocr_data.xlsx', index=False, engine='openpyxl')
        df_xone.to_excel('xone_data.xlsx', index=False, engine='openpyxl')
        print("Successfully created 'ocr_data.xlsx' and 'xone_data.xlsx'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_comprehensive_test_files()