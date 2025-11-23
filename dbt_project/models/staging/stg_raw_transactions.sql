{{ config(
  materialized='view',
  tags=['staging']
) }}

WITH source AS (
    SELECT * FROM {{ source('kaggle_raw', 'transactions') }}  -- Raw Kaggle transactions source
),

renamed AS (
    SELECT
        -- Generate deterministic unique identifier for each transaction
        {{ dbt_utils.generate_surrogate_key([
            'Time',
            'Amount',
            'V1', 'V2', 'V3', 'V4', 'V5', 'V6',
            'V7', 'V8', 'V9', 'V10',
            'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
            'V21','V22','V23','V24','V25','V26','V27','V28',
            'Class'
        ]) }} AS transaction_id,

        -- Convert relative Time (seconds since start) to absolute timestamp anchored on 2013-09-01 midnight
        {{ dbt.dateadd('second', 'cast(Time as INT64)', "'2013-09-01 00:00:00'") }} AS transaction_timestamp,

        -- Retain original Time as time_seconds for velocity calculations
        Time AS time_seconds,

        -- Include PCA anonymized features dynamically for maintainability
        {% for i in range(1, 29) %}
        V{{ i }}{{ "," if not loop.last }}
        {% endfor %},

        -- Transaction amount with clear naming
        Amount AS amount,

        -- Fraud indicator with clear naming
        Class AS is_fraud

    FROM source
)

SELECT * FROM renamed
