-- Staging model: Clean and standardize raw transactions
-- Materializes as view in fraud_detection_dev

{{ config(
    materialized='view',
    tags=['staging']
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'transactions') }}
),

cleaned AS (
    SELECT
        -- Generate unique ID
        ROW_NUMBER() OVER (ORDER BY Time) AS transaction_id,
        
        -- Convert Time to proper timestamp (assuming base date)
        TIMESTAMP_ADD(
            TIMESTAMP('2013-09-01 00:00:00'), 
            INTERVAL CAST(Time AS INT64) SECOND
        ) AS transaction_timestamp,
        
        -- Original time in seconds
        Time AS time_seconds,
        
        -- Anonymized features (V1-V28 from PCA)
        V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
        V11, V12, V13, V14, V15, V16, V17, V18, V19, V20,
        V21, V22, V23, V24, V25, V26, V27, V28,
        
        -- Transaction amount
        Amount AS amount,
        
        -- Fraud indicator (1 = fraud, 0 = legitimate)
        Class AS is_fraud
        
    FROM source
)

SELECT * FROM cleaned
