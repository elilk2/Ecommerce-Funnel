"""
This file unions the 5 month CSV files into a parquet that is much more storage friendly and possible to process through pandas

Run with 'python src/ingestion.py'

"""


import duckdb

print("Starting Ingestion: Please Wait a Minute")

duckdb.sql("""
    COPY(
        SELECT * FROM read_csv_auto('data/raw/*.csv')
        ) TO 'data/processed/master_events.parquet' (FORMAT PARQUET);
    """)

print("Ingestion Complete: Parquet File Saved at data/processed/master_events.parquet")





