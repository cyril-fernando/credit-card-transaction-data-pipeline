{{ config(
    materialized='table',
    tags=['marts', 'fraud'],
    description='Hourly summary of transaction and fraud metrics; one row per (transaction_date, hour_of_day).'
) }}

WITH source AS (
    -- Input fact: one row per transaction from the marts layer
    SELECT * FROM {{ ref('fct_fraud_transactions') }}
),

hourly AS (
    SELECT
        -- Grain: all transactions within this transaction_date and hour_of_day
        transaction_date,
        hour_of_day,

        -- Hourly transaction volume and amount
        COUNT(*) AS transactions_count,
        SUM(transaction_amount) AS total_amount,
        AVG(transaction_amount) AS avg_transaction_amount,

        -- Hourly fraud counts and fraud amount
        SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_transactions_count,
        SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END) AS fraud_amount,

        -- Hourly count of 3-sigma outliers and transactions in the highest risk band
        SUM(CASE WHEN is_amount_outlier_3sigma THEN 1 ELSE 0 END) AS outlier_transactions_count,
        SUM(CASE WHEN amount_risk_category = 'Critical' THEN 1 ELSE 0 END) AS critical_amount_transactions_count,

        -- Hourly counts of priority transactions by reason
        SUM(CASE WHEN is_priority_high_value THEN 1 ELSE 0 END) AS priority_high_value_transactions_count,
        SUM(CASE WHEN is_priority_off_peak THEN 1 ELSE 0 END) AS priority_off_peak_transactions_count,

        -- Hourly total of all priority transactions (combined flag)
        SUM(CASE WHEN is_priority_review THEN 1 ELSE 0 END) AS priority_review_transactions_count,

        -- Hourly count of transactions that occurred in off-peak hours
        SUM(CASE WHEN is_off_peak_tx THEN 1 ELSE 0 END) AS off_peak_transactions_count

    FROM source
    GROUP BY transaction_date, hour_of_day
),

final AS (
    SELECT
        transaction_date,
        hour_of_day,

        -- Core hourly volume metrics
        transactions_count,
        ROUND(total_amount, 2) AS total_amount,
        ROUND(avg_transaction_amount, 2) AS avg_transaction_amount,

        -- Hourly fraud counts, fraud amount, and fraud rate
        fraud_transactions_count,
        ROUND(fraud_amount, 2) AS fraud_amount,
        ROUND(SAFE_DIVIDE(fraud_transactions_count, transactions_count), 4) AS fraud_rate,

        -- Hourly anomaly and priority metrics
        outlier_transactions_count,
        critical_amount_transactions_count,
        priority_high_value_transactions_count,
        priority_off_peak_transactions_count,
        priority_review_transactions_count,
        ROUND(SAFE_DIVIDE(priority_review_transactions_count, transactions_count), 4) AS priority_review_rate,

        -- Hourly count of off-peak transactions
        off_peak_transactions_count

    FROM hourly
)

-- Final mart: one row per (transaction_date, hour_of_day) with hourly fraud and anomaly KPIs
SELECT *
FROM final
