import requests
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
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
        job_id = hashlib.md5(job['url'].encode()).hexdigest()
        
        try:
            c.execute('''
                INSERT INTO jobs 
                (id, title, company, url, location, type, posted_date, description, source, found_at, notified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                job.get('title', '')[:100],
                job.get('company', '')[:100],
                job['url'],
                job.get('location', '')[:50],
                job.get('type', 'Unknown'),
                job.get('posted_date', ''),
                job.get('description', '')[:500],
                job.get('source', 'Unknown'),
                datetime.now().isoformat(),
                0
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ New job added: {job['company']} - {job['title']}")
            return True
        except sqlite3.IntegrityError:
            conn.close()
            logger.debug(f"Duplicate job (already in DB): {job['url']}")
            return False
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            conn.close()
            return False
    
    def get_new_jobs(self, limit=20) -> List[Dict]:
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
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM jobs')
        total = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM jobs WHERE notified = 1')
        notified = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM jobs WHERE notified = 0')
        pending = c.fetchone()[0]
        conn.close()
        return {'total': total, 'notified': notified, 'pending': pending}


class LinkedInScraper:
    """Scrape LinkedIn job listings with multiple search queries"""
    
    def scrape(self) -> List[Dict]:
        """Fetch LinkedIn jobs using multiple search queries for variety"""
        jobs = []
        
        # Multiple search queries to get variety
        search_queries = [
            'internship mexico',
            'cybersecurity mexico',
            'network engineer mexico',
            'security analyst mexico',
            'junior software engineer mexico',
            'junior developer mexico',
            'support engineer mexico',
            'analyst mexico cdmx',
            'infrastructure mexico',
            'devops mexico'
        ]
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            for query in search_queries:
                try:
                    url = "https://www.linkedin.com/jobs/search/"
                    params = {'keywords': query, 'location': 'Mexico', 'sort': 'date'}
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-search-card')
                    
                    logger.info(f"LinkedIn search '{query}' found {len(job_cards)} results")
                    
                    for card in job_cards[:15]:  # 15 per search = more variety
                        try:
                            title_elem = card.find('h3', class_='base-search-card__title')
                            title = title_elem.get_text(strip=True) if title_elem else ''
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            company = company_elem.get_text(strip=True) if company_elem else ''
                            link = card.find('a', class_='base-card__full-link')
                            job_url = link.get('href', '') if link else ''
                            location_elem = card.find('span', class_='base-search-card__location')
                            location = location_elem.get_text(strip=True) if location_elem else 'Mexico'
                            
                            if title and job_url:
                                jobs.append({
                                    'title': title,
                                    'company': company,
                                    'url': job_url,
                                    'location': location,
                                    'type': 'Internship/Entry-level',
                                    'posted_date': '',
                                    'description': '',
                                    'source': 'LinkedIn'
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing LinkedIn job: {e}")
                            continue
                
                except Exception as e:
                    logger.error(f"LinkedIn search '{query}' error: {e}")
                    continue
            
            logger.info(f"LinkedIn scraper found {len(jobs)} total jobs")
        except Exception as e:
            logger.error(f"LinkedIn scraper error: {e}")
        
        return jobs


class JobAggregator:
    """Aggregate jobs from multiple sources"""
    
    def __init__(self):
        self.scrapers = [LinkedInScraper()]  # Only LinkedIn (works best)
        self.db = JobDatabase()
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs for Brando Cervantes - Telematics/Security/Network Profile"""
        
        tech_keywords = [
            # Security/Cybersecurity
            'cybersecurity', 'security', 'seguridad', 'ciberseguridad',
            'soc', 'threat', 'pentesting', 'vulnerability',
            'information security', 'infosec', 'iam',
            
            # Network/Infrastructure
            'network', 'networking', 'redes', 'cloud', 'aws', 'azure', 'gcp',
            'devops', 'infrastructure', 'systems', 'linux', 'windows',
            'docker', 'kubernetes',
            
            # Database/Data
            'database', 'sql', 'postgres', 'mysql', 'data',
            
            # Software Development
            'software', 'developer', 'programador', 'backend', 'frontend',
            'python', 'java', 'c++', 'go', 'rust', 'api', 'rest',
            
            # Job types (ALL LEVELS)
            'intern', 'becario', 'practicante', 'analyst', 'analista',
            'engineer', 'ingeniero', 'specialist', 'especialista',
            'junior', 'entry', 'support', 'soporte', 'administrator',
            
            # Companies
            'cisco', 'ericsson', 'dahua', 'hikvision', 'totalplay',
            'at&t', 'ibm', 'oracle',
        ]
        
        locations = [
            'cdmx', 'mexico city', 'ciudad de méxico', 'miguel hidalgo',
            'polanco', 'benito juarez', 'cuauhtemoc', 'mexico'
        ]
        
        exclude_keywords = [
            'sales', 'ventas', 'marketing', 'hr', 'rrhh', 'legal', 'abogado'
        ]
        
        filtered = []
        for job in jobs:
            title = job.get('title', '').lower()
            location = job.get('location', '').lower()
            company = job.get('company', '').lower()
            description = job.get('description', '').lower()
            full_text = f"{title} {company} {description}"
            
            # CDMX is REQUIRED
            has_location = any(loc in location for loc in locations)
            if not has_location:
                continue
            
            # Check for excluded keywords
            if any(excl in full_text for excl in exclude_keywords):
                continue
            
            # Must have at least one tech keyword
            has_tech = any(kw in full_text for kw in tech_keywords)
            
            if has_tech:
                filtered.append(job)
        
        return filtered
    
    def scrape_all(self) -> List[Dict]:
        """Run all scrapers and return new jobs"""
        all_jobs = []
        new_jobs = []
        
        logger.info("📡 Starting job scrape with multiple LinkedIn queries...")
        
        for scraper in self.scrapers:
            logger.info(f"Running {scraper.__class__.__name__}...")
            try:
                jobs = scraper.scrape()
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error in {scraper.__class__.__name__}: {e}")
        
        logger.info(f"📊 Raw jobs found: {len(all_jobs)}")
        
        # Filter
        filtered_jobs = self.filter_jobs(all_jobs)
        logger.info(f"📊 After filtering: {len(filtered_jobs)}")
        
        # Deduplicate and add to DB
        for job in filtered_jobs:
            if not self.db.job_exists(job['url']):
                if self.db.add_job(job):
                    new_jobs.append(job)
        
        logger.info(f"✅ New jobs: {len(new_jobs)}")
        
        # Get DB stats
        stats = self.db.get_stats()
        logger.info(f"📈 DB Stats - Total: {stats['total']} | Notified: {stats['notified']} | Pending: {stats['pending']}")
        
        return self.db.get_new_jobs(limit=20)


if __name__ == "__main__":
    aggregator = JobAggregator()
    new_jobs = aggregator.scrape_all()
    
    print(f"\n{'='*60}")
    print(f"Found {len(new_jobs)} new job(s) to notify")
    print(f"{'='*60}\n")
    
    for job in new_jobs:
        print(f"🔹 {job['company']} - {job['title']}")
        print(f"   📍 {job['location']} | {job['type']}")
        print(f"   📌 {job['source']}")
        print(f"   🔗 {job['url']}\n")