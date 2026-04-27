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

