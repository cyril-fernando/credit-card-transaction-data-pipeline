-- Test: Transaction dates should be within reasonable range (2013-2014 based on dataset)
SELECT 
    transaction_id,
    transaction_date,
    transaction_timestamp
FROM {{ ref('int_transaction_features') }}
WHERE transaction_date < '2013-09-01' 
   OR transaction_date > '2013-09-03'
