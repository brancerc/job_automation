import requests
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobDatabase:
    """SQLite database for tracking job postings"""
    
    def __init__(self, db_path='jobs.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database if not exists"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                url TEXT UNIQUE,
                location TEXT,
                type TEXT,
                posted_date TEXT,
                description TEXT,
                source TEXT,
                found_at TEXT,
                notified INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def job_exists(self, url: str) -> bool:
        """Check if job already in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id FROM jobs WHERE url = ?', (url,))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    def add_job(self, job: Dict) -> bool:
        """Add job to database, return True if new"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Generate unique ID from URL hash
        job_id = hashlib.md5(job['url'].encode()).hexdigest()
        
        try:
            c.execute('''
                INSERT INTO jobs 
                (id, title, company, url, location, type, posted_date, description, source, found_at, notified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                job.get('title', ''),
                job.get('company', ''),
                job['url'],
                job.get('location', ''),
                job.get('type', 'Unknown'),
                job.get('posted_date', ''),
                job.get('description', '')[:500],  # Limit description
                job.get('source', 'Unknown'),
                datetime.now().isoformat(),
                0  # not notified yet
            ))
            conn.commit()
            conn.close()
            logger.info(f"New job added: {job['company']} - {job['title']}")
            return True
        except sqlite3.IntegrityError:
            conn.close()
            logger.info(f"Job already exists: {job['url']}")
            return False
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            conn.close()
            return False
    
    def get_new_jobs(self, limit=10) -> List[Dict]:
        """Get jobs not yet notified"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT id, title, company, url, location, type, posted_date, description, source
            FROM jobs 
            WHERE notified = 0
            ORDER BY found_at DESC
            LIMIT ?
        ''', (limit,))
        
        jobs = []
        for row in c.fetchall():
            jobs.append({
                'id': row[0],
                'title': row[1],
                'company': row[2],
                'url': row[3],
                'location': row[4],
                'type': row[5],
                'posted_date': row[6],
                'description': row[7],
                'source': row[8]
            })
        
        conn.close()
        return jobs
    
    def mark_notified(self, job_id: str):
        """Mark job as notified"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE jobs SET notified = 1 WHERE id = ?', (job_id,))
        conn.commit()
        conn.close()


class CiscoScraper:
    """Scrape Cisco Careers for internship positions"""
    
    API_URL = "https://jobs.cisco.com/api/jobs"
    
    def scrape(self) -> List[Dict]:
        """Fetch Cisco job listings"""
        jobs = []
        try:
            params = {
                'search': 'intern',
                'location': 'Mexico',
                'page': 1
            }
            
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            job_list = data.get('jobs', [])
            
            for job in job_list:
                if 'intern' in job.get('title', '').lower() or 'mexico' in job.get('location', '').lower():
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': 'Cisco',
                        'url': f"https://jobs.cisco.com/jobs/{job.get('id', '')}",
                        'location': job.get('location', ''),
                        'type': 'Internship',
                        'posted_date': job.get('posted_date', ''),
                        'description': job.get('description', ''),
                        'source': 'Cisco Careers'
                    })
            
            logger.info(f"Cisco scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Cisco scraper error: {e}")
        
        return jobs


class LinkedInScraper:
    """Scrape LinkedIn job listings"""
    
    def scrape(self) -> List[Dict]:
        """Fetch LinkedIn internship positions in Mexico City"""
        jobs = []
        try:
            # LinkedIn is challenging to scrape directly due to JavaScript
            # Using a simple approach with the LinkedIn Job API (if available)
            # For now, we'll use a fallback to the public search
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            search_url = "https://www.linkedin.com/jobs/search/?keywords=internship&location=Mexico%20City"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # Note: LinkedIn heavily protects against scraping
            # This is a placeholder - LinkedIn requires Selenium for full JS rendering
            logger.info("LinkedIn scraper (limited): LinkedIn requires Selenium for full scraping")
        except Exception as e:
            logger.error(f"LinkedIn scraper error: {e}")
        
        return jobs


class OCCMexicoScraper:
    """Scrape OCC.com.mx for internships in Mexico"""
    
    def scrape(self) -> List[Dict]:
        """Fetch OCC.com.mx internship positions"""
        jobs = []
        try:
            url = "https://www.occ.com.mx/empleos/de-becario/en-ciudad-de-mexico/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # OCC.com.mx structure would require BeautifulSoup parsing
            # Basic placeholder for demonstration
            logger.info("OCC scraper: Connected to OCC.com.mx")
        except Exception as e:
            logger.error(f"OCC scraper error: {e}")
        
        return jobs


class JobAggregator:
    """Aggregate jobs from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            CiscoScraper(),
            LinkedInScraper(),
            OCCMexicoScraper()
        ]
        self.db = JobDatabase()
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs based on criteria"""
        keywords = ['intern', 'becario', 'network', 'cisco', 'meraki', 'ericsson', 
                   'dahua', 'hikvision', 'totalplay', 'at&t', 'engineer', 'support']
        locations = ['cdmx', 'mexico city', 'miguel hidalgo', 'polanco']
        
        filtered = []
        for job in jobs:
            title = job.get('title', '').lower()
            location = job.get('location', '').lower()
            company = job.get('company', '').lower()
            
            # Check keywords
            has_keyword = any(kw in title or kw in company for kw in keywords)
            # Check location
            has_location = any(loc in location for loc in locations) or 'mexico' in location
            
            if has_keyword and has_location:
                filtered.append(job)
        
        return filtered
    
    def scrape_all(self) -> List[Dict]:
        """Run all scrapers and return new jobs"""
        all_jobs = []
        new_jobs = []
        
        for scraper in self.scrapers:
            logger.info(f"Running {scraper.__class__.__name__}...")
            jobs = scraper.scrape()
            all_jobs.extend(jobs)
        
        # Filter and deduplicate
        filtered_jobs = self.filter_jobs(all_jobs)
        
        for job in filtered_jobs:
            if not self.db.job_exists(job['url']):
                if self.db.add_job(job):
                    new_jobs.append(job)
        
        logger.info(f"Total jobs found: {len(all_jobs)} | Filtered: {len(filtered_jobs)} | New: {len(new_jobs)}")
        return self.db.get_new_jobs()


if __name__ == "__main__":
    aggregator = JobAggregator()
    new_jobs = aggregator.scrape_all()
    
    print(f"\n{'='*60}")
    print(f"Found {len(new_jobs)} new job(s)")
    print(f"{'='*60}\n")
    
    for job in new_jobs:
        print(f"🔹 {job['company']} - {job['title']}")
        print(f"   📍 {job['location']} | {job['type']}")
        print(f"   🔗 {job['url']}\n")
