{{ config(
    materialized='table',
    tags=['marts', 'fraud'],
    description='Fact table of credit card transactions for fraud analytics and ML; one row per transaction with engineered time, velocity, and amount anomaly features.',
    partition_by={
        'field': 'transaction_date',
        'data_type': 'date',
        'granularity': 'day'
    },
    cluster_by=['is_fraud', 'amount_risk_category']
) }}

WITH source AS (
    -- One row per cleaned, deduplicated transaction from the intermediate layer
    SELECT * FROM {{ ref('int_transaction_features') }}
),

enriched AS (
    SELECT 
        -- Transaction grain: one row per transaction
        transaction_id,
        transaction_timestamp,
        transaction_date,

        -- Time features for time-of-day and day-of-week analysis
        hour_of_day,
        day_of_week,
        hour_sin,
        hour_cos,

        -- Velocity: seconds since previous transaction
        time_since_prev_tx,
        CASE
            WHEN time_since_prev_tx <= 1 THEN TRUE
            ELSE FALSE
        END AS velocity_flag,

        -- Amount features: raw amount, log transform, and z-score
        amount AS transaction_amount,
        amount_log,
        amount_z_score,

        -- 3-sigma outlier flag based on amount z-score
        CASE
            WHEN ABS(amount_z_score) >= 3.0 THEN TRUE
            ELSE FALSE
        END AS is_amount_outlier_3sigma,

        -- Sigma-based risk tiers derived from |amount_z_score|
        CASE
            WHEN ABS(amount_z_score) >= 3.0 THEN 'Critical'  -- |z| >= 3
            WHEN ABS(amount_z_score) >= 2.0 THEN 'High'      -- 2 <= |z| < 3
            WHEN ABS(amount_z_score) >= 1.0 THEN 'Medium'    -- 1 <= |z| < 2
            ELSE 'Normal'                                    -- |z| < 1
        END AS amount_risk_category,

        -- Priority flags based on anomaly score, amount, and time-of-day

        -- High-value priority: 3-sigma anomaly and in the top 1% of amounts for the transaction_date
        CASE 
            WHEN ABS(amount_z_score) >= 3.0 
             AND PERCENT_RANK() OVER (
                    PARTITION BY transaction_date
                    ORDER BY amount
                 ) >= 0.99
            THEN TRUE 
            ELSE FALSE 
        END AS is_priority_high_value,

        -- Off-peak priority: 3-sigma anomaly that occurs during off-peak hours (18:00–05:59)
        CASE 
            WHEN ABS(amount_z_score) >= 3.0 
             AND (
                    hour_of_day BETWEEN 18 AND 23
                 OR hour_of_day BETWEEN 0 AND 5
                 )
            THEN TRUE 
            ELSE FALSE 
        END AS is_priority_off_peak,

        -- Combined priority flag for downstream alerting and aggregation
        CASE 
            WHEN (
                    ABS(amount_z_score) >= 3.0 
                    AND PERCENT_RANK() OVER (
                            PARTITION BY transaction_date
                            ORDER BY amount
                        ) >= 0.99
                 )
              OR (
                    ABS(amount_z_score) >= 3.0 
                    AND (
                           hour_of_day BETWEEN 18 AND 23
                        OR hour_of_day BETWEEN 0 AND 5
                        )
                 )
            THEN TRUE 
            ELSE FALSE 
        END AS is_priority_review,

        -- Off-peak time-of-day flags
        CASE 
            WHEN hour_of_day BETWEEN 18 AND 23 THEN TRUE 
            ELSE FALSE 
        END AS is_evening_tx,          -- 18:00–23:59

        CASE 
            WHEN hour_of_day BETWEEN 0 AND 5 THEN TRUE 
            ELSE FALSE 
        END AS is_late_night_tx,       -- 00:00–05:59

        CASE 
            WHEN hour_of_day BETWEEN 18 AND 23 
               OR hour_of_day BETWEEN 0 AND 5 THEN TRUE 
            ELSE FALSE 
        END AS is_off_peak_tx,         -- 18:00–05:59 combined off-hours

        -- Fraud label
        is_fraud,

        -- PCA/anonymized features for ML use
        V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
        V11, V12, V13, V14, V15, V16, V17, V18, V19, V20,
        V21, V22, V23, V24, V25, V26, V27, V28

    FROM source
)

-- Final fact table output: one row per transaction
SELECT *
FROM enriched
