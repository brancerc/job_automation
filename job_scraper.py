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
        
        # Generate unique ID from URL hash
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
            logger.debug(f"Job already exists: {job['url']}")
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
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('a', class_='jobCard')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='jobPosting')
            
            for card in job_cards[:20]:
                try:
                    title = card.get('aria-label', '')
                    if not title:
                        title_elem = card.find('h2')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                    
                    job_url = card.get('href', '')
                    if not job_url.startswith('http'):
                        job_url = 'https://www.occ.com.mx' + job_url
                    
                    company = ''
                    company_elem = card.find('span', class_='company')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    
                    location = 'Mexico City'
                    
                    if title and job_url:
                        jobs.append({
                            'title': title,
                            'company': company or 'OCC',
                            'url': job_url,
                            'location': location,
                            'type': 'Becario',
                            'posted_date': '',
                            'description': '',
                            'source': 'OCC.com.mx'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing OCC job: {e}")
                    continue
            
            logger.info(f"OCC scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"OCC scraper error: {e}")
        
        return jobs


class IndeedScraper:
    """Scrape Indeed.com.mx for jobs"""
    
    def scrape(self) -> List[Dict]:
        """Fetch Indeed jobs for interns in Mexico City"""
        jobs = []
        try:
            base_url = "https://mx.indeed.com/jobs"
            params = {
                'q': 'becario OR intern OR practicante',
                'l': 'Mexico City',
                'sort': 'date'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='resultContent')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    link = card.find('a', class_='jcs-JobTitle')
                    job_url = link.get('href', '') if link else ''
                    if job_url and not job_url.startswith('http'):
                        job_url = 'https://mx.indeed.com' + job_url
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    location_elem = card.find('span', class_='companyLocation')
                    location = location_elem.get_text(strip=True) if location_elem else 'Mexico City'
                    
                    if title and job_url:
                        jobs.append({
                            'title': title,
                            'company': company,
                            'url': job_url,
                            'location': location,
                            'type': 'Internship',
                            'posted_date': '',
                            'description': '',
                            'source': 'Indeed.com.mx'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing Indeed job: {e}")
                    continue
            
            logger.info(f"Indeed scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Indeed scraper error: {e}")
        
        return jobs


class LinkedInScraper:
    """Scrape LinkedIn job listings"""
    
    def scrape(self) -> List[Dict]:
        """Fetch LinkedIn internship positions in Mexico"""
        jobs = []
        try:
            url = "https://www.linkedin.com/jobs/search/"
            params = {
                'keywords': 'internship AND (mexico OR CDMX)',
                'location': 'Mexico',
                'sort': 'date'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='base-search-card')
            
            for card in job_cards[:20]:
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
                            'type': 'Internship',
                            'posted_date': '',
                            'description': '',
                            'source': 'LinkedIn'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing LinkedIn job: {e}")
                    continue
            
            logger.info(f"LinkedIn scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"LinkedIn scraper error: {e}")
        
        return jobs


class ComputrabajoScraper:
    """Scrape Computrabajo.com.mx for tech jobs"""
    
    def scrape(self) -> List[Dict]:
        """Fetch Computrabajo tech internships in Mexico"""
        jobs = []
        try:
            url = "https://www.computrabajo.com.mx/search/empleos"
            params = {
                'q': 'becario OR intern',
                'l': 'Mexico City'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='search-result-item')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find('h2', class_='job-title')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    company_elem = card.find('span', class_='company-name')
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    link = card.find('a', class_='job-link')
                    job_url = link.get('href', '') if link else ''
                    if job_url and not job_url.startswith('http'):
                        job_url = 'https://www.computrabajo.com.mx' + job_url
                    
                    location = 'Mexico City'
                    
                    if title and job_url:
                        jobs.append({
                            'title': title,
                            'company': company,
                            'url': job_url,
                            'location': location,
                            'type': 'Becario',
                            'posted_date': '',
                            'description': '',
                            'source': 'Computrabajo.com.mx'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing Computrabajo job: {e}")
                    continue
            
            logger.info(f"Computrabajo scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Computrabajo scraper error: {e}")
        
        return jobs


class HirelineScraper:
    """Scrape Hireline.io for startup jobs"""
    
    def scrape(self) -> List[Dict]:
        """Fetch Hireline internship positions"""
        jobs = []
        try:
            url = "https://hireline.io/jobs"
            params = {
                'search': 'intern OR becario',
                'location': 'Mexico'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='job-card')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    company_elem = card.find('p', class_='company')
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    link = card.find('a')
                    job_url = link.get('href', '') if link else ''
                    if job_url and not job_url.startswith('http'):
                        job_url = 'https://hireline.io' + job_url
                    
                    if title and job_url:
                        jobs.append({
                            'title': title,
                            'company': company,
                            'url': job_url,
                            'location': 'Mexico',
                            'type': 'Internship',
                            'posted_date': '',
                            'description': '',
                            'source': 'Hireline.io'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing Hireline job: {e}")
                    continue
            
            logger.info(f"Hireline scraper found {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Hireline scraper error: {e}")
        
        return jobs


class JobAggregator:
    """Aggregate jobs from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            OCCMexicoScraper(),
            IndeedScraper(),
            LinkedInScraper(),
            ComputrabajoScraper(),
            HirelineScraper()
        ]
        self.db = JobDatabase()
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs for Brando Cervantes - Telematics Engineering Profile"""
        
        # Keywords for Telematics/Network/Security/Cloud/SOC
        tech_keywords = [
            # Job types
            'intern', 'becario', 'practicante', 'pasante', 'trainee',
            
            # Core telematics
            'network', 'networking', 'redes', 'cybersecurity', 'security', 
            'seguridad', 'cloud', 'aws', 'azure', 'gcp', 'soc', 'analyst',
            'database', 'sql', 'postgres', 'devops', 'infrastructure',
            
            # Companies of interest
            'cisco', 'meraki', 'ericsson', 'dahua', 'hikvision', 'totalplay',
            'at&t', 'axtel', 'genetec', 'ntt', 'ibm', 'oracle', 'huawei', 'zte',
            
            # Engineering roles
            'engineer', 'ingeniero', 'support', 'soporte', 'specialist',
            'especialista', 'técnico', 'admin', 'administrator', 'system',
            
            # Development
            'software', 'developer', 'programador', 'backend', 'frontend',
            'python', 'java', 'c++', 'go', 'rust',
            
            # Tech skills
            'linux', 'windows', 'wireshark', 'firewall', 'router', 'vpn',
            'encryption', 'api', 'rest', 'docker', 'kubernetes', 'git'
        ]
        
        locations = [
            'cdmx', 'mexico city', 'ciudad de méxico', 'miguel hidalgo',
            'polanco', 'benito juarez', 'cuauhtemoc', 'anzures', 'granada',
            'mexico'
        ]
        
        exclude_keywords = [
            'sales', 'ventas', 'marketing', 'hr', 'rrhh',
            'legal', 'abogado', 'contador'
        ]
        
        filtered = []
        for job in jobs:
            title = job.get('title', '').lower()
            location = job.get('location', '').lower()
            company = job.get('company', '').lower()
            description = job.get('description', '').lower()
            full_text = f"{title} {company} {description}"
            
            # Check location match
            has_location = any(loc in location for loc in locations)
            if not has_location:
                continue
            
            # Check for excluded keywords
            if any(excl in full_text for excl in exclude_keywords):
                continue
            
            # Check for tech keywords (at least one match)
            has_tech = any(kw in full_text for kw in tech_keywords)
            
            if has_tech:
                filtered.append(job)
        
        return filtered
    
    def scrape_all(self) -> List[Dict]:
        """Run all scrapers and return new jobs"""
        all_jobs = []
        new_jobs = []
        
        for scraper in self.scrapers:
            logger.info(f"Running {scraper.__class__.__name__}...")
            try:
                jobs = scraper.scrape()
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error in {scraper.__class__.__name__}: {e}")
        
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
        print(f"   📌 {job['source']}")
        print(f"   🔗 {job['url']}\n")