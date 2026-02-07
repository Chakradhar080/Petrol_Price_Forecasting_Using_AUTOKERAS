"""
APScheduler application for automated task scheduling.
Runs as a standalone service.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scheduler.jobs import combined_daily_job, weekly_retraining_job
from config import SchedulerConfig
from utils.logger import setup_logger
import time

logger = setup_logger(__name__, 'logs/scheduler.log')

def create_scheduler():
    """
    Create and configure APScheduler
    
    Returns:
        BackgroundScheduler instance
    """
    scheduler = BackgroundScheduler()
    
    # Daily job: Data fetch + Prediction
    # Runs every day at configured hour (default: 9 AM)
    scheduler.add_job(
        combined_daily_job,
        trigger=CronTrigger(hour=SchedulerConfig.DATA_FETCH_HOUR, minute=0),
        id='daily_data_and_prediction',
        name='Daily Data Fetch and Prediction',
        replace_existing=True
    )
    logger.info(f"Scheduled daily job at {SchedulerConfig.DATA_FETCH_HOUR}:00")
    
    # Weekly job: Model Retraining
    # Runs once a week at configured day and hour (default: Sunday 2 AM)
    scheduler.add_job(
        weekly_retraining_job,
        trigger=CronTrigger(
            day_of_week=SchedulerConfig.RETRAIN_DAY,
            hour=SchedulerConfig.RETRAIN_HOUR,
            minute=0
        ),
        id='weekly_retraining',
        name='Weekly Model Retraining',
        replace_existing=True
    )
    logger.info(f"Scheduled weekly retraining on day {SchedulerConfig.RETRAIN_DAY} at {SchedulerConfig.RETRAIN_HOUR}:00")
    
    return scheduler

def main():
    """Main scheduler application"""
    if not SchedulerConfig.ENABLE_SCHEDULER:
        logger.warning("Scheduler is disabled in configuration")
        return
    
    logger.info("Starting Petrol Price Forecasting Scheduler...")
    
    # Create and start scheduler
    scheduler = create_scheduler()
    scheduler.start()
    
    logger.info("Scheduler started successfully")
    logger.info("Press Ctrl+C to exit")
    
    try:
        # Keep the script running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == '__main__':
    main()
