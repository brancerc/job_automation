import os
import asyncio
import logging
from typing import List, Dict
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JobTelegramNotifier:
    """Send job notifications via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
    
    def format_job_message(self, job: Dict) -> str:
        """Format job data into a readable Telegram message"""
        message = f"""
🚀 <b>NUEVA VACANTE ENCONTRADA</b>

<b>📌 {job.get('company', 'Unknown')} - {job.get('title', 'Unknown')}</b>
🏢 <b>Location:</b> {job.get('location', 'Not specified')}
💼 <b>Type:</b> {job.get('type', 'Unknown')}
📅 <b>Posted:</b> {job.get('posted_date', 'Unknown')}

<b>Source:</b> {job.get('source', 'Unknown')}

🔗 <a href="{job.get('url', '#')}"><b>APPLY NOW</b></a>
"""
        return message.strip()
    
    async def send_notification(self, job: Dict) -> bool:
        """Send single job notification"""
        try:
            message = self.format_job_message(job)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info(f"✅ Notification sent: {job['company']} - {job['title']}")
            return True
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    async def send_summary(self, jobs: List[Dict]) -> bool:
        """Send summary message with all new jobs"""
        if not jobs:
            logger.info("No new jobs to notify")
            return True
        
        try:
            summary = f"<b>📊 JOB ALERT SUMMARY</b>\n\n"
            summary += f"Found <b>{len(jobs)}</b> new job(s) matching your criteria:\n\n"
            
            for i, job in enumerate(jobs[:10], 1):  # Limit to 10 jobs per summary
                summary += f"{i}. <b>{job['company']}</b> - {job['title']}\n"
                summary += f"   📍 {job['location']} | <a href=\"{job['url']}\">Apply</a>\n\n"
            
            if len(jobs) > 10:
                summary += f"\n... and {len(jobs) - 10} more jobs. Check your database! 🔍"
            
            summary += f"\n\n⏰ Last updated: {jobs[0]['found_at']}"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=summary,
                parse_mode='HTML'
            )
            logger.info(f"✅ Summary sent for {len(jobs)} jobs")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending summary: {e}")
            return False
    
    async def send_notifications_batch(self, jobs: List[Dict]) -> int:
        """Send notifications for multiple jobs"""
        sent_count = 0
        
        if not jobs:
            logger.info("No jobs to notify")
            return 0
        
        # Send individual notifications
        for job in jobs:
            if await self.send_notification(job):
                sent_count += 1
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(1)
        
        # Send summary
        await self.send_summary(jobs)
        
        logger.info(f"✅ Sent {sent_count}/{len(jobs)} notifications")
        return sent_count


async def main():
    """Test the notifier"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        return
    
    notifier = JobTelegramNotifier(bot_token, chat_id)
    
    # Test message
    test_job = {
        'company': 'Cisco',
        'title': 'Network Support Engineering Intern',
        'location': 'Mexico City, CDMX',
        'type': 'Internship (6 months)',
        'posted_date': '2024-03-19',
        'source': 'Cisco Careers',
        'url': 'https://jobs.cisco.com/jobs/...',
        'found_at': '2024-03-19T10:30:00'
    }
    
    await notifier.send_notification(test_job)


if __name__ == "__main__":
    asyncio.run(main())
