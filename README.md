# 🚀 Job Automation Bot - Brando's Job Alerts

Automated job scraper that finds internship opportunities matching your profile and sends notifications via Telegram. Uses GitHub Actions to run every 4 hours completely free.

---

## 📋 Features

✅ **Multi-source scraping:**
- Cisco Careers API
- LinkedIn (basic support)
- OCC.com.mx
- Other job portals (expandable)

✅ **Smart filtering:**
- Keywords: internship, becario, network, Cisco, Meraki, Ericsson, Dahua, etc.
- Location: Mexico City, CDMX, Miguel Hidalgo, Polanco
- Company whitelisting

✅ **Deduplication:**
- SQLite database tracks all seen jobs
- No duplicate notifications

✅ **Telegram notifications:**
- Individual job alerts
- Daily/periodic summaries
- Clickable links to apply

✅ **Automated execution:**
- GitHub Actions (runs every 4 hours, completely free)
- No server needed
- 2,000 free minutes/month

---

## 🛠️ Setup Instructions

### Step 1: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Follow prompts:
   - Name: `BrandoJobAlerts` (or whatever you want)
   - Username: `brando_job_alerts_bot` (must be unique)
4. Copy the **API Token** (looks like: `123456789:ABCDefGHIJKLmnoPQRSTUvwxyz`)
5. Send `/start` to your new bot to enable it

Get your **Chat ID:**
1. Search for **@userinfobot** on Telegram
2. Send `/start`
3. It will show your Chat ID (a number like: `987654321`)

### Step 2: Fork/Create GitHub Repository

```bash
# Option A: Clone this repo and push to your GitHub
git clone https://github.com/brancerc/job_automation.git
cd job_automation
git remote set-url origin https://github.com/YOUR_USERNAME/job_automation.git
git push -u origin main

# Option B: Create new repo
git init
git add .
git commit -m "Initial commit: Job automation setup"
git remote add origin https://github.com/YOUR_USERNAME/job_automation.git
git branch -M main
git push -u origin main
```

### Step 3: Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add two secrets:

   **Name:** `TELEGRAM_BOT_TOKEN`
   **Value:** Paste your API Token from BotFather
   
   **Name:** `TELEGRAM_CHAT_ID`
   **Value:** Paste your Chat ID from @userinfobot

4. Click **Add secret** for each

### Step 4: Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"** (if shown)
3. That's it! Workflow will run automatically

---

## 🚀 Usage

### Automatic (every 4 hours)
Nothing to do! GitHub Actions will run automatically and send Telegram messages.

### Manual trigger
1. Go to **Actions** tab
2. Select **"🚀 Job Scraper Alert"** on the left
3. Click **"Run workflow"** → **Run workflow**

### Check logs
1. Go to **Actions** → **"🚀 Job Scraper Alert"**
2. Click the latest run
3. Click **"scrape-and-notify"** to see detailed logs

---

## 📝 Project Structure

```
job_automation/
├── main.py                 # Main orchestration script
├── job_scraper.py          # Scraping logic + database
├── telegram_bot.py         # Telegram notifications
├── requirements.txt        # Python dependencies
├── jobs.db                 # SQLite database (auto-created)
├── README.md               # This file
└── .github/
    └── workflows/
        └── job_alert.yml   # GitHub Actions workflow
```

---

## 🎯 Customization

### Change scraping frequency
Edit `.github/workflows/job_alert.yml`:

```yaml
on:
  schedule:
    # Run every 2 hours instead of 4
    - cron: '0 */2 * * *'
    
    # Or run at specific times (UTC):
    # 8 AM, 12 PM, 4 PM, 8 PM UTC
    - cron: '0 8,12,16,20 * * *'
```

[Cron time reference](https://crontab.guru/)

### Add more job sources
Edit `job_scraper.py`, add new scraper class:

```python
class NewSiteScraper:
    def scrape(self) -> List[Dict]:
        # Your scraping logic here
        jobs = []
        # ...
        return jobs

# Add to JobAggregator
self.scrapers = [
    CiscoScraper(),
    NewSiteScraper(),  # Add here
    # ...
]
```

### Change filter keywords
Edit `job_scraper.py` in `filter_jobs()`:

```python
keywords = ['intern', 'becario', 'network', 'cisco', 
           'your_keyword', 'another_keyword']
```

### Adjust notification format
Edit `telegram_bot.py` in `format_job_message()`:

```python
def format_job_message(self, job: Dict) -> str:
    message = f"""
    Your custom format here
    {job['title']}
    {job['company']}
    # ...
    """
    return message
```

---

## 🔧 Troubleshooting

### Not receiving notifications
1. Check Telegram secrets are correct:
   - Go to Settings → Secrets → verify values
2. Test bot manually:
   ```bash
   python telegram_bot.py
   ```
3. Check GitHub Actions logs for errors

### No jobs found
1. Check filter keywords in `job_scraper.py`
2. Verify scrapers are returning data:
   ```bash
   python job_scraper.py
   ```
3. Expand location filter

### Database errors
Simply delete `jobs.db` and the bot will recreate it:
```bash
rm jobs.db
```

---

## 📊 Monitoring

### Check job database
```bash
sqlite3 jobs.db
SELECT COUNT(*) FROM jobs;
SELECT * FROM jobs WHERE notified = 0;
.exit
```

### View GitHub Actions logs
1. Go to **Actions** tab
2. Click latest workflow run
3. View detailed execution logs

### Set up email notifications
GitHub can email you when workflows fail:
1. Go to repo → **Settings** → **Notifications**
2. Select notification preferences

---

## 🎓 How It Works

```
┌─────────────────────────────────────────────────┐
│  GitHub Actions Timer (every 4 hours)           │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  1. Scrape multiple job sources                 │
│     - Cisco Careers                             │
│     - LinkedIn                                  │
│     - OCC.com.mx                                │
│     - Others...                                 │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  2. Filter jobs by keywords + location          │
│     - Match: "intern", "network", "Mexico City" │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  3. Check SQLite database for duplicates        │
│     - Only process NEW jobs                     │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  4. Send Telegram notifications                 │
│     - Individual job alerts                     │
│     - Daily summary                             │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  📱 YOU RECEIVE ALERTS ON TELEGRAM              │
│     - Click to apply directly                   │
│     - New opportunities every 4 hours           │
└─────────────────────────────────────────────────┘
```

---

## 📱 Telegram Message Example

```
🚀 NUEVA VACANTE ENCONTRADA

📌 Cisco - Network Support Engineering Intern
🏢 Location: Mexico City, CDMX
💼 Type: Internship (6 months)
📅 Posted: 2024-03-19

Source: Cisco Careers

🔗 APPLY NOW
```

---

## 🆓 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| GitHub Actions | FREE | 2,000 free minutes/month |
| Telegram Bot | FREE | Forever free |
| Database (jobs.db) | FREE | Stored in GitHub repo |
| **TOTAL** | **$0/month** | ✅ Completely free! |

---

## 📈 Next Steps

1. ✅ Set up Telegram bot and secrets
2. ✅ Push code to GitHub
3. ✅ Enable GitHub Actions
4. ✅ Wait for first run (or trigger manually)
5. ✅ Receive Telegram alerts every 4 hours
6. 🔄 Apply to opportunities
7. 🎯 Get job offer! 🎉

---

## 🤝 Contributing

Want to improve the scraper? 

1. Add new job sources in `job_scraper.py`
2. Improve filtering logic
3. Add more companies to whitelist
4. Test with real job portals

---

## 📧 Support

Stuck? Check:
1. GitHub Actions logs (Actions → Latest run)
2. Telegram secrets configuration
3. Python installation
4. Network connectivity

---

## 🎉 Credits

Built for Brando's job search automation. May your next opportunity be just a Telegram message away! 🚀

---

**Good luck with your job search!** 💪

If you land a job using this bot, please update the README with your success story! 🎊
