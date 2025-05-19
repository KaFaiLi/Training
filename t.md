import os
import glob
import sys
import pandas as pd

def process_folder(input_folder: str, output_folder: str):
    """
    Reads all .csv, .csv.gz, and .zip files in input_folder,
    splits each file's data by month (based on 'pricingdate'),
    and writes one CSV per year-month to output_folder, named YYYYMM.csv.
    """
    os.makedirs(output_folder, exist_ok=True)

    # find all supported files
    patterns = ["*.csv", "*.csv.gz", "*.zip"]
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(input_folder, pat)))

    for file_path in files:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".gz":
            compression = "gzip"
        elif ext == ".zip":
            compression = "zip"
        else:
            compression = None

        print(f"Reading {os.path.basename(file_path)} (compression={compression})...")
        try:
            df = pd.read_csv(
                file_path,
                sep=";",
                compression=compression,
                parse_dates=["pricingdate"],
                dayfirst=False,   # set True if your CSV uses D/M/Y
                dtype=str
            )
        except Exception as e:
            print(f"  ⚠️  Failed to read: {e}")
            continue

        if "pricingdate" not in df.columns:
            print("  ⚠️  Skipping: no 'pricingdate' column found.")
            continue

        df["year_month"] = df["pricingdate"].dt.to_period("M").astype(str)
        months = df["year_month"].unique()
        if len(months) > 1:
            print(f"  ⚠️  Warning: multiple months in one file: {months}. Splitting.")

        for ym in months:
            out_df = df[df["year_month"] == ym].drop(columns="year_month")
            out_name = f"{ym.replace('-', '')}.csv"   # e.g. 202312.csv
            out_path = os.path.join(output_folder, out_name)
            print(f"  → Writing {out_name} ({len(out_df)} rows)")
            out_df.to_csv(out_path, index=False, sep=";")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_by_month.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder, output_folder = sys.argv[1], sys.argv[2]
    process_folder(input_folder, output_folder)
