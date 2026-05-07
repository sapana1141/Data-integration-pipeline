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
