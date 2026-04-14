import pandas as pd
from utils.db import get_connection
from utils.logger import get_logger
import re

logger = get_logger("csv_loader")

FILE_PATH = r"C:\Users\Admin\Downloads\FM_pipeline.xlsx - Truck_tb.csv"
TABLE_NAME = "Truck_tb_csv"


def clean_column(name):
    name = name.lower()
    name = re.sub(r"[()]", "", name)
    name = name.replace(" ", "_")
    name = name.replace("/", "_")
    return name


def run():
    logger.info("CSV pipeline started")

    df = pd.read_csv(FILE_PATH)

    if df.empty:
        logger.warning("CSV is empty")
        return

    original_columns = df.columns.tolist()
    clean_columns = [clean_column(c) for c in original_columns]

    df.columns = clean_columns

    conn = get_connection()
    cur = conn.cursor()

    column_defs = ", ".join([f"{c} TEXT" for c in clean_columns])

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            {column_defs}
        )
    """)

    column_list = ", ".join(clean_columns)
    placeholders = ", ".join(["%s"] * len(clean_columns))

    insert_query = f"""
        INSERT INTO {TABLE_NAME} ({column_list})
        VALUES ({placeholders})
    """

    for _, row in df.iterrows():
        cur.execute(insert_query, list(row.astype(str)))

    conn.commit()
    conn.close()

    logger.info(f"{len(df)} rows inserted")
    logger.info("CSV pipeline completed")
    
if __name__ == "__main__":
    run()