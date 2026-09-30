# NYC Taxi ETL Pipeline 🚕

An end-to-end ETL data pipeline built with Python and Google Cloud Platform.

## What This Project Does

Extracts raw NYC Taxi trip data from a CSV file, cleans and transforms it,
and loads it into Google BigQuery for analysis.


## What the Pipeline Does

| Step | File | Action |
|---|---|---|
| Extract | extract.py | Reads 10,000 rows, validates 3 data quality checks |
| Transform | transform.py | Removes 94 bad rows, adds 5 new columns |
| Load | load.py | Uploads to GCS, loads 9,906 rows into BigQuery |

## New Columns Created

| Column | Description |
|---|---|
| trip_duration_minutes | Calculated from pickup and dropoff time |
| pickup_hour | Hour of the day — 0 to 23 |
| cost_per_mile | Fare divided by distance |
| tip_percentage | Tip as % of fare |
| payment_type_label | Human readable — Cash, Credit Card etc |

## How to Run

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set GCP credentials: `SET GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json`
6. Run pipeline: `python main.py`

## Results

- Raw rows: 10,000
- Clean rows loaded to BigQuery: 9,906
- Rows removed (bad data + outliers): 94
- Pipeline run time: ~12 seconds

## Author

Umang Bansal — Data Engineer | GCP Specialist
[LinkedIn](https://www.linkedin.com/in/umang-bansal) |
[GitHub](https://github.com/umang-bansal-dev)