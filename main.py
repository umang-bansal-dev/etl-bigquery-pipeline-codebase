import time
import sys
sys.path.append('.')
from src.extract import extract
from src.transform import transform
from src.load import load

def run_pipeline():

    print('=' * 50)
    print('NYC TAXI PIPELINE - STARTING')
    print('=' * 50)

    pipeline_start = time.time()

    print('STEP 1 OF 3 - EXTRACT')
    step_start=time.time()
    raw_df = extract()
    extract_time_diff = round(time.time()-step_start,2)
    print(f'Extraction Completed in {extract_time_diff} seconds.')

    print('STEP 2 OF 3 - TRANSFORM')
    step_start=time.time()
    clean_df = transform(raw_df)
    transform_time_diff = round(time.time()-step_start,2)
    print(f'Transformation Completed in {transform_time_diff} seconds.')

    print('STEP 3 OF 3 - LOAD')
    step_start=time.time()
    load(clean_df)
    load_time_diff = round(time.time()-step_start,2)
    print(f'Load Completed in {load_time_diff} seconds.')

    total_time = round(time.time()-pipeline_start,2)

    print('=' * 50)
    print('PIPELINE COMPLETED SUCCESSFULLY!!!')
    print('=' * 50)
    print('Pipeline Summary:')
    print(f'Raw Rows Extracted: {len(raw_df):,}')
    print(f'Clean Rows Loaded: {len(clean_df):,}')
    print(f'Rows Removed: {(len(raw_df)-len(clean_df)):,}')
    print(f'Extract Time: {extract_time_diff}s')
    print(f'Transform Time: {transform_time_diff}s')
    print(f'Load Time : {load_time_diff}s')
    print(f'Pipeline Time: {total_time}s')
    print('\n View Data in BigQuery.')
    print(f" https://console.cloud.google.com/bigquery")
    print("=" * 50 )

if __name__ == "__main__":
    run_pipeline()