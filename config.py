import os

GCP_PROJECT_ID = "etl-bigquery-project-509907"

GCS_BUCKET_NAME = "etl-pipeline-umang-raw-data"

GCS_RAW_FOLDER = "raw/"


BQ_DATASET_NAME = "nyc_taxi_data_db"

BQ_TABLE_NAME = "taxi_trips"

BQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_NAME}.{BQ_TABLE_NAME}"


RAW_DATA_PATH = "data/raw_data.csv"


CHUNK_SIZE = 10000
BQ_WRITE_MODE = "replace"


# Path to svc-key
CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "etl-pipeline-svc-key.json"  # fallback default
)