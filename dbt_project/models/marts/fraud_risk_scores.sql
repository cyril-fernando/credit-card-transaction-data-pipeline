{{ config(
    materialized='table',
    partition_by={
        'field': 'transaction_date',
        'data_type': 'date',
        'granularity': 'day'
    },
    cluster_by=['is_fraud', 'hour_of_day'],
    tags=['gold']
) }}

WITH features AS (
    -- Pull from intermediate layer
    SELECT * FROM {{ ref('int_transaction_features') }}
),

final AS (
    SELECT
        -- Keys and timestamps
        transaction_id,
        transaction_date,
        transaction_timestamp,
        hour_of_day,
        day_of_week,
        
        -- Amount features
        amount,
        amount_z,
        amount_log,
        
        -- Select key PCA features (keep top 10 for now)
        V1, V2, V3, V4, V5,
        V6, V7, V8, V9, V10,
        
        -- Target variable
        is_fraud,
        
        -- Add simple risk categories
        CASE 
            WHEN amount_z > 3 THEN 'High Risk'
            WHEN amount_z > 2 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS amount_risk_category
        
    FROM features
)

SELECT * FROM final
