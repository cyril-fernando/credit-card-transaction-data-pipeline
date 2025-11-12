-- Test: Fraud rate should be between 0.1% and 1%
WITH fraud_stats AS (
    SELECT 
        COUNT(*) as total_transactions,
        SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
        (SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as fraud_rate_pct
    FROM {{ ref('fraud_risk_scores') }}
)
SELECT *
FROM fraud_stats
WHERE fraud_rate_pct < 0.1 OR fraud_rate_pct > 1.0
