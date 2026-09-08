-- Query 1: Top 5 funds by AUM

SELECT
    amfi_code,
    scheme_name,
    fund_house,
    category,
    aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;


-- Query 2: Average NAV per month

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS average_nav
FROM fact_nav n
JOIN dim_date d
    ON n.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- Query 3: SIP YoY growth

SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;


-- Query 4: Transactions by state

SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_transaction_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_transaction_amount DESC;


-- Query 5: Funds with expense ratio below 1%

SELECT
    amfi_code,
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct ASC;


-- Query 6: Top 10 funds by 1-year return

SELECT
    amfi_code,
    scheme_name,
    fund_house,
    category,
    return_1yr_pct
FROM fact_performance
ORDER BY return_1yr_pct DESC
LIMIT 10;


-- Query 7: Category-wise average 3-year return

SELECT
    category,
    COUNT(*) AS fund_count,
    ROUND(AVG(return_3yr_pct), 2) AS average_return_3yr_pct
FROM fact_performance
GROUP BY category
ORDER BY average_return_3yr_pct DESC;


-- Query 8: Transaction distribution by transaction type

SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS average_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;


-- Query 9: Portfolio holdings by sector

SELECT
    sector,
    COUNT(*) AS holding_count,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr,
    ROUND(AVG(weight_pct), 2) AS average_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_market_value_cr DESC;


-- Query 10: Fund-house AUM ranking

SELECT
    fund_house,
    ROUND(SUM(aum_crore), 2) AS total_aum_crore,
    SUM(num_schemes) AS total_schemes
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_crore DESC;