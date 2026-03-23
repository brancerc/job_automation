# 🏗️ Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions (Free)                     │
│              Runs every 4 hours automatically                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Job Scraper Pipeline                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. MULTIPLE DATA SOURCES                                   │
│     ├─ Cisco Careers API                                    │
│     ├─ LinkedIn (with Selenium support)                     │
│     ├─ OCC.com.mx                                           │
│     └─ Expandable to more sources                           │
│                                                              │
│  2. FILTERING ENGINE                                        │
│     ├─ Keyword matching (intern, network, Cisco...)         │
│     ├─ Location filtering (CDMX, Mexico City...)            │
│     ├─ Company whitelisting                                 │
│     └─ Exclude patterns (senior, management...)             │
│                                                              │
│  3. DEDUPLICATION                                           │
│     ├─ SQLite database (jobs.db)                            │
│     ├─ URL-based deduplication (MD5 hash)                   │
│     ├─ Tracks all seen jobs                                 │
│     └─ Prevents duplicate notifications                     │
│                                                              │
│  4. NOTIFICATION ENGINE                                     │
│     ├─ Individual job alerts (one message per job)          │
│     ├─ Daily summary (all new jobs)                         │
│     ├─ Rich formatting (HTML)                               │
│     └─ Clickable apply links                                │
│                                                              │
│  5. STATE MANAGEMENT                                        │
│     ├─ Mark jobs as "notified"                              │
│     ├─ Store in jobs.db (SQLite)                            │
│     ├─ Persist across runs                                  │
│     └─ Git commit for history                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│             Telegram Bot API (Free, always on)              │
│        Sends formatted messages to your Telegram            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
                    📱 YOU RECEIVE ALERTS
```

---

## Database Schema

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,              -- MD5 hash of URL
    title TEXT,                       -- Job title
    company TEXT,                     -- Company name
    url TEXT UNIQUE,                  -- Job posting link
    location TEXT,                    -- Job location
    type TEXT,                        -- Internship/Entry-Level/etc
    posted_date TEXT,                 -- When job was posted
    description TEXT,                 -- Job description (truncated)
    source TEXT,                      -- Where we found it
    found_at TEXT,                    -- ISO timestamp when we found it
    notified INTEGER DEFAULT 0        -- 0 = not notified, 1 = already sent
);
```

---

## Data Flow Diagram

```
Github Actions Trigger (Cron)
        ↓
   [main.py]
        ↓
  [JobAggregator]
        ├─ CiscoScraper.scrape()        → [requests API]
        ├─ LinkedInScraper.scrape()     → [BeautifulSoup/Selenium]
        └─ OCCMexicoScraper.scrape()    → [requests + BS4]
        ↓
  [Filter & Deduplicate]
        ├─ Check keywords (title, company)
        ├─ Check location
        ├─ Query jobs.db for duplicates
        └─ Return only NEW jobs
        ↓
  [JobDatabase]
        ├─ INSERT INTO jobs (...)
        └─ Mark notified = 0
        ↓
  [JobTelegramNotifier]
        ├─ Format message (HTML)
        ├─ Send individual alerts
        └─ Send summary
        ↓
  [Telegram Bot API]
        ↓
  🔔 YOU GET NOTIFIED
        ↓
  [Commit jobs.db to Git]
        └─ Persist state
```

---

## Component Details

### 1. Job Scrapers

```python
class BaseScraper:
    def scrape(self) -> List[Dict]:
        # Must return list of dicts with:
        # - title (str)
        # - company (str)
        # - url (str)
        # - location (str)
        # - type (str)
        # - posted_date (str)
        # - description (str)
        pass
```

**Supported sources:**
- **Cisco Careers:** API-based (simplest)
- **LinkedIn:** Requires Selenium for JavaScript
- **OCC.com.mx:** HTML scraping with BeautifulSoup
- **Custom:** Add your own scraper!

### 2. Filtering Logic

```python
def filter_jobs(jobs: List[Dict]) -> List[Dict]:
    keywords = ['intern', 'network', 'cisco', ...]
    locations = ['cdmx', 'mexico city', ...]
    
    filtered = []
    for job in jobs:
        title_lower = job['title'].lower()
        location_lower = job['location'].lower()
        
        # Must match keyword AND location
        if any(kw in title_lower for kw in keywords):
            if any(loc in location_lower for loc in locations):
                filtered.append(job)
    
    return filtered
```

**Keywords to match:**
- Job type: intern, becario, graduate, entry-level, junior
- Technology: network, cisco, meraki, ericsson, dahua
- Role: engineer, support, analyst, specialist

### 3. Deduplication Strategy

**Method:** URL-based MD5 hashing

```python
job_id = hashlib.md5(job['url'].encode()).hexdigest()

# Check if job already exists
SELECT id FROM jobs WHERE url = ?

# If exists: skip (already notified before)
# If new: INSERT and set notified = 0
```

**Why this works:**
- URLs are unique identifiers
- Same job on different platforms = different URLs
- No duplicate notifications across runs

### 4. Telegram Notification Format

```python
message = """
🚀 NUEVA VACANTE ENCONTRADA

📌 {company} - {title}
🏢 Location: {location}
💼 Type: {type}
📅 Posted: {posted_date}

Source: {source}

🔗 [APPLY NOW]({url})
"""
```

**Features:**
- HTML formatting (bold, links)
- Emoji indicators
- Clickable apply link
- Summary message combining multiple jobs

### 5. GitHub Actions Workflow

```yaml
trigger: schedule (every 4 hours)
  │
  ├─ Checkout code
  ├─ Setup Python 3.11
  ├─ Install dependencies
  ├─ Run main.py
  │  └─ Sets env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  ├─ Commit jobs.db (if changed)
  └─ Done
```

**Execution time:** ~30 seconds
**Cost:** Minimal (part of 2,000 free minutes/month)

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Scraping time | 5-10 seconds |
| Filtering time | <1 second |
| DB insert time | <1 second |
| Telegram send time | 2-5 seconds |
| **Total per run** | **~30 seconds** |
| Runs per month | 180 (every 4 hours × 30 days) |
| **Total time/month** | **90 minutes** (well under 2,000 free limit) |

---

## Scalability

### Current limits
- **Jobs per run:** 50-100 (no hard limit)
- **Database size:** Unlimited (SQLite can handle millions)
- **Telegram messages:** 200+ per month free

### How to scale
- Add more scrapers (just inherit BaseScraper)
- Increase execution frequency
- Add more detailed filtering
- Store more job history

---

## Security Considerations

### Environment Variables
- `TELEGRAM_BOT_TOKEN` → GitHub Secrets (encrypted)
- `TELEGRAM_CHAT_ID` → GitHub Secrets (encrypted)
- Never committed to Git

### Database
- `jobs.db` stored in GitHub (committed for history)
- No sensitive data
- SQLite (encrypted if needed)

### API Usage
- Respects rate limiting
- User-Agent headers for politeness
- Timeout protection (10 seconds)

---

## Modification Guide

### Add a new scraper

```python
class MyNewScraper:
    def scrape(self) -> List[Dict]:
        jobs = []
        # Fetch from your source
        for item in data:
            jobs.append({
                'title': item['position'],
                'company': item['employer'],
                'url': item['link'],
                'location': item['city'],
                'type': 'Internship',
                'posted_date': item['date'],
                'description': item['description'],
                'source': 'My New Source'
            })
        return jobs

# Register in JobAggregator
self.scrapers = [
    CiscoScraper(),
    MyNewScraper(),  # Add here
]
```

### Change filtering logic

Edit `job_scraper.py`, method `filter_jobs()`:

```python
def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
    # Modify keywords, locations, exclude patterns
    keywords = ['your', 'new', 'keywords']
    locations = ['your', 'locations']
    
    # Optional: company whitelist
    companies = ['Cisco', 'Ericsson', 'Dahua']
    
    filtered = []
    for job in jobs:
        if matches_criteria(job, keywords, locations, companies):
            filtered.append(job)
    
    return filtered
```

### Change notification frequency

Edit `.github/workflows/job_alert.yml`:

```yaml
on:
  schedule:
    # Every 2 hours
    - cron: '0 */2 * * *'
    
    # Or specific times (UTC)
    - cron: '0 8,12,16,20 * * *'
```

---

## Monitoring & Debugging

### Check logs
```bash
# GitHub Actions → Job → scrape-and-notify
# View each step's output
```

### Test locally
```bash
pip install -r requirements.txt
python main.py  # Requires env vars
```

### Inspect database
```bash
sqlite3 jobs.db
SELECT COUNT(*) FROM jobs;
SELECT * FROM jobs WHERE notified = 0;
```

### Check deployment
```bash
# Jobs.db should update after each run
git log --oneline jobs.db
```

---

## Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| GitHub Actions | FREE | 2,000 min/month |
| Telegram Bot | FREE | Unlimited |
| Database | FREE | Stored in Git repo |
| Hosting | FREE | Serverless on GitHub |
| **TOTAL** | **$0** | Completely free! |

**Why free?**
- GitHub Actions: Everyone gets 2,000 free minutes
- Telegram: Free API forever
- No servers to rent
- No databases to pay for

---

## Future Enhancements

**Planned:**
- [ ] LinkedIn Selenium scraper
- [ ] OCC.com.mx HTML improvements
- [ ] Company review aggregation
- [ ] Salary range filtering
- [ ] Application tracking
- [ ] Success notification

**Possible:**
- [ ] Web dashboard
- [ ] Email forwarding
- [ ] Slack integration
- [ ] Discord bot
- [ ] Mobile app

---

## Architecture Evolution

**Phase 1 (Current)** - MVP
- Basic scrapers
- Simple filtering
- Telegram notifications
- SQLite deduplication

**Phase 2** - Enhanced
- Multiple notification channels
- Better filtering
- Job descriptions + reviews
- Analytics

**Phase 3** - Intelligence
- ML-based job matching
- Salary prediction
- Company sentiment analysis
- Interview preparation

---

That's the architecture! Clean, simple, and FREE. 🚀
