
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Configurazione della pagina
st.set_page_config(
    page_title="Olist Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Olist E-commerce Analytics")
st.caption("Dashboard interattiva collegata a PostgreSQL")

# Carica le credenziali dal file .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Connessione al database
connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(connection_url)


@st.cache_data(ttl=300)
def load_data():
    """Legge dal database e memorizza i risultati per 5 minuti."""

    with engine.connect() as connection:
        kpis = pd.read_sql(
            "SELECT * FROM vw_order_kpis",
            connection,
        )

        monthly = pd.read_sql(
            """
            SELECT *
            FROM vw_monthly_revenue
            ORDER BY month
            """,
            connection,
        )

        reviews = pd.read_sql(
            """
            SELECT *
            FROM vw_review_distribution
            ORDER BY review_score
            """,
            connection,
        )

        payments = pd.read_sql(
            """
            SELECT
                payment_type,
                COUNT(*) AS payment_records,
                ROUND(SUM(payment_value)::numeric, 2)
                    AS total_payment_value
            FROM order_payments
            GROUP BY payment_type
            ORDER BY total_payment_value DESC
            """,
            connection,
        )

        
        delivery_kpis = pd.read_sql(
            """
            SELECT
                COUNT(*) AS analyzed_orders,
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
                ) AS late_percentage,
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
              AND order_estimated_delivery_date IS NOT NULL
            """,
            connection,
        )

        delivery_reviews = pd.read_sql(
            """
            WITH delivery_status AS (
                SELECT
                    o.order_id,
                    CASE
                        WHEN o.order_delivered_customer_date
                             > o.order_estimated_delivery_date
                            THEN 'In ritardo'
                        ELSE 'Puntuale o in anticipo'
                    END AS delivery_group
                FROM orders o
                WHERE o.order_status = 'delivered'
                  AND o.order_delivered_customer_date IS NOT NULL
                  AND o.order_estimated_delivery_date IS NOT NULL
            )
            SELECT
                d.delivery_group,
                COUNT(*) AS review_count,
                ROUND(AVG(r.review_score)::numeric, 2)
                    AS avg_review_score,
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
            ORDER BY d.delivery_group
            """,
            connection,
        )

    return (
    kpis,
    monthly,
    reviews,
    payments,
    delivery_kpis,
    delivery_reviews,
)


try:
    (
    kpis,
    monthly,
    reviews,
    payments,
    delivery_kpis,
    delivery_reviews,
) = load_data()

    # KPI principali
    kpi = kpis.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Ordini totali",
        f"{int(kpi['total_orders']):,}".replace(",", "."),
    )

    col2.metric(
        "Ordini consegnati",
        f"{int(kpi['delivered_orders']):,}".replace(",", "."),
    )

    col3.metric(
        "Tasso di consegna",
        f"{float(kpi['delivered_rate_pct']):.2f}%",
    )

    st.divider()

    
    # Analisi dei ritardi di consegna
    st.subheader("🚚 Puntualità delle consegne")

    delivery = delivery_kpis.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Ordini consegnati in ritardo",
        f"{int(delivery['late_orders']):,}".replace(",", "."),
    )

    col2.metric(
        "Ordini in ritardo (%)",
        f"{float(delivery['late_percentage']):.2f}%",
    )

    col3.metric(
        "Ritardo medio",
        f"{float(delivery['avg_days_late']):.2f} giorni",
    )

    st.caption(
        f"Analisi basata su {int(delivery['analyzed_orders']):,} "
        "ordini consegnati con entrambe le date disponibili."
    )

    st.divider()

    st.subheader("⭐ Puntualità e soddisfazione dei clienti")

    left, right = st.columns(2)

    with left:
        fig_delivery_score = px.bar(
            delivery_reviews,
            x="delivery_group",
            y="avg_review_score",
            text="avg_review_score",
            labels={
                "delivery_group": "Stato della consegna",
                "avg_review_score": "Punteggio medio",
            },
            title="Punteggio medio delle recensioni",
        )

        fig_delivery_score.update_traces(
            texttemplate="%{text:.2f}/5",
            textposition="outside",
        )

        fig_delivery_score.update_yaxes(
            range=[0, 5],
            title="Punteggio medio (su 5)",
        )

        st.plotly_chart(
            fig_delivery_score,
            use_container_width=True,
        )

    with right:
        fig_negative_reviews = px.bar(
            delivery_reviews,
            x="delivery_group",
            y="negative_review_percentage",
            text="negative_review_percentage",
            labels={
                "delivery_group": "Stato della consegna",
                "negative_review_percentage": "Recensioni negative (%)",
            },
            title="Recensioni negative (1–2 stelle)",
        )

        fig_negative_reviews.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        fig_negative_reviews.update_yaxes(
            range=[0, 100],
            title="Recensioni negative (%)",
        )

        st.plotly_chart(
            fig_negative_reviews,
            use_container_width=True,
        )

    st.caption(
        "I risultati mostrano un'associazione tra ritardi e recensioni "
        "negative, ma non dimostrano un rapporto causale."
    )

    st.divider()

    # Filtro per periodo
    monthly["month"] = pd.to_datetime(monthly["month"])

    min_month = monthly["month"].min().to_period("M")
    max_month = monthly["month"].max().to_period("M")

    available_months = pd.period_range(
        min_month,
        max_month,
        freq="M",
    )

    selected_months = st.select_slider(
        "Periodo da analizzare",
        options=list(available_months),
        value=(min_month, max_month),
        format_func=lambda month: month.strftime("%m/%Y"),
    )

    start_month, end_month = selected_months

    filtered_monthly = monthly[
        monthly["month"].dt.to_period("M").between(
            start_month,
            end_month,
        )
    ].copy()

    # Grafico del fatturato degli articoli
    st.subheader("Andamento mensile dei ricavi degli articoli")

    fig_revenue = px.line(
        filtered_monthly,
        x="month",
        y="product_revenue",
        markers=True,
        labels={
            "month": "Mese",
            "product_revenue": "Valore degli articoli",
        },
    )

    fig_revenue.update_layout(
        xaxis_title="Mese",
        yaxis_title="Valore (€)",
        hovermode="x unified",
    )

    st.plotly_chart(fig_revenue, use_container_width=True)

    st.caption(
        "Il valore considera il prezzo degli articoli degli ordini "
        "consegnati, senza le spese di spedizione. "
        "Non rappresenta necessariamente il fatturato contabile."
    )

    # Distribuzione delle recensioni
    left, right = st.columns(2)

    with left:
        st.subheader("Distribuzione delle recensioni")

        fig_reviews = px.bar(
            reviews,
            x="review_score",
            y="total_reviews",
            text="percentage",
            labels={
                "review_score": "Punteggio",
                "total_reviews": "Numero di recensioni",
                "percentage": "Percentuale",
            },
        )

        fig_reviews.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        st.plotly_chart(
            fig_reviews,
            use_container_width=True,
        )

    # Metodi di pagamento
    with right:
        st.subheader("Metodi di pagamento")

        fig_payments = px.bar(
            payments,
            x="payment_type",
            y="total_payment_value",
            labels={
                "payment_type": "Metodo",
                "total_payment_value": "Valore dei pagamenti (€)",
            },
        )

        st.plotly_chart(
            fig_payments,
            use_container_width=True,
        )

    # Tabelle dei dati
    with st.expander("Visualizza dati mensili"):
        st.dataframe(
            filtered_monthly,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Visualizza dati dei pagamenti"):
        st.dataframe(
            payments,
            use_container_width=True,
            hide_index=True,
        )

    st.success("Dashboard caricata correttamente.")

except Exception as error:
    st.error(f"Errore durante il caricamento dei dati: {error}")
    st.info(
        "Verifica che PostgreSQL sia attivo, che il file .env "
        "sia corretto e che le tre viste SQL esistano."
    )