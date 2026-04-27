# Subscription Churn Intelligence Dashboard

A portfolio project that demonstrates how to use Python, SQL, NumPy, pandas, and Streamlit to analyze subscription customer behavior and churn.

## Why this project works for a portfolio

- Shows practical analytics work on a business problem recruiters immediately understand
- Combines Python data wrangling, SQL querying, KPI design, and interactive dashboarding
- Includes code snippets inside the app so viewers can see implementation details
- Uses a public churn dataset when available and falls back to a reproducible synthetic dataset so the app still runs end to end

## Project concept

The dashboard is framed as a B2C subscription business health review. It helps answer:

- Which customer segments churn the most?
- How do contract type, monthly charges, and tenure relate to churn?
- What does revenue at risk look like?
- How does churn vary by customer cohort?

## Stack

- Python
- pandas
- NumPy
- SQLite
- Streamlit
- Plotly

## Project structure

```text
app/
  app.py
data/
  raw/
  processed/
sql/
  analysis_queries.sql
src/
  analysis.py
  config.py
  data_pipeline.py
```

## How to run locally

1. Create a virtual environment.
2. Install dependencies.
3. Build the dataset.
4. Run the Streamlit app.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.data_pipeline
streamlit run app/app.py
```

## Data source

Primary target:

- Public IBM-style telco churn CSV mirrored on GitHub:
  `https://raw.githubusercontent.com/Nas-virat/Telco-Customer-Churn/main/Telco-Customer-Churn.csv`

Fallback:

- A synthetic subscription dataset generated locally with NumPy for reproducible demos if download is unavailable.

## Portfolio talking points

- Cleaned and standardized messy raw billing fields
- Built SQL-ready fact table in SQLite
- Engineered retention and revenue-risk features
- Added executive KPIs and segment-level drilldowns in Streamlit
- Embedded real code snippets so portfolio visitors can inspect implementation style

## Next steps

- Add predictive churn scoring
- Add A/B style retention intervention simulator
- Deploy to Streamlit Community Cloud and link it from GitHub Pages

# Subscription_Churn_Dashboard
