from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "subscription_analytics.db"
RAW_CSV_PATH = RAW_DIR / "telco_churn.csv"
CLEAN_CSV_PATH = PROCESSED_DIR / "subscription_customers.csv"
METADATA_PATH = PROCESSED_DIR / "build_metadata.json"
PUBLIC_DATA_URL = (
    "https://raw.githubusercontent.com/Nas-virat/"
    "Telco-Customer-Churn/main/Telco-Customer-Churn.csv"
)
