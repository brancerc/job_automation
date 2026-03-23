import os
import asyncio
import logging
from job_scraper import JobAggregator
from telegram_bot import JobTelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main orchestration function"""
    
    logger.info("=" * 60)
    logger.info("🚀 JOB AUTOMATION WORKFLOW STARTED")
    logger.info("=" * 60)
    
    # Step 1: Scrape jobs from all sources
    logger.info("\n📡 STEP 1: Scraping jobs from all sources...")
    aggregator = JobAggregator()
    new_jobs = aggregator.scrape_all()
    
    if not new_jobs:
        logger.info("✅ No new jobs found. Everything up to date!")
        return
    
    logger.info(f"\n✅ Found {len(new_jobs)} new job(s)")
    
    # Step 2: Send Telegram notifications
    logger.info("\n📱 STEP 2: Sending Telegram notifications...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        logger.error("Please set these environment variables before running")
        return
    
    notifier = JobTelegramNotifier(bot_token, chat_id)
    sent_count = await notifier.send_notifications_batch(new_jobs)
    
    # Step 3: Mark jobs as notified
    logger.info("\n💾 STEP 3: Updating database...")
    for job in new_jobs:
        aggregator.db.mark_notified(job['id'])
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    logger.info(f"📊 Summary: {sent_count} notifications sent for {len(new_jobs)} jobs")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
