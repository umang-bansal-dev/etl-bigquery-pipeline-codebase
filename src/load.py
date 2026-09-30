import pandas as pd
import sys
sys.path.append('.')
import config
from google.cloud import bigquery as bq
from google.cloud import storage as gcs
from google.cloud.storage.retry import DEFAULT_RETRY
from google.cloud.exceptions import NotFound

def create_gcs_bucket():
    
    print('\nUploading Raw file into Google Cloud Storage...')
    storage_client = gcs.Client(
        project=config.GCP_PROJECT_ID
    )

    try :
        bucket = storage_client.get_bucket(config.GCS_BUCKET_NAME)
        print(f'Bucket already exists: {bucket}\n')
    except NotFound:
        bucket = storage_client.create_bucket(config.GCS_BUCKET_NAME, location= 'US')
        print(f'Bucket created: {bucket}\n')

    return bucket

def upload_to_gcs(bucket):
    blob_name = config.GCS_RAW_FOLDER + "raw_data.csv"
    blob = bucket.blob(blob_name)

    gcs_path = f"gs://{config.GCS_BUCKET_NAME}/{blob_name}"

    # Check whether file already exists in GCS
    if blob.exists():
        print(f"File already exists in GCS: {gcs_path}")
        print("Skipping GCS upload...\n")
        return gcs_path

    print("Uploading raw_data.csv to GCS...")

    blob.chunk_size = 32 * 1024 * 1024  # 32 MB

    retry = DEFAULT_RETRY.with_timeout(500.0)

    blob.upload_from_filename(
        config.RAW_DATA_PATH,
        timeout=500,
        retry=retry
    )

    print(f"File uploaded to GCS Bucket: {gcs_path}\n")

    return gcs_path

def create_bq_dataset(bq_client):

    print('Setting up BigQuery...')

    dataset_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_NAME}"
    try:
        bq_client.get_dataset(dataset_id)
        print(f"Dataset already exists: {config.BQ_DATASET_NAME}")
    except NotFound:
        dataset = bq.Dataset(dataset_id)
        dataset.location = 'US'

        bq_client.create_dataset(dataset)
        print(f"BigQuery Dataset Created: {dataset}")

def define_schema():
    schema = [
        bq.SchemaField("VendorID", "INTEGER", description="Taxi vendor ID — 1 or 2"),
        bq.SchemaField("tpep_pickup_datetime", "TIMESTAMP", description="Trip pickup date and time"),
        bq.SchemaField("tpep_dropoff_datetime", "TIMESTAMP", description="Trip dropoff date and time"),
        bq.SchemaField("passenger_count", "INTEGER", description="Number of passengers — 1 to 6"),
        bq.SchemaField("trip_distance", "FLOAT", description="Trip distance in miles"),
        bq.SchemaField("fare_amount", "FLOAT", description="Base fare amount in USD"),
        bq.SchemaField("tip_amount", "FLOAT", description="Tip amount in USD"),
        bq.SchemaField("tolls_amount", "FLOAT", description="Toll charges in USD"),
        bq.SchemaField("total_amount", "FLOAT", description="Total trip amount in USD"),
        bq.SchemaField("payment_type", "INTEGER", description="Payment type code"),
        bq.SchemaField("trip_duration_minutes", "FLOAT", description="Calculated trip duration in minutes"),
        bq.SchemaField("pickup_hour", "INTEGER", description="Hour of pickup — 0 to 23"),
        bq.SchemaField("cost_per_mile", "FLOAT", description="Fare amount divided by trip distance"),
        bq.SchemaField("tip_percentage", "FLOAT", description="Tip as percentage of fare amount"),
        bq.SchemaField("payment_type_label", "STRING", description="Human readable payment type label"),
    ]

    return schema


def load_to_bigquery(df,bq_client):
    
    print(f"Loading {len(df):,} rows into BigQuery Table...")
    print(f"Target Table is: {config.BQ_TABLE_ID}")

    job_config = bq.LoadJobConfig(
        schema=define_schema(),
        write_disposition = bq.WriteDisposition.WRITE_TRUNCATE,
        #skip_leading_rows=1,
        source_format = bq.SourceFormat.CSV
    )

    total_rows = len(df)
    chunks_loaded=0
    rows_loaded=0

    for start in range(0,total_rows,config.CHUNK_SIZE):

        chunk = df.iloc[start:start+config.CHUNK_SIZE]
        if start == 0:
            job_config.write_disposition = bq.WriteDisposition.WRITE_TRUNCATE
        else:
            job_config.write_disposition = bq.WriteDisposition.WRITE_APPEND


        job = bq_client.load_table_from_dataframe(chunk,config.BQ_TABLE_ID,job_config=job_config)

        job.result()
        rows_loaded+=len(chunk)
        chunks_loaded+=1
        print(f"Chunk {chunks_loaded} loaded\n")
        print(f"{rows_loaded:,}/{total_rows:,}rows")

    print(f"\nAll data loaded into BigQuery!")
    return rows_loaded

def verify_load(bq_client):
    
    query = f"""
    SELECT count(*) from `{config.BQ_TABLE_ID}`
    """
    result = bq_client.query(query).result()
    total = list(result)[0][0]

    print(f"\nData is in BigQuery, Total records loaded :{total:,} ")

    
def load(df):

    bq_client=bq.Client(
        project=config.GCP_PROJECT_ID
    )

    bucket = create_gcs_bucket()
    upload_to_gcs(bucket)

    create_bq_dataset(bq_client)
    load_to_bigquery(df,bq_client)
    verify_load(bq_client)

    print(f"\nLOAD COMPLETE: Data is live in BigQuery!")
    print(f"View your table at:")
    print(f"https://console.cloud.google.com/bigquery?project={config.GCP_PROJECT_ID}")




if __name__ == "__main__":
    from  extract import extract
    from transform import transform

    raw_df = extract()
    clean_df = transform(raw_df)
    load(clean_df)