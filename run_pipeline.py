# from connectors.google_sheet import run as google_sheet_run
from connectors.csv_loader import run as csv_run
# from connectors.odoo_api import odoo_run

def main():

    print("Pipeline started")

    # google_sheet_run()
    csv_run()
    # odoo_run()

    print("Pipeline finished")

if __name__ == "__main__":
    main()