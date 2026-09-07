-- Day 1 SQL validation examples
-- Run after loading CSVs into a SQL database.

-- 1. Count fund master schemes
SELECT COUNT(*) AS scheme_count FROM fund_master;

-- 2. Unique fund houses
SELECT DISTINCT fund_house
FROM fund_master
ORDER BY fund_house;

-- 3. Risk categories
SELECT risk_category, COUNT(*) AS schemes
FROM fund_master
GROUP BY risk_category
ORDER BY schemes DESC;

-- 4. Check AMFI codes with no NAV history
SELECT f.amfi_code
FROM fund_master f
LEFT JOIN nav_history n ON n.amfi_code = f.amfi_code
WHERE n.amfi_code IS NULL;
