import pandas as pd        
import os 
import sys
sys.path.append('.')                 
import config              

def read_csv():
    print("=" * 50)
    print("Reading raw CSV file...")
    print("=" * 50)

    #checking csv is present or not
    if not os.path.exists(config.RAW_DATA_PATH):
        raise FileNotFoundError(
            f"CSV file not found at: {config.RAW_DATA_PATH}"
        )

    print(f"File found: {config.RAW_DATA_PATH}")

    # Read the CSV 
    TEST_MODE = True
    df = pd.read_csv(config.RAW_DATA_PATH,nrows=10000 if TEST_MODE else None)

    print(f"File read successfully")
    print(f"Total rows    : {len(df):,}")
    print(f"Total columns : {len(df.columns)}")

    return df


def validate(df):
    print("Running data validation checks...")

    # Check 1: File is not empty
    if len(df) == 0:
        raise ValueError("CSV file is empty no rows found.")

    print(f"Check 1 passed: file has {len(df):,} rows")

    # Check 2: Required columns exist
    required_columns = ["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount"]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}\n"
            f"Columns found in file: {list(df.columns)}"
        )

    print(f"Check 2 passed: all required columns are present")

    # Check 3: No column is fully empty 
    fully_empty = [col for col in df.columns if df[col].isnull().all()]

    if fully_empty:
        raise ValueError(f"These columns are completely empty: {fully_empty}")

    print(f"Check 3 passed: no column is fully empty ")

    print(f"\nAll validation checks passed!")
    return df


def extract():
    df = read_csv()
    df = validate(df)
    return df


if __name__ == "__main__":
    df = extract()
    print(f"\nFirst 3 rows of data:")
    print(df.head(3))
    print(f"\nColumn data types:")
    print(df.dtypes)