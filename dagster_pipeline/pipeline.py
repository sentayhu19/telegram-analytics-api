from dagster import job, op, schedule, ScheduleEvaluationContext
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.scraper.collector import ChannelScraper
from src.loaders.load_raw_to_oracle import load_messages_from_date
from src.image.process_images import process_images_for_date
from src.constants import env

@op
async def scrape_telegram_data(context):
    """Scrape Telegram data for configured channels."""
    scraper = ChannelScraper()
    channels = env.TELEGRAM_CHANNELS.split(',')
    
    for channel in channels:
        try:
            await scraper.collect_messages(channel)
            context.log.info(f"Successfully scraped {channel}")
        except Exception as e:
            context.log.error(f"Error scraping {channel}: {str(e)}")
            raise

@op
async def load_raw_to_oracle(context):
    """Load raw Telegram messages into Oracle."""
    try:
        # Load messages from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        await load_messages_from_date(yesterday)
        context.log.info("Successfully loaded messages to Oracle")
    except Exception as e:
        context.log.error(f"Error loading to Oracle: {str(e)}")
        raise

@op
async def run_dbt_transformations(context):
    """Run dbt transformations to create the data mart."""
    try:
        result = subprocess.run(
            ['dbt', 'run'],
            check=True,
            capture_output=True,
            text=True
        )
        context.log.info(f"DBT run completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        context.log.error(f"DBT run failed: {e.stderr}")
        raise

@op
async def run_yolo_enrichment(context):
    """Run YOLO object detection on images."""
    try:
        # Process images from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        await process_images_for_date(yesterday)
        context.log.info("Successfully ran YOLO enrichment")
    except Exception as e:
        context.log.error(f"Error running YOLO enrichment: {str(e)}")
        raise

@job
async def telegram_analytics_pipeline():
    """Main pipeline for the Telegram analytics workflow."""
    scrape_telegram_data()
    load_raw_to_oracle()
    run_dbt_transformations()
    run_yolo_enrichment()

@schedule(
    cron_schedule="0 0 * * *",  # Run daily at midnight
    job=telegram_analytics_pipeline,
    execution_timezone="UTC"
)
def daily_telegram_analytics(context: ScheduleEvaluationContext):
    """Daily schedule for the Telegram analytics pipeline."""
    return telegram_analytics_pipeline.execute_in_process()
