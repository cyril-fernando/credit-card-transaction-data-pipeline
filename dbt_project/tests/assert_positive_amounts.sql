-- Test: All transaction amounts must be positive
SELECT 
    transaction_id,
    amount
FROM {{ ref('stg_raw_transactions') }}
WHERE amount < 0
