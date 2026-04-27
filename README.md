# Subscription Churn Intelligence Dashboard

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
