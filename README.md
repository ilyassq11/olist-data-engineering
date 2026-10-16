# Brazilian E-Commerce Data Engineering Project

## Overview

This project analyzes the Brazilian E-Commerce Public Dataset by Olist using Python, Pandas, PostgreSQL, SQL, and Streamlit.

The goal is to build a small end-to-end data pipeline, validate data quality, perform business analysis, and present key findings through an interactive dashboard.

## Tech Stack

* **Python** — ETL pipeline and automated data quality checks
* **Pandas** — data ingestion and transformation
* **PostgreSQL** — relational database and SQL analysis
* **SQLAlchemy** — database connectivity
* **Streamlit** — interactive dashboard
* **Plotly** — data visualizations
* **python-dotenv** — environment variable management

## Project Architecture

1. **Data ingestion:** Load the source CSV files.
2. **ETL pipeline:** Parse date columns and load data into PostgreSQL.
3. **Data quality:** Run automated checks for duplicates, missing relationships, invalid review scores, and invalid numeric values.
4. **SQL analysis:** Create views and analyze orders, payments, reviews, and delivery performance.
5. **Dashboard:** Explore the results through interactive charts and KPIs.

## Key Findings

The analysis of delivered orders found that:

* **8.11%** of delivered orders with available delivery dates arrived later than estimated.
* Late deliveries were associated with an average review score of **2.57/5**, compared with **4.29/5** for orders delivered on time or early.
* **54.03%** of reviews associated with late deliveries had a score of 1 or 2, compared with **9.23%** for on-time or early deliveries.
* The automated data quality script completed **17 checks**, all passing.

These findings show an association between delivery delays and lower customer satisfaction. They do not establish that delays alone caused the lower scores.

## Project Structure

```text
olist-data-engineering/
├── data/                       # Source CSV files (download separately)
├── 03_etl.py                   # ETL pipeline
├── 04_sql_analysis.sql         # Business analysis queries
├── 05_dashboard.py             # Streamlit dashboard
├── 06_data_quality.py          # Automated data quality checks
├── 07_delivery_analysis.sql    # Delivery performance analysis
├── data_quality_report.csv     # Generated quality check report
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

## Setup

### 1. Download the dataset

Download the Brazilian E-Commerce Public Dataset by Olist from Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Place the required CSV files inside the project's `data/` directory, preserving their original filenames.

### 2. Install dependencies

Python 3.10 or newer is recommended.

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Create a PostgreSQL database and configure the connection in a `.env` file in the project root.

Example:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Olist
DB_USER=postgres
DB_PASSWORD=your_local_password
```

Use your own local database credentials. Never commit the `.env` file.

Create the required tables and constraints in PostgreSQL before running the ETL pipeline.

### 4. Run the ETL pipeline

```bash
python 03_etl.py
```

The script reads the CSV files, converts relevant date columns, and loads the data into PostgreSQL.

**Note:** The current ETL script appends rows to existing tables. Prepare empty tables before the initial load, and do not rerun it against populated tables without resetting or adapting the load strategy.

### 5. Run data quality checks

```bash
python 06_data_quality.py
```

The script runs automated checks and generates a data quality report.

### 6. Launch the dashboard

```bash
python -m streamlit run 05_dashboard.py
```

Streamlit will provide a local URL where the dashboard can be viewed in a browser.

## SQL Analysis

The project includes SQL analysis for:

* Order status and delivery KPIs
* Monthly value of delivered order items
* Payment methods
* Customer review distribution
* Late delivery rates and delays
* Review scores by delivery performance

## Future Improvements

* Make the ETL pipeline idempotent and safe to rerun.
* Add structured logging and error handling.
* Automate pipeline execution.
* Add tests for transformation logic.
* Containerize the application with Docker.
* Deploy the dashboard.

## Data Source

Brazilian E-Commerce Public Dataset by Olist, available on Kaggle.

This project is for educational and portfolio purposes.

## Data Quality Testing

The project includes automated data quality checks for duplicate identifiers, referential integrity, invalid review scores, and negative financial values.

### Run data quality checks

```bash
python 06_data_quality.py
```

The script executes 17 checks against the PostgreSQL database and generates `data_quality_report.csv`.

### Run automated tests

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest -v
```

The test verifies that all data quality checks pass and that the report is generated correctly.

**Note:** PostgreSQL must be running, the database must be populated, and the local `.env` file must contain the correct connection settings.