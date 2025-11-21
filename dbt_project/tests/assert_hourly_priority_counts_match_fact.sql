-- Test: hourly priority counts in the summary mart should equal the count of priority transactions in the fact table
-- Grain: one row per (transaction_date, hour_of_day) where counts don't match

WITH hourly_from_fact AS (
    SELECT 
        transaction_date,
        hour_of_day,
        COUNTIF(is_priority_review = TRUE) AS priority_count_from_fact
    FROM {{ ref('fct_fraud_transactions') }}
    GROUP BY transaction_date, hour_of_day
),

hourly_from_summary AS (
    SELECT 
        transaction_date,
        hour_of_day,
        priority_review_transactions_count AS priority_count_from_summary
    FROM {{ ref('fct_fraud_hourly_summary') }}
)

SELECT 
    fact.transaction_date,
    fact.hour_of_day,
    fact.priority_count_from_fact,
    summary.priority_count_from_summary
FROM hourly_from_fact AS fact
FULL OUTER JOIN hourly_from_summary AS summary
    ON fact.transaction_date = summary.transaction_date
   AND fact.hour_of_day = summary.hour_of_day
WHERE 
    -- Fail if counts don't match or if one side is missing
    COALESCE(fact.priority_count_from_fact, 0) != COALESCE(summary.priority_count_from_summary, 0)
