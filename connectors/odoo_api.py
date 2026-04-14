# optimized version with incremental load and better logging
import xmlrpc.client
from utils.db import get_connection
from utils.logger import get_logger
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = get_logger("odoo_api")

TABLE_NAME = "odoo_contacts"
STATE_FILE = "state.json"


# 🔹 Get last sync time
def get_last_sync():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_sync")
    except:
        return None


# 🔹 Update last sync time
def update_last_sync():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(STATE_FILE, "w") as f:
        json.dump({"last_sync": now}, f)

    logger.info(f"Updated last_sync to {now}")


def odoo_run():

    logger.info("Odoo pipeline started")

    # Odoo Config
    url = os.getenv("ODOO_URL")
    db = os.getenv("ODOO_DB")
    username = os.getenv("ODOO_USER")
    password = os.getenv("ODOO_PASS")

    # Authenticate
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if not uid:
        raise Exception("Authentication failed ❌")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    logger.info("Connected to Odoo API")

    # 🔹 Get last sync
    last_sync = get_last_sync()

    if last_sync:
        logger.info(f"Incremental load from: {last_sync}")
        domain = [('write_date', '>', last_sync)]
    else:
        logger.info("First run - full load")
        domain = []

    # Extract Data
    data = models.execute_kw(
        db, uid, password,
        'res.partner', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'email', 'write_date']}
    )

    if not data:
        logger.info("No new records found")
        return
    logger.info(f"Fetched {len(data)} records from Odoo")


    # Connect PostgreSQL
    conn = get_connection()
    cur = conn.cursor()

    logger.info("Connected to PostgreSQL")

    # Create Table
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT PRIMARY KEY,
        name TEXT,
        email TEXT,
        write_date TIMESTAMP
    )
    """

    cur.execute(create_query)
    logger.info(f"Table '{TABLE_NAME}' ensured")

    # Insert / Update Data
    insert_query = f"""
    INSERT INTO {TABLE_NAME} (id, name, email, write_date)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name,
        email = EXCLUDED.email,
        write_date = EXCLUDED.write_date
    """

    processed = 0

    for row in data:
        cur.execute(insert_query, (
            row.get('id'),
            row.get('name'),
            row.get('email'),
            row.get('write_date')
        ))
        processed += 1

    conn.commit()
    conn.close()

    logger.info(f"{processed} rows processed into {TABLE_NAME}")

    # 🔹 Update last sync AFTER success
    update_last_sync()

    logger.info("Odoo pipeline completed successfully")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# # connectors/odoo_api.py

# import xmlrpc.client
# from utils.db import get_connection
# from utils.logger import get_logger
# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()
# logger = get_logger("odoo_api")

# TABLE_NAME = "odoo_contacts"


# def odoo_run():

#     logger.info("Odoo pipeline started")

#     # Odoo Config
#     url = os.getenv("ODOO_URL")
#     db = os.getenv("ODOO_DB")
#     username = os.getenv("ODOO_USER")
#     password = os.getenv("ODOO_PASS")

#     # Authenticate
#     common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
#     uid = common.authenticate(db, username, password, {})
#     print("UID:", uid)
#     if not uid:
#         raise Exception("Authentication failed ❌") 

#     models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

#     logger.info("Connected to Odoo API")

#     # Extract Data
#     data = models.execute_kw(
#         db, uid, password,
#         'res.partner', 'search_read',
#         [[]],
#         {'fields': ['id', 'name', 'email']}
#     )

#     if not data:
#         logger.warning("No data fetched from Odoo")
#         return

#     logger.info(f"Fetched {len(data)} records from Odoo")

#     # Connect PostgreSQL (reuse db.py)
#     conn = get_connection()
#     cur = conn.cursor()

#     logger.info("Connected to PostgreSQL")

#     # Create Table
#     create_query = f"""
#     CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#         id INT PRIMARY KEY,
#         name TEXT,
#         email TEXT
#     )
#     """

#     cur.execute(create_query)
#     logger.info(f"Table '{TABLE_NAME}' ensured")

#     # Insert Data
#     insert_query = f"""
#     INSERT INTO {TABLE_NAME} (id, name, email)
#     VALUES (%s, %s, %s)
#     ON CONFLICT (id) DO UPDATE
#     SET name = EXCLUDED.name,
#         email = EXCLUDED.email
#     """

#     inserted = 0

#     for row in data:
#         cur.execute(insert_query, (
#             row.get('id'),
#             row.get('name'),
#             row.get('email')
#         ))
#         inserted += 1

#     conn.commit()
#     conn.close()

#     # logger.info(f"{inserted} rows loaded into {TABLE_NAME}")
#     logger.info(f"{len(data)} rows processed into {TABLE_NAME}")
#     logger.info("Odoo pipeline completed successfully")
