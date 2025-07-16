# Telegram Analytics Pipeline

This directory contains the Dagster pipeline for orchestrating the Telegram analytics workflow.

## Pipeline Structure

The pipeline consists of four main operations:

1. `scrape_telegram_data`: Scrapes messages from configured Telegram channels
2. `load_raw_to_oracle`: Loads raw messages into Oracle database
3. `run_dbt_transformations`: Runs dbt transformations to create the data mart
4. `run_yolo_enrichment`: Runs YOLO object detection on images

## Running the Pipeline

1. Install Dagster:
```bash
pip install dagster dagster-webserver
```

2. Launch the Dagster UI:
```bash
dagster dev
```

3. The UI will be available at http://localhost:3000

## Configuration

The pipeline uses environment variables for configuration. Make sure to set the following in your `.env` file:

- ORACLE_HOST
- ORACLE_PORT
- ORACLE_SERVICE
- ORACLE_USER
- ORACLE_PASSWORD
- TELEGRAM_CHANNELS
- TELEGRAM_API_ID
- TELEGRAM_API_HASH
- TELEGRAM_SESSION_NAME
- DATA_LAKE_DIR
- DBT_PROFILES_DIR
- DBT_TARGET
- YOLO_MODEL_PATH

## Scheduling

The pipeline is configured to run daily at midnight (UTC). You can modify the schedule in `pipeline.py` by changing the `cron_schedule` parameter in the `@schedule` decorator.

## Monitoring

The Dagster UI provides:
- Pipeline visualization
- Run history
- Error tracking
- Asset materialization tracking
- Schedule management

## Error Handling

Each operation includes proper error handling and logging. Failed runs will be visible in the Dagster UI with detailed error information.
