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
    
    # Initialize Telegram notifier first
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        logger.error("Please set these environment variables before running")
        return
    
    notifier = JobTelegramNotifier(bot_token, chat_id)
    
    # Send startup message
    logger.info("\n📱 STEP 0: Sending startup notification...")
    startup_msg = "🤖 <b>Job Automation Bot Started</b>\n\n⏱️ Scanning for new opportunities...\n\nStand by for results!"
    try:
        await notifier.bot.send_message(
            chat_id=chat_id,
            text=startup_msg,
            parse_mode='HTML'
        )
        logger.info("✅ Startup notification sent")
    except Exception as e:
        logger.error(f"⚠️ Could not send startup notification: {e}")
    
    # Step 1: Scrape jobs from all sources
    logger.info("\n📡 STEP 1: Scraping jobs from all sources...")
    aggregator = JobAggregator()
    new_jobs = aggregator.scrape_all()
    
    if not new_jobs:
        logger.info("✅ No new jobs found. Everything up to date!")
        try:
            await notifier.bot.send_message(
                chat_id=chat_id,
                text="✅ <b>Scan Complete</b>\n\nNo new opportunities at this time.\n\nKeep checking back!",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"⚠️ Could not send completion message: {e}")
        return
    
    logger.info(f"\n✅ Found {len(new_jobs)} new job(s)")
    
    # Step 2: Send Telegram notifications
    logger.info("\n📱 STEP 2: Sending Telegram notifications...")
    
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