{{ config(
    materialized='view',
    tags=['intermediate']
) }}

WITH base AS (
    -- Pull from staging
    SELECT * FROM {{ ref('stg_raw_transactions') }}
),

features AS (
    SELECT
        -- Primary keys
        transaction_id,
        transaction_timestamp,
        time_seconds,
        
        -- Date/time features (for grouping and patterns)
        DATE(transaction_timestamp) AS transaction_date,
        EXTRACT(HOUR FROM transaction_timestamp) AS hour_of_day,
        EXTRACT(DAYOFWEEK FROM transaction_timestamp) AS day_of_week,  -- 1=Sunday, 7=Saturday
        
        -- Amount features
        amount,
        -- Standardized amount (z-score for anomaly detection)
        SAFE_DIVIDE(
            amount - AVG(amount) OVER (),
            NULLIF(STDDEV(amount) OVER (), 0)
        ) AS amount_z,
        
        -- Log transform (common for skewed financial data)
        SAFE.LN(amount + 1) AS amount_log,
        
        -- Keep all PCA features for ML models later
        V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
        V11, V12, V13, V14, V15, V16, V17, V18, V19, V20,
        V21, V22, V23, V24, V25, V26, V27, V28,
        
        -- Target variable
        is_fraud
        
    FROM base
)

SELECT * FROM features
