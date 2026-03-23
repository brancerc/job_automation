# Job Automation Configuration

## Filtering Keywords
# Add keywords to match in job titles and company names
FILTER_KEYWORDS = [
    # Job types
    'intern',
    'becario',
    'graduate',
    'entry-level',
    'junior',
    
    # Technologies (your expertise)
    'network',
    'networking',
    'cisc',  # Matches Cisco/Ciscom
    'meraki',
    'ericsson',
    'dahua',
    'hikvision',
    'totalplay',
    'at&t',
    'axtel',
    
    # Roles
    'engineer',
    'support',
    'analyst',
    'specialist',
    'administrator'
]

## Location Keywords
# Jobs must match at least one of these
FILTER_LOCATIONS = [
    'cdmx',
    'mexico city',
    'miguel hidalgo',
    'polanco',
    'granada',
    'anzures',
    'cuauhtemoc',
    'benito juarez',
    'mexico'
]

## Excluded Keywords (filter these OUT)
# Use this to exclude jobs that don't match your interest
EXCLUDE_KEYWORDS = [
    'senior',          # No senior roles
    'principal',       # No principal roles
    'management',      # No management
    'sales',           # No pure sales
]

## Company Whitelist (optional - if set, ONLY these companies)
# Leave empty to search all companies
COMPANY_WHITELIST = [
    'Cisco',
    'Ericsson',
    'Dahua',
    'Hikvision',
    'Totalplay',
    'AT&T',
    'Axtel',
    'Genetec',
    'NTT DATA',
    'Indra',
    'Huawei',
    'ZTE'
]

## Scraping Sources to Enable
ENABLED_SCRAPERS = {
    'cisco': True,
    'linkedin': False,  # Requires Selenium
    'occ_mexico': False,  # Requires BeautifulSoup improvements
}

## Telegram Notification Settings
TELEGRAM_SETTINGS = {
    'send_individual_alerts': True,   # Send one message per job
    'send_summary': True,              # Send daily summary
    'max_jobs_per_summary': 10,        # Max jobs in summary
    'include_description': True,       # Include job description
}

## Database Settings
DATABASE = {
    'name': 'jobs.db',
    'auto_cleanup_days': 30,  # Delete old jobs after N days
}

## Scraping Settings
SCRAPING = {
    'timeout_seconds': 10,
    'retry_attempts': 3,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

## Notification Formatting
MESSAGE_FORMAT = {
    'include_source': True,
    'include_posted_date': True,
    'include_description': True,
    'max_description_length': 500,
}
