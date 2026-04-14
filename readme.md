# Project Overview

This project is a **data integration pipeline** that extracts data from multiple sources and loads it into a PostgreSQL database.

### Objective

- Build reusable **data connectors**
- Extract data from different sources:
    - Google Sheets
    - Local CSV files
    - Odoo ERP (API)
- Load data into PostgreSQL
- Add **logging, scheduling, and automation**
- Follow **real-world data engineering practices**

---

# Project Structure

```
Integration/
│
├── connectors/
│   ├── google_sheet.py     # Google Sheets → PostgreSQL
│   ├── csv_loader.py       # Local CSV → PostgreSQL
│   ├── odoo_api.py         # Odoo ERP API → PostgreSQL
│
├── utils/
│   ├── db.py               # Database connection logic
│   ├── logger.py           # Logging setup
│
├── run_pipeline.py         # Main orchestrator
├── .env                    # Environment variables
├── credentials.json        # Google service account credentials
├── requirements.txt        # Dependencies
│
├── *.log                   # Log files (generated during runs)
└── state.json              # Stores last sync time (incremental load)
```

---

# Data Sources Used

## 1. Google Sheets

- Extract data using **service account**
- API: `gspread`
- Example use: Truck data (`Truck_tb`)

---

## 2. CSV Files (Local)

- Read CSV from local system
- Use `pandas` for ingestion
- Useful for offline / batch ingestion

---

## 3. Odoo ERP (API)

- Extract data using **XML-RPC API**
- Incremental load using `write_date`
- Stores last sync in `state.json`

---

# What Each File Does

## 🔹 `connectors/google_sheet.py`

- Connects to Google Sheets using service account
- Reads data from sheet
- Cleans column names
- Loads data into PostgreSQL
- Prevents duplicates using:   ON CONFLICT (truck_id) DO NOTHING

---

## 🔹 `connectors/csv_loader.py`

- Reads local CSV using `pandas`
- Cleans column names
- Creates table dynamically
- Inserts data into PostgreSQL

---

## 🔹 `connectors/odoo_api.py`

- Connects to Odoo via API
- Fetches records (`res.partner`)
- Supports **incremental loading**
- Uses:
    - `write_date`
    - `state.json`
- Upserts data using:  ON CONFLICT (id) DO UPDATE

---

## 🔹 `utils/db.py`

- Centralized PostgreSQL connection
- Reads DB config from `.env`
- Used by all connectors

---

## 🔹 `utils/logger.py`

- Creates logger for each pipeline
- Writes logs to `.log` files
- Format:  timestamp | level | message

---

## 🔹 `run_pipeline.py`

- Main orchestrator
- Runs all pipelines in sequence

Example:

```
from connectors.csv_loader import run as csv_run
from connectors.google_sheet import run as gs_run
from connectors.odoo_api import odoo_run

def main():
    print("Pipeline started")
    csv_run()
    gs_run()
    odoo_run()
    print("Pipeline completed")
```

---

## 🔹 `.env`

- Stores sensitive configs

---

## 🔹 `credentials.json`

- Google service account file
- Required for Google Sheets API access

---

## 🔹 `state.json`

- Stores last sync time for Odoo
- Enables incremental load

---

# requirements.txt

Install dependencies:   pip install-r requirements.txt

### Includes:

- `gspread` → Google Sheets
- `oauth2client` → Auth
- `pandas` → CSV handling
- `psycopg2` → PostgreSQL
- `python-dotenv` → Env variables
- `xmlrpc` → Odoo API

---

# How to Run

### Step 1: Activate virtual environment

```
venv\Scripts\activate
```

---

### Step 2: Run pipeline

```
python run_pipeline.py
```

---

# Logging System

Each pipeline generates logs:

- `google_sheet.log`
- `csv_loader.log`
- `odoo_api.log`

---

### Logs Track:

- Pipeline start/end
- Rows processed
- Errors
- DB connection
- Incremental loads

---

# Features Implemented

- Modular connectors
- Reusable DB connection
- Logging system
- Duplicate handling
- Incremental loading (Odoo)
- Config via `.env`
- Pipeline orchestration
- Scheduler-ready

---

# Scheduling

You can schedule pipeline using:

### Windows Task Scheduler

- Runs daily at specific time (e.g., 10 AM)

---

# Future Improvements

- Add Airflow orchestration
- Add API-based connectors (Oracle, external systems)
- Add data validation layer
- Add monitoring dashboard

---

# Final Summary

This project demonstrates:

- Real-world ETL pipeline design
- Multiple data source integration
- Production-ready structure
- Logging + automation
- Scalable architecture
