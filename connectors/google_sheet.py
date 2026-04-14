# Google Sheets to PostgreSQL Pipeline with dotenv and db connection abstraction

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import psycopg2
# from psycopg2.extras import execute_values
# import re
# import os
# from dotenv import load_dotenv      
# load_dotenv()  

# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER")
# DB_PASS = os.getenv("DB_PASS")
# DB_PORT = os.getenv("DB_PORT")

# SPREADSHEET_ID = "1gC1HVl__zlxRTMx2eph9UOHHrejyOpihPSWp90cZgQA"
# SHEET_NAME = "Truck_tb"
# TABLE_NAME = "truck_tb"


# def clean_column(name):
#     name = name.lower()
#     name = re.sub(r"[()]", "", name)
#     name = name.replace(" ", "_")
#     name = name.replace("/", "_")
#     return name


# def run():

#     #Connect Google Sheets
#     scope = [
#         "https://spreadsheets.google.com/feeds",
#         "https://www.googleapis.com/auth/drive"
#     ]

#     creds = ServiceAccountCredentials.from_json_keyfile_name(
#         "credentials.json", scope
#     )

#     client = gspread.authorize(creds)

#     sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

#     rows = sheet.get_all_records()

#     print(f"Fetched {len(rows)} rows")

#     if not rows:
#         print("No data found")
#         return

    
#     # Build Column Mapping
#     sheet_columns = list(rows[0].keys())
#     column_map = {col: clean_column(col) for col in sheet_columns}
#     db_columns = list(column_map.values())
#     print("Column mapping:", column_map)

  
#     # Connect PostgreSQL
#     conn = psycopg2.connect(
#         host="DB_HOST",
#         database="DB_NAME",
#         user="DB_USER",
#         password="DB_PASS",
#         port="DB_PORT"
#     )

#     cur = conn.cursor()

 
#     # Create Table
#     column_defs = ", ".join([f"{c} TEXT" for c in db_columns])

#     create_table_query = f"""
#     CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#         {column_defs},
#         PRIMARY KEY (truck_id)
#     )
#     """

#     cur.execute(create_table_query)

#     print("Table ensured")

   
#     # Prepare Bulk Data
#     data = []

#     for r in rows:
#         row_values = [str(r[col]) for col in sheet_columns]
#         data.append(row_values)

  
#     # Bulk Insert
#     insert_query = f"""
#     INSERT INTO {TABLE_NAME} ({",".join(db_columns)})
#     VALUES %s
#     ON CONFLICT (truck_id) DO NOTHING
#     """

#     execute_values(cur, insert_query, data)

#     conn.commit()
#     conn.close()

#     print("Data loaded successfully")


# if __name__ == "__main__":
#     run()








# Optimized version with better structure, logging, and error handling
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

from utils.db import get_connection
from utils.logger import get_logger

# Logger
logger = get_logger("google_sheet")

# Spreadsheet info
SPREADSHEET_ID = "1gC1HVl__zlxRTMx2eph9UOHHrejyOpihPSWp90cZgQA"
SHEET_NAME = "Truck_tb"
TABLE_NAME = "truck_tb"


def clean_column(name):
    name = name.lower()
    name = re.sub(r"[()]", "", name)
    name = name.replace(" ", "_")
    name = name.replace("/", "_")
    return name


def run():

    logger.info("Google Sheets pipeline started")

   
    # Google API Authentication
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)

    logger.info("Connected to Google Sheets")

    # Read Sheet Data
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    rows = sheet.get_all_records()

    if not rows:
        logger.warning("No data found in sheet")
        return

    logger.info(f"Fetched {len(rows)} rows from Google Sheet")

   
    # Prepare Columns
    original_columns = list(rows[0].keys())
    clean_columns = [clean_column(c) for c in original_columns]

    column_map = dict(zip(original_columns, clean_columns))

    logger.info(f"Column mapping: {column_map}")

  
    # Connect PostgreSQL
    conn = get_connection()
    cur = conn.cursor()

    logger.info("Connected to PostgreSQL")

  
    # Create Table
    column_defs = ", ".join([f"{c} TEXT" for c in clean_columns])

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {column_defs}
    )
    """

    cur.execute(create_table_query)

    logger.info(f"Table '{TABLE_NAME}' ensured")


    # Insert Data
    column_list = ", ".join(clean_columns)
    placeholders = ", ".join(["%s"] * len(clean_columns))

    insert_query = f"""
    INSERT INTO {TABLE_NAME} ({column_list})
    VALUES ({placeholders})
    ON CONFLICT (truck_id) DO NOTHING
    """

    inserted_rows = 0

    for r in rows:

        values = [str(r[orig]) for orig in original_columns]

        cur.execute(insert_query, values)

        inserted_rows += cur.rowcount

    conn.commit()
    conn.close()
    
    duplicates = len(rows) - inserted_rows
    logger.info(f"{duplicates} duplicate rows skipped")
    logger.info(f"{inserted_rows} rows inserted into {TABLE_NAME}")

    logger.info("Google Sheets pipeline completed successfully")