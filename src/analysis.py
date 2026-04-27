from __future__ import annotations

import sqlite3
import json

import pandas as pd

from src.config import CLEAN_CSV_PATH, DB_PATH, METADATA_PATH


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(CLEAN_CSV_PATH)


def get_build_metadata() -> dict[str, str]:
    if not METADATA_PATH.exists():
        return {"data_source": "unknown"}
    return json.loads(METADATA_PATH.read_text())


def query_sql(query: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def get_kpis() -> dict[str, float]:
    df = load_dataset()
    return {
        "customers": int(df["customerID"].nunique()),
        "churn_rate": float(round(df["churn_flag"].mean() * 100, 2)),
        "avg_monthly_revenue": float(round(df["monthly_revenue"].mean(), 2)),
        "revenue_at_risk": float(round(df["revenue_at_risk"].sum(), 2)),
    }


def churn_by_segment(column: str) -> pd.DataFrame:
    safe_columns = {
        "Contract",
        "InternetService",
        "PaymentMethod",
        "tenure_band",
        "charge_band",
        "PaperlessBilling",
    }
    if column not in safe_columns:
        raise ValueError(f"Unsupported segment: {column}")

    query = f"""
        SELECT
            {column} AS segment,
            COUNT(*) AS customers,
            ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
            ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue,
            ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
        FROM subscription_customers
        GROUP BY {column}
        ORDER BY churn_rate DESC, customers DESC
    """
    return query_sql(query)


def cohort_summary() -> pd.DataFrame:
    query = """
        SELECT
            cohort_month,
            COUNT(*) AS customers,
            ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
            ROUND(AVG(tenure), 1) AS avg_tenure_months,
            ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue
        FROM subscription_customers
        GROUP BY cohort_month
        ORDER BY
            CASE cohort_month
                WHEN 'Recent' THEN 1
                WHEN 'Developing' THEN 2
                WHEN 'Established' THEN 3
                ELSE 4
            END
    """
    return query_sql(query)


def churn_heatmap() -> pd.DataFrame:
    query = """
        SELECT
            tenure_band,
            charge_band,
            COUNT(*) AS customers,
            ROUND(AVG(churn_flag) * 100, 2) AS churn_rate
        FROM subscription_customers
        GROUP BY tenure_band, charge_band
    """
    df = query_sql(query)

    tenure_order = ["0-12m", "13-24m", "25-48m", "49-72m"]
    charge_order = ["Low", "Mid", "High", "Premium"]

    df["tenure_band"] = pd.Categorical(df["tenure_band"], categories=tenure_order, ordered=True)
    df["charge_band"] = pd.Categorical(df["charge_band"], categories=charge_order, ordered=True)
    return df.sort_values(["tenure_band", "charge_band"])


def top_revenue_risk(limit: int = 10) -> pd.DataFrame:
    query = f"""
        SELECT
            customerID,
            Contract,
            InternetService,
            PaymentMethod,
            tenure,
            ROUND(monthly_revenue, 2) AS monthly_revenue,
            ROUND(revenue_at_risk, 2) AS revenue_at_risk
        FROM subscription_customers
        WHERE churn_flag = 1
        ORDER BY revenue_at_risk DESC, tenure ASC
        LIMIT {int(limit)}
    """
    return query_sql(query)


CODE_SNIPPETS = {
    "python_feature_engineering": """
cleaned["churn_flag"] = cleaned["Churn"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
cleaned["monthly_revenue"] = cleaned["MonthlyCharges"]
cleaned["annualized_revenue"] = cleaned["MonthlyCharges"] * 12
cleaned["revenue_at_risk"] = cleaned["monthly_revenue"] * cleaned["churn_flag"]
    """.strip(),
    "sql_segment_analysis": """
SELECT
    Contract AS segment,
    COUNT(*) AS customers,
    ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
    ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
FROM subscription_customers
GROUP BY Contract
ORDER BY churn_rate DESC;
    """.strip(),
}
