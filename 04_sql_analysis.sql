
-- 1. KPI generali degli ordini
SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered_orders,
    COUNT(*) FILTER (WHERE order_status = 'canceled') AS canceled_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE order_status = 'delivered')
        / NULLIF(COUNT(*), 0), 2
    ) AS delivered_rate_pct
FROM orders;


-- 2. Fatturato prodotti per mese
-- Somma price degli articoli, escludendo il trasporto
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp)::date AS month,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;


-- 3. Metodi di pagamento
SELECT
    payment_type,
    COUNT(*) AS payment_records,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- 4. Valutazione media delle recensioni
SELECT
    review_score,
    COUNT(*) AS reviews,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
    ) AS percentage
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;