-- 1. Find all schemes a user is enrolled in
SELECT 
    u.name AS user_name, 
    s.name AS scheme_name
FROM users u
JOIN wallet_logs w ON u.id = w.user_id
JOIN schemes s ON s.id = w.scheme_id
ORDER BY u.name;

-- 2. Show total benefits received by each user
SELECT 
    u.name, 
    SUM(w.amount) AS total_benefits
FROM users u
JOIN wallet_logs w ON u.id = w.user_id
GROUP BY u.name;

-- 3. Show all users who uploaded Aadhaar card
SELECT 
    u.name, 
    d.doc_type
FROM users u
JOIN documents d ON u.id = d.user_id
WHERE d.doc_type = 'Aadhaar Card';

-- 4. Show top 3 users with highest wallet amounts
SELECT 
    u.name, 
    SUM(w.amount) AS total_amount
FROM users u
JOIN wallet_logs w ON u.id = w.user_id
GROUP BY u.name
ORDER BY total_amount DESC
LIMIT 3;
