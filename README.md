# Telegram Medical Business Analytics Platform

A comprehensive platform for analyzing medical product mentions in Telegram channels, featuring:

- Telegram data scraping
- Data warehousing with Oracle
- Data transformation with dbt
- Image analysis with YOLO
- RESTful API with FastAPI
- Pipeline orchestration with Dagster

---

## Features

- **Telethon scraper**
  - Incremental, resumable scraping of Telegram channels
  - JSON message storage in data lake
  - Error handling and logging

- **Data Warehouse**
  - Oracle database integration
  - Structured data storage
  - Connection pooling

- **Data Transformation**
  - dbt models for staging and marts
  - Star schema implementation
  - Business rule validations

- **Image Analysis**
  - YOLOv8 object detection
  - Image processing pipeline
  - Detection result storage

- **API**
  - FastAPI REST endpoints
  - Real-time analytics
  - Search functionality

- **Pipeline Orchestration**
  - Dagster workflow management
  - Daily scheduled runs
  - Monitoring and error tracking

- **Docker**
  - Containerized development environment
  - Production deployment ready
  - Isolated dependencies

---

## Quick Start

## Setup

### Prerequisites

1. Python 3.10+
2. Oracle Database
3. Docker (optional)

### Installation

1. Clone the repository
2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

1. Copy environment template:
```bash
cp .env.example .env
```
2. Edit `.env` with your credentials:
```env
# Oracle Database
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=freepdb1
ORACLE_USER=SYSTEM
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/freepdb1

# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=telegram_scraper
TELEGRAM_CHANNELS=channel1,channel2

# Data Lake
DATA_LAKE_DIR=data/raw

# dbt
DBT_PROFILES_DIR=~/.dbt
DBT_TARGET=oracle

# YOLO
YOLO_MODEL_PATH=models/yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
```

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Setup

1. Create the database schema:
```bash
python setup_database.py
```

2. Initialize dbt:
```bash
dbt init
```

### API Development

1. Run the API:
```bash
python -m api.run_api
```

2. Access the API at:
- Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health check: http://localhost:8000/api/health

### Pipeline Orchestration

1. Start Dagster UI:
```bash
dagster dev
```

2. Access the UI at: http://localhost:3000

## API Endpoints

### Top Products
```http
GET /api/reports/top-products?limit=10
```

### Channel Activity
```http
GET /api/channels/{channel_name}/activity?start_date=2023-01-01&end_date=2023-12-31
```

### Message Search
```http
POST /api/search/messages
Content-Type: application/json

{
    "query": "paracetamol",
    "channel": "optional_channel",
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-12-31T23:59:59Z",
    "limit": 10
}
```

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

## Project Structure

```
.
├── api/                 # FastAPI application for analytics
├── dagster_pipeline/    # Dagster pipeline orchestration
├── notebooks/           # Jupyter notebooks for development
├── src/                # Source code
│   ├── scraper/        # Telegram scraping logic
│   ├── loaders/        # Data loading utilities
│   ├── db/            # Database connections
│   ├── image/         # Image processing and YOLO
│   └── constants/      # Configuration and constants
├── tests/              # Test files
└── data/              # Data storage
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
