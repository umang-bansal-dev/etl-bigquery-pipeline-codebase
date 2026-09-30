import pandas as pd
import sys
sys.path.append('.')
import config
#import extract

def fix_datatypes(df):
    print('Fixing datatypes of Columns for transforming data\n')
    datetime_columns=["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    for col in datetime_columns:
        df[col]=pd.to_datetime(df[col],errors='coerce')
    print('Datetime Columns Fixed!!!\n')

    numeric_columns=["passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount","payment_type"]
    for col in numeric_columns:
        df[col]=pd.to_numeric(df[col],errors='coerce')
    print('Numeric Columns Fixed!!!\n')

    return df

def remove_bad_rows(df):
    original_count=len(df)
    print('Removing Bad Rows and Unwanted data from dataframe\n')
    
    datetime_columns=["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    numeric_columns=["passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount","payment_type"]

    df= df.dropna(subset=datetime_columns)
    df= df.dropna(subset=numeric_columns)
    
    df= df[(df['passenger_count']>=1)&(df['passenger_count']<=6)] # only keeping the data where passenger_count is greater than 1 and less than 6
    df= df[df['trip_distance']>0]  #only keeping the data where trip distance is greater than 0
    df= df[df['fare_amount']>0]  #only keeping the data where fare_amount distance is a positive value
    df= df[df['total_amount']>0]  #only keeping the data where total_amount distance is a positive value

    removed_count=original_count-len(df)
    removal_percentage = (removed_count/original_count)*100

    print(f'Removed {removed_count:,} Bad rows, {removal_percentage:.2f}%\n')
    print(f"Clean rows remaining: {len(df):,}")

    return df

def add_new_rows(df):
    print('Adding Derived Columns: \n')

    df['trip_duration_minutes'] = (df['tpep_dropoff_datetime']-df['tpep_pickup_datetime']).dt.total_seconds()/60
    df['trip_duration_minutes'] = df['trip_duration_minutes'].round(2)
    print('Added trip_duration_minutes')

    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    print('Added pickup_hour')

    df['cost_per_mile'] = (df['fare_amount']/df['trip_distance']).where(df['trip_distance']>0,0).round(2)
    print('Added cost_per_mile')

    df['tip_percentage'] = ((df['tip_amount']/df['fare_amount'])*100).where(df['fare_amount']>0,0).round(2)
    print('Added tip_percentage')

    payment_map = {
        1: 'Credit Card',
        2: 'Cash',
        3: 'No Charge',
        4: 'Dispute',
        5: 'Unknown',
        6: 'Voided Trip'
    }
    df['payment_type_label'] = df['payment_type'].map(payment_map).fillna('Unknown')
    print('Added payment_type_label')

    return df

def remove_outliers(df):
    original_count=len(df)
    print('Removing Outliers...\n')

    df= df[(df['trip_duration_minutes']>=1)&(df['trip_duration_minutes']<=180)] # Trips under 1 minute or over 3 hours are not realistic
    df= df[df['trip_distance']<=100]  #only keeping the data where trip_distance is less than 100 miles
    df= df[df['cost_per_mile']<=500]  #only keeping the data where cost_per_mile is less than $500 

    removed_count=original_count-len(df)
    removal_percentage = (removed_count/original_count)*100

    print(f'Removed {removed_count:,} Outliers, {removal_percentage:.2f}%\n')
    print(f"Final Clean Rows: {len(df):,}")
    return df

def select_final_columns(df):
    print("Selecting final columns for BigQuery...\n")

    final_columns = [
        # Original columns
        'VendorID',
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime',
        'passenger_count',
        'trip_distance',
        'fare_amount',
        'tip_amount',
        'tolls_amount',
        'total_amount',
        'payment_type',
        # New calculated columns
        'trip_duration_minutes',
        'pickup_hour',
        'cost_per_mile',
        'tip_percentage',
        'payment_type_label'
    ]

    df = df[final_columns]

    print(f"Selected {len(final_columns)} columns for BigQuery\n")

    return df

def transform(df):
    print('=' * 50)
    print('Transforming the raw data into clean data\n')
    print('=' * 50)

    df = fix_datatypes(df)
    df = remove_bad_rows(df)
    df = add_new_rows(df)
    df = remove_outliers(df)
    df = select_final_columns(df)

    print(f'Final Rows: {len(df):,}\n')
    print(f'Final Columns: {len(df.columns)}\n')

    return df


if __name__ == "__main__":
    from extract import extract
    raw_df = extract()
    clean_df=transform(raw_df)

    print(f"\nSample of transformed data:")
    print(clean_df.head(3))

    #list of newly added columns
    new_list = ['trip_duration_minutes', 'pickup_hour', 'cost_per_mile', 'tip_percentage', 'payment_type_label']
    print(f"\nNew columns added: \n")
    print(clean_df[new_list].head(5))

    print(f"\nFinal data types:")
    print(clean_df.dtypes)