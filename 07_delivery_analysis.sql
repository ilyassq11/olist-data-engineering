
SELECT
    COUNT(*) AS total_delivered_orders,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date
              > order_estimated_delivery_date
    ) AS late_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_delivered_customer_date
                  > order_estimated_delivery_date
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS late_order_percentage,
    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (
                    order_delivered_customer_date
                    - order_estimated_delivery_date
                )
            ) / 86400.0
        ) FILTER (
            WHERE order_delivered_customer_date
                  > order_estimated_delivery_date
        )::numeric,
        2
    ) AS avg_days_late
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;

/*Le recensioni sono peggiori quando la consegna è in ritardo?  */

WITH delivery_status AS (
    SELECT
        o.order_id,
        CASE
            WHEN o.order_delivered_customer_date
                 > o.order_estimated_delivery_date
                THEN 'Late'
            ELSE 'On time or early'
        END AS delivery_group
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT
    d.delivery_group,
    COUNT(*) AS review_count,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_score,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE r.review_score <= 2
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS negative_review_percentage
FROM delivery_status d
JOIN order_reviews r
    ON d.order_id = r.order_id
GROUP BY d.delivery_group
ORDER BY d.delivery_group;