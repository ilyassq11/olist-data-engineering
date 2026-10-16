# Brazilian E-Commerce Data Engineering Project

## Overview

An end-to-end data engineering and analytics project built using the Brazilian E-Commerce Public Dataset by Olist.

The project demonstrates how to ingest raw CSV files, transform and load data into PostgreSQL, validate data quality, analyze business performance with SQL, and communicate findings through an interactive Streamlit dashboard.

## Tech Stack

- **Python** — ETL pipeline, data validation, and automation
- **Pandas** — data ingestion and transformation
- **PostgreSQL** — relational data storage and analysis
- **SQLAlchemy & psycopg2** — database connectivity
- **SQL** — business analysis and database views
- **Streamlit** — interactive dashboard
- **Plotly** — data visualizations
- **python-dotenv** — environment configuration
- **pytest** — automated testing

## Project Architecture

1. **Data ingestion:** Read the original Olist CSV files.
2. **Database setup:** Create the PostgreSQL tables and relationships.
3. **ETL pipeline:** Validate source files, transform date fields, load data in dependency order, and verify row counts.
4. **Data quality:** Execute 17 SQL-based checks for duplicates, referential integrity, invalid values, and other data issues.
5. **SQL analysis:** Analyze orders, payments, reviews, and delivery performance.
6. **Dashboard:** Explore business KPIs and findings through interactive visualizations.

## Key Findings

The delivery analysis identified the following patterns among delivered orders with available delivery dates:

- **8.11%** arrived later than estimated.
- Late-delivered orders had an average review score of **2.57/5**, compared with **4.29/5** for orders delivered on time or early.
- **54.03%** of reviews associated with late deliveries scored 1 or 2, compared with **9.23%** for on-time or early deliveries.
- All **17 data quality checks** passed during the reported validation run.

These results indicate a strong association between delivery delays and lower customer satisfaction. They do not establish causation.

## Project Structure

```text
olist-data-engineering/
├── data/                       # Source CSV files (download separately)
├── src/                        # Supporting analysis scripts
├── tests/
│   └── test_data_quality.py    # Automated data quality test
├── 01_create_schema.sql        # Database schema
├── 03_etl.py                   # ETL pipeline
├── 04_sql_analysis.sql         # Business analysis queries
├── 05_dashboard.py             # Streamlit dashboard
├── 06_data_quality.py          # Data quality validation
├── 07_delivery_analysis.sql    # Delivery performance analysis
├── data_quality_report.csv     # Generated quality report
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- PostgreSQL
- The Olist dataset downloaded from Kaggle

### 1. Download the dataset

Download the [Brazilian E-Commerce Public Dataset by Olist on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

Create a `data/` directory in the project root and place the required CSV files inside it, preserving their original filenames.

The source CSV files are not included in this repository.

### 2. Install dependencies

Open a terminal in the project directory and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Create a PostgreSQL database and configure the connection in a `.env` file in the project root:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Olist
DB_USER=postgres
DB_PASSWORD=your_local_password
```

Replace the example password with your own local database password. Never commit `.env` or publish database credentials.

### 4. Create the database schema

Execute `01_create_schema.sql` against your PostgreSQL database to create the required tables and constraints before running the ETL pipeline.

You can execute the SQL file using a PostgreSQL client such as pgAdmin or `psql`.

### 5. Run the ETL pipeline

```bash
python 03_etl.py
```

The pipeline validates the source files, transforms relevant fields, and loads the data into PostgreSQL in the correct dependency order. It checks the expected row counts and uses a database transaction to protect against partial loads.

The ETL uses a **full-refresh strategy** for the tables it manages: existing data in those tables is replaced on a successful run. The `customers` table is not refreshed by this pipeline and must already be populated.

The pipeline includes structured logging and records execution duration. Check the generated `etl.log` file for execution details.

### 6. Run data quality checks

```bash
python 06_data_quality.py
```

This executes 17 checks against PostgreSQL and generates `data_quality_report.csv`. The script exits with a failure status if any check fails.

### 7. Run automated tests

```bash
python -m pytest -v
```

The test suite verifies that the data quality script completes successfully, produces the expected report, and passes all 17 checks.

PostgreSQL must be running, the database must be populated, and `.env` must contain valid connection settings.

### 8. Launch the dashboard

```bash
python -m streamlit run 05_dashboard.py
```

Open the local URL displayed in the terminal to explore the dashboard.

## SQL Analysis

The project includes SQL queries and views covering:

- Order status and delivery KPIs
- Monthly value of delivered order items
- Payment method distribution
- Customer review distribution
- Late-delivery rates and delays
- Review scores by delivery performance

## Future Improvements

- Add tests for individual transformation functions.
- Automate ETL execution and scheduling.
- Containerize the application with Docker.
- Deploy the dashboard for public access.

## Data Source and Disclaimer

Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

This project is intended for educational purposes and as a data engineering portfolio project.
