# Telegram Medical Business Analytics Platform

This repository contains an end-to-end data platform for analysing Ethiopian medical-sector businesses on Telegram. It scrapes raw messages, stages them in a data lake, pushes structured data into an Oracle warehouse, and exposes transformed analytics through dbt and (soon) a FastAPI service.

---

## Features

* **Telethon scraper** – Incremental, resumable scraping of specified Telegram channels / groups.
* **Data lake** – Raw JSON messages stored partitioned by date & channel (`data/raw/...`).
* **Oracle warehouse** – Thin-mode `oracledb` connection pool and dbt models (views & tables).
* **dbt** – Source definitions, staging, star-schema marts, and data tests.
* **Dagster (planned)** – Orchestration for scheduled scrape → load → transform workflows.
* **Docker (planned)** – Reproducible local dev + production deployments.

---

## Quick Start

### 1. Clone & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```dotenv
# Telegram API
telegram_api_id=123456
telegram_api_hash=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
telegram_session_name=telegram_scraper  # optional

# Data lake
DATA_LAKE_DIR=data/raw  # optional override

# Oracle connection
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=orclpdb1
ORACLE_USER=your_user
ORACLE_PASSWORD=your_password
```

> **Note**
> The `telegram_` prefix is required for Telegram settings because Pydantic auto-maps them in `src/config.py`.

### 3. Initialise the database

Ensure your Oracle instance is running and the user has permissions to create views & tables in the target schema.

### 4. Run the scraper

```bash
python -m src.scripts.scrape_channels --channels lobelia4cosmetics medi_store_ethiopia ...
```

This writes channel JSON files to `data/raw/telegram_messages/YYYY-MM-DD/<channel>.json`.

### 5. Load raw data into Oracle (optional)

Upload the JSON files to an Oracle external table or use `DBMS_CLOUD.COPY_DATA`. You can also leverage the `dbt-external-tables` package.

### 6. Execute dbt transformations

```bash
cd telegram-analytics-api
# Ensure ~/.dbt/profiles.yml has a `telegram_oracle` profile pointing to your DB

dbt deps   # only if using packages
# Build all models (staging + marts) and run tests
 dbt run && dbt test
```

---

## Repository Structure

```
├── data/                  # Raw / processed data (ignored by Git)
├── notebooks/             # Exploration & ad-hoc analysis
├── src/
│   ├── config.py          # Pydantic Settings loader
│   ├── constants/         # Reusable env constants
│   ├── db/                # Oracle connection helpers
│   └── scraper/           # Telethon scraping logic
├── dbt_project.yml        # dbt configuration
└── requirements.txt       # Python dependencies
```

---

## Testing

Run unit tests (coming soon) with **pytest**:

```bash
pytest -q
```

Data quality tests are implemented in dbt (`tests/` folder) and executed via `dbt test`.

---

## Contributing

1. Fork the repo & create your feature branch (`git checkout -b feature/foo`).
2. Commit your changes (`git commit -am 'Add foo'`).
3. Push to the branch (`git push origin feature/foo`).
4. Open a Pull Request.

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
