You are an expert Python developer specializing in data reconciliation and analysis using the Pandas library. Your task is to write a single, complete Python script that performs a comprehensive reconciliation between two datasets stored in Excel files.

### Dataset 1: OCR Data (`ocr_data.xlsx`)

*   **Columns:**
    *   `pdf_name` (string)
    *   `発行価格` (Issue Price, numeric)
    *   `募入額` (Funded Amount, string with commas)
    *   `銘柄` (Isin Code, string)
    *   `発行日` (Issue Date, Japanese-style string)
    *   `払込期日` (Payment Date, string)
*   **Transformations:**
    1.  **`発行日` (Date Conversion):** This column is a string in `"YY-MM-DD"` format representing a Japanese era year. Convert it to a Gregorian date by adding 2018 to the year value. For example, `"06-10-05"` becomes `"2024-10-05"`. Handle potential malformed dates gracefully.
    2.  **`募入額` (Notional Scaling):** This is a string that may contain commas (e.g., `"2,500"`). Remove the commas, convert the value to a number, and then multiply it by 1,000,000 to match the scale of the X-one data.
    3.  **`発行価格` (Numeric Conversion):** Convert this column to a numeric type.

### Dataset 2: X-one Data (`xone_data.xlsx`)

*   **Columns:**
    *   `Counterparty Name` (string)
    *   `Value Date` (string, `DD/MM/YY` format)
    *   `Notional` (string with commas)
    *   `Product Price` (numeric)
    *   `Isin Code` (string)
*   **Transformations:**
    1.  **Filtering:** Before any matching, filter the dataset to only include rows where `Counterparty Name` is exactly `"AUCTION BOJ"`.
    2.  **`Value Date` (Date Conversion):** Convert this column from its `DD/MM/YY` string format (e.g., `"05/10/24"`) into a standard datetime object.
    3.  **`Notional` and `Product Price` (Numeric Conversion):** Clean these columns of any commas or spaces and convert them to numeric types.

### Reconciliation Logic

1.  **Key-Based Matching:**
    *   The primary keys for matching are the instrument identifier and the date.
    *   Match OCR's `銘柄` with X-one's `Isin Code`.
    *   Match OCR's **converted** `発行日` with X-one's **converted** `Value Date`.

2.  **Join Strategy:**
    *   Use a **`pandas.merge`** with a **`how='outer'`** join to ensure that all records from both datasets are included in the result.
    *   Use the `indicator=True` parameter in the merge to create a `_merge` column that tracks the origin of each row (`left_only`, `right_only`, or `both`).

3.  **Numeric Comparisons (for key-matched records):**
    *   For rows where the keys matched (`_merge == 'both'`), perform two numeric comparisons using `numpy.isclose()` to handle floating-point precision.
    *   **Price Comparison:** Compare OCR's `発行価格` with X-one's `Product Price` using a tolerance of `1e-6`.
    *   **Notional Comparison:** Compare the scaled OCR `募入額` with X-one's `Notional` using a tolerance of `1e-2`.

### Output Requirements

Export the results to a single Excel file with **four separate sheets**:

1.  **`Matched`:** Contains the combined rows where the keys matched AND both the price and notional comparisons passed.
2.  **`Mismatched_Breaks`:** Contains the combined rows where the keys matched, but at least one of the numeric comparisons (price or notional) failed.
3.  **`Unmatched_OCR`:** Contains only the original OCR rows that had no key match in the X-one data (`_merge == 'left_only'`).
4.  **`Unmatched_Xone`:** Contains only the original (but filtered) X-one rows that had no key match in the OCR data (`_merge == 'right_only'`).

The final Python script should be self-contained, well-commented, and include a main execution block (`if __name__ == "__main__":`) that shows how to run the function with example file paths.