from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import (
    CODE_SNIPPETS,
    cohort_summary,
    churn_heatmap,
    get_build_metadata,
    get_kpis,
    load_dataset,
    top_revenue_risk,
    churn_by_segment,
)


st.set_page_config(
    page_title="Subscription Churn Intelligence",
    page_icon="📈",
    layout="wide",
)


def load_data() -> pd.DataFrame:
    return load_dataset()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .hero {
            padding: 1.6rem 1.8rem;
            border-radius: 18px;
            background:
                radial-gradient(circle at top left, rgba(176, 68, 44, 0.18), transparent 34%),
                linear-gradient(135deg, #f8f3ea 0%, #e7ddcc 100%);
            border: 1px solid rgba(31, 26, 23, 0.08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.3rem;
        }
        .hero p {
            margin: 0.4rem 0 0;
            font-size: 1rem;
            max-width: 52rem;
        }
        .snippet {
            border-radius: 16px;
            padding: 0.8rem;
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid rgba(31, 26, 23, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    df = load_data()
    kpis = get_kpis()
    metadata = get_build_metadata()

    st.markdown(
        """
        <div class="hero">
            <h1>Subscription Churn Intelligence</h1>
            <p>
                An interactive portfolio project showing how Python, SQL, pandas, NumPy, and Streamlit
                can be used to analyze churn, retention, cohort health, and revenue risk in a subscription business.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Dataset mode: `{metadata['data_source']}`")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Customers", f"{kpis['customers']:,}")
    metric_cols[1].metric("Churn Rate", f"{kpis['churn_rate']:.2f}%")
    metric_cols[2].metric("Avg Monthly Revenue", f"${kpis['avg_monthly_revenue']:,.2f}")
    metric_cols[3].metric("Revenue At Risk", f"${kpis['revenue_at_risk']:,.2f}")

    st.divider()
    left, right = st.columns([1.15, 0.85])

    with left:
        segment = st.selectbox(
            "Segment customers by",
            [
                "Contract",
                "InternetService",
                "PaymentMethod",
                "tenure_band",
                "charge_band",
                "PaperlessBilling",
            ],
        )
        segment_df = churn_by_segment(segment)

        fig_segment = px.bar(
            segment_df,
            x="segment",
            y="churn_rate",
            color="revenue_at_risk",
            text="customers",
            color_continuous_scale="OrRd",
            title=f"Churn Rate by {segment}",
            labels={"segment": segment, "churn_rate": "Churn rate (%)", "revenue_at_risk": "Revenue at risk"},
        )
        fig_segment.update_traces(textposition="outside")
        fig_segment.update_layout(height=440, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_segment, use_container_width=True)

    with right:
        st.subheader("Churn heatmap")
        heatmap_df = churn_heatmap()
        fig_heatmap = px.density_heatmap(
            heatmap_df,
            x="tenure_band",
            y="charge_band",
            z="churn_rate",
            text_auto=".1f",
            color_continuous_scale="OrRd",
            title="Churn Rate by Tenure and Charge Band",
            labels={
                "tenure_band": "Tenure band",
                "charge_band": "Charge band",
                "churn_rate": "Churn rate (%)",
            },
        )
        fig_heatmap.update_layout(height=440, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_heatmap, use_container_width=True)

    bottom_left, bottom_right = st.columns([1, 1])

    with bottom_left:
        cohort_df = cohort_summary()
        fig_cohort = px.line(
            cohort_df,
            x="cohort_month",
            y="churn_rate",
            markers=True,
            title="Churn by Tenure Cohort",
            labels={"cohort_month": "Cohort", "churn_rate": "Churn rate (%)"},
        )
        fig_cohort.update_traces(line_color="#1F1A17", marker_color="#B0442C", line_width=3)
        fig_cohort.update_layout(height=360, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_cohort, use_container_width=True)

    with bottom_right:
        st.subheader("Highest revenue-risk churned customers")
        st.dataframe(top_revenue_risk(12), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Code Spotlight")
    st.caption("These snippets are surfaced intentionally for portfolio viewers who want proof of hands-on SQL and Python work.")

    snippet_left, snippet_right = st.columns(2)
    with snippet_left:
        st.markdown('<div class="snippet">', unsafe_allow_html=True)
        st.code(CODE_SNIPPETS["python_feature_engineering"], language="python")
        st.markdown("</div>", unsafe_allow_html=True)
    with snippet_right:
        st.markdown('<div class="snippet">', unsafe_allow_html=True)
        st.code(CODE_SNIPPETS["sql_segment_analysis"], language="sql")
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Preview cleaned dataset"):
        st.dataframe(df.head(25), use_container_width=True, hide_index=True)

    with st.expander("Portfolio framing"):
        st.markdown(
            """
            - Business question: Which customers are most at risk of churning and what revenue is exposed?
            - Python value: data cleaning, feature engineering, segmentation, and metric creation
            - SQL value: cohort and segment aggregation against a SQLite table
            - Dashboard value: decision-ready views for executives and hiring managers
            """
        )


if __name__ == "__main__":
    main()
