-- Highest-risk segment in each contract type using a window function
WITH segment_risk AS (
    SELECT
        Contract,
        InternetService,
        COUNT(*) AS customers,
        ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
        ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
    FROM subscription_customers
    GROUP BY Contract, InternetService
),
ranked_segments AS (
    SELECT
        Contract,
        InternetService,
        customers,
        churn_rate,
        revenue_at_risk,
        ROW_NUMBER() OVER (
            PARTITION BY Contract
            ORDER BY churn_rate DESC, revenue_at_risk DESC
        ) AS risk_rank
    FROM segment_risk
)
SELECT
    Contract,
    InternetService,
    customers,
    churn_rate,
    revenue_at_risk,
    risk_rank
FROM ranked_segments
WHERE risk_rank = 1
ORDER BY churn_rate DESC, revenue_at_risk DESC;

-- KPI snapshot
SELECT
    COUNT(*) AS customers,
    ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
    ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue,
    ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
FROM subscription_customers;

-- Churn by contract
SELECT
    Contract,
    COUNT(*) AS customers,
    ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
    ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue
FROM subscription_customers
GROUP BY Contract
ORDER BY churn_rate DESC;

-- Churn by payment method
SELECT
    PaymentMethod,
    COUNT(*) AS customers,
    ROUND(AVG(churn_flag) * 100, 2) AS churn_rate,
    ROUND(SUM(revenue_at_risk), 2) AS revenue_at_risk
FROM subscription_customers
GROUP BY PaymentMethod
ORDER BY churn_rate DESC;


