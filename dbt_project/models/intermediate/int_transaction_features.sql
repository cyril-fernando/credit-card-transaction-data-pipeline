{{ config(
    materialized='view',
    tags=['intermediate'],
    description='Enriched transaction features including velocity, cyclical time encoding, and statistical amount normalization.'
) }}

WITH base AS (
    -- Import staging data (may contain raw duplicates)
    SELECT * FROM {{ ref("stg_raw_transactions") }}
),

-- =================================================================
-- GROUP 1: TIME & VELOCITY LOGIC
-- Goal: Capture temporal patterns (hour/day) and system-level velocity
-- =================================================================
time_features AS (
    SELECT
        -- 1. ID & Timestamp
        transaction_id,
        transaction_timestamp,
        amount,
        time_seconds,

        -- 2. Calendar date (for daily aggregations / partitioning later)
        DATE(transaction_timestamp) AS transaction_date,

        -- 3. Velocity feature (system-level)
        -- Seconds elapsed since previous transaction in the dataset
        -- COALESCE to 0 so we avoid a single NULL on the very first row
        COALESCE(
            TIMESTAMP_DIFF(
                transaction_timestamp,
                LAG(transaction_timestamp) OVER (ORDER BY transaction_timestamp),
                SECOND
            ),
            0
        ) AS time_since_prev_tx,

        -- 4. Human-readable time
        EXTRACT(HOUR FROM transaction_timestamp) AS hour_of_day,
        EXTRACT(DAYOFWEEK FROM transaction_timestamp) AS day_of_week, -- 1=Sun, 7=Sat

        -- 5. Cyclical time encoding (for ML)
        -- Maps hour of day onto the unit circle so 23:00 and 00:00 are close
        SIN(2 * ACOS(-1) * EXTRACT(HOUR FROM transaction_timestamp) / 24) AS hour_sin,
        COS(2 * ACOS(-1) * EXTRACT(HOUR FROM transaction_timestamp) / 24) AS hour_cos,

        -- 6. Passthrough remaining columns (V1–V28, is_fraud, etc.)
        * EXCEPT (transaction_id, transaction_timestamp, amount, time_seconds)
    FROM base
),

-- =================================================================
-- GROUP 2: MONEY LOGIC
-- Goal: Normalize skewed amount distributions for analytics and ML
-- =================================================================
money_features AS (
    SELECT
        -- Core identifiers and time features
        transaction_id,
        transaction_timestamp,
        time_seconds,
        transaction_date,
        time_since_prev_tx,
        hour_of_day,
        day_of_week,
        hour_sin,
        hour_cos,

        -- Raw amount
        amount,

        -- Log(amount + 1): compresses large values, safe for zero amounts
        SAFE.LN(amount + 1) AS amount_log,

        -- Global Z-score: (amount - mean) / stddev
        SAFE_DIVIDE(
            amount - AVG(amount) OVER (),
            NULLIF(STDDEV(amount) OVER (), 0)
        ) AS amount_z_score,

        -- Passthrough PCA features and label
        * EXCEPT (
            transaction_id,
            transaction_timestamp,
            time_seconds,
            transaction_date,
            time_since_prev_tx,
            hour_of_day,
            day_of_week,
            hour_sin,
            hour_cos,
            amount
        )
    FROM time_features
),

-- =================================================================
-- GROUP 3: DEDUPLICATION
-- Goal: Enforce one row per transaction_id at the intermediate grain
-- =================================================================
deduped AS (
    SELECT *
    FROM (
        SELECT
            money_features.*,
            ROW_NUMBER() OVER (
                PARTITION BY transaction_id
                ORDER BY transaction_timestamp
            ) AS _row_num
        FROM money_features
    )
    WHERE _row_num = 1
)

-- Final Output (drop helper column)
SELECT * EXCEPT (_row_num)
FROM deduped
