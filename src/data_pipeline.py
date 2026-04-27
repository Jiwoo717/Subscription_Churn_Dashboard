from __future__ import annotations

import json
import sqlite3
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
import pandas as pd

from src.config import CLEAN_CSV_PATH, DB_PATH, METADATA_PATH, PROCESSED_DIR, PUBLIC_DATA_URL, RAW_CSV_PATH, RAW_DIR


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def download_public_dataset() -> bool:
    if RAW_CSV_PATH.exists():
        return True

    try:
        with urlopen(PUBLIC_DATA_URL, timeout=8) as response:
            RAW_CSV_PATH.write_bytes(response.read())
        return True
    except URLError:
        return False


def generate_synthetic_dataset(rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 73, rows)
    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"],
        size=rows,
        p=[0.56, 0.23, 0.21],
    )
    internet_service = rng.choice(
        ["Fiber optic", "DSL", "No"],
        size=rows,
        p=[0.46, 0.36, 0.18],
    )
    payment_method = rng.choice(
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
        size=rows,
    )
    senior = rng.choice([0, 1], size=rows, p=[0.84, 0.16])
    partner = rng.choice(["Yes", "No"], size=rows, p=[0.5, 0.5])
    dependents = rng.choice(["Yes", "No"], size=rows, p=[0.32, 0.68])
    paperless = rng.choice(["Yes", "No"], size=rows, p=[0.62, 0.38])
    phone_service = rng.choice(["Yes", "No"], size=rows, p=[0.9, 0.1])

    base_charge = rng.normal(70, 22, rows).clip(18, 140)
    monthly_charges = np.where(contract == "Two year", base_charge - 8, base_charge)
    monthly_charges = np.where(internet_service == "No", monthly_charges - 28, monthly_charges)
    monthly_charges = np.round(monthly_charges.clip(18, 135), 2)
    total_charges = np.round(monthly_charges * tenure + rng.normal(0, 45, rows).clip(-100, 100), 2)
    total_charges = np.where(total_charges < monthly_charges, monthly_charges, total_charges)

    churn_score = (
        0.22
        + (contract == "Month-to-month") * 0.24
        + (internet_service == "Fiber optic") * 0.09
        + (payment_method == "Electronic check") * 0.08
        + (paperless == "Yes") * 0.03
        + (tenure < 12) * 0.16
        + (monthly_charges > 85) * 0.08
        + senior * 0.02
        - (contract == "Two year") * 0.14
        - (tenure > 36) * 0.12
    )
    churn_probability = np.clip(churn_score, 0.03, 0.9)
    churn = np.where(rng.random(rows) < churn_probability, "Yes", "No")

    df = pd.DataFrame(
        {
            "customerID": [f"CUST-{100000 + idx}" for idx in range(rows)],
            "gender": rng.choice(["Male", "Female"], size=rows),
            "SeniorCitizen": senior,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": tenure,
            "PhoneService": phone_service,
            "InternetService": internet_service,
            "Contract": contract,
            "PaperlessBilling": paperless,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges,
            "Churn": churn,
        }
    )
    return df


def load_raw_dataset() -> pd.DataFrame:
    if download_public_dataset():
        return pd.read_csv(RAW_CSV_PATH)
    return generate_synthetic_dataset()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [column.strip() for column in cleaned.columns]

    if "customerID" not in cleaned.columns and "CustomerID" in cleaned.columns:
        cleaned = cleaned.rename(columns={"CustomerID": "customerID"})

    cleaned["TotalCharges"] = pd.to_numeric(cleaned["TotalCharges"], errors="coerce")
    cleaned["MonthlyCharges"] = pd.to_numeric(cleaned["MonthlyCharges"], errors="coerce")
    cleaned["tenure"] = pd.to_numeric(cleaned["tenure"], errors="coerce")
    cleaned["TotalCharges"] = cleaned["TotalCharges"].fillna(cleaned["MonthlyCharges"] * cleaned["tenure"])

    cleaned["churn_flag"] = cleaned["Churn"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    cleaned["monthly_revenue"] = cleaned["MonthlyCharges"]
    cleaned["annualized_revenue"] = cleaned["MonthlyCharges"] * 12
    cleaned["revenue_at_risk"] = cleaned["monthly_revenue"] * cleaned["churn_flag"]

    cleaned["tenure_band"] = pd.cut(
        cleaned["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12m", "13-24m", "25-48m", "49-72m"],
        include_lowest=True,
    )
    cleaned["charge_band"] = pd.qcut(
        cleaned["MonthlyCharges"],
        q=4,
        labels=["Low", "Mid", "High", "Premium"],
        duplicates="drop",
    )
    cleaned["cohort_month"] = np.where(
        cleaned["tenure"] <= 12,
        "Recent",
        np.where(cleaned["tenure"] <= 24, "Developing", np.where(cleaned["tenure"] <= 48, "Established", "Loyal")),
    )

    return cleaned


def write_outputs(df: pd.DataFrame, source: str) -> None:
    df.to_csv(CLEAN_CSV_PATH, index=False)

    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql("subscription_customers", connection, if_exists="replace", index=False)

    METADATA_PATH.write_text(json.dumps({"data_source": source}, indent=2))


def main() -> None:
    ensure_directories()
    used_public_data = download_public_dataset()
    raw_df = pd.read_csv(RAW_CSV_PATH) if used_public_data else generate_synthetic_dataset()
    clean_df = clean_dataset(raw_df)
    write_outputs(clean_df, source="public_telco_csv" if used_public_data else "synthetic_fallback")
    print(f"Built dataset with {len(clean_df):,} rows")
    print(f"CSV: {CLEAN_CSV_PATH}")
    print(f"SQLite DB: {DB_PATH}")


if __name__ == "__main__":
    main()
