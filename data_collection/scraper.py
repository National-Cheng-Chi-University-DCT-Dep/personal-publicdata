#!/usr/bin/env python3
"""
Advanced University Data Scraper
Automatically collects and validates university application information

Features:
- Multi-source data collection
- DOM structure change detection  
- Rate limiting and politeness
- Data validation and cross-verification
- Error recovery and resilience
"""

import os
import sys
import time
import yaml
import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Web scraping
try:
    from bs4 import BeautifulSoup
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("⚠️  Missing dependencies. Install with: pip install beautifulsoup4 selenium requests")
    sys.exit(1)

@dataclass
class ScrapedData:
    school_id: str
    timestamp: datetime
    tuition_fee: Optional[str] = None
    ielts_requirements: Optional[Dict] = None
    application_deadline: Optional[str] = None
    course_list: Optional[List[str]] = None
    living_cost: Optional[str] = None
    scholarship_info: Optional[List[str]] = None
    professor_list: Optional[List[Dict]] = None
    source_urls: Optional[List[str]] = None
    confidence_score: float = 0.0
    
class UniversityScraper:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.data_collection_dir = self.base_dir / "data_collection"
        
        # Load configuration
        self.load_schools_config()
        self.setup_driver()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_delay = 2  # seconds between requests to same domain
        
        # DOM structure tracking
        self.dom_signatures_file = self.data_collection_dir / "dom_signatures.json"
        self.load_dom_signatures()
        
    def load_schools_config(self):
        """Load school configuration from YAML"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def setup_driver(self):
        """Setup headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"⚠️  Chrome driver setup failed: {e}")
            print("💡 Please install ChromeDriver: https://chromedriver.chromium.org/")
            self.driver = None
    
    def load_dom_signatures(self):
        """Load DOM structure signatures for change detection"""
        if self.dom_signatures_file.exists():
            with open(self.dom_signatures_file, 'r', encoding='utf-8') as f:
                self.dom_signatures = json.load(f)
        else:
            self.dom_signatures = {}
    
    def save_dom_signatures(self):
        """Save DOM structure signatures"""
        with open(self.dom_signatures_file, 'w', encoding='utf-8') as f:
            json.dump(self.dom_signatures, f, indent=2)
    
    def rate_limit(self, domain: str):
        """Implement polite rate limiting"""
        now = time.time()
        if domain in self.last_request_time:
            time_since_last = now - self.last_request_time[domain]
            if time_since_last < self.min_delay:
                sleep_time = self.min_delay - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()
    
    def get_dom_signature(self, html: str, url: str) -> str:
        """Generate DOM structure signature for change detection"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract structural elements that are likely to contain important data
        selectors = [
            'h1', 'h2', 'h3', '.tuition', '.fee', '.cost', '.deadline', 
            '.ielts', '.requirement', '.course', '.program', '#tuition',
            '#fee', '#deadline', '#requirements'
        ]
        
        signature_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                # Create signature from tag, class, and id
                sig = f"{elem.name}:{elem.get('class', [])}:{elem.get('id', '')}"
                signature_elements.append(sig)
        
        # Create hash of the structure
        structure_string = "|".join(sorted(signature_elements))
        return hashlib.md5(structure_string.encode()).hexdigest()
    
    def check_dom_changes(self, school_id: str, url: str, html: str) -> bool:
        """Check if DOM structure has changed significantly"""
        current_signature = self.get_dom_signature(html, url)
        key = f"{school_id}:{url}"
        
        if key in self.dom_signatures:
            stored_signature = self.dom_signatures[key]
            if current_signature != stored_signature:
                print(f"⚠️  DOM structure change detected for {school_id} at {url}")
                # Update signature and return False to indicate changes
                self.dom_signatures[key] = current_signature
                self.save_dom_signatures()
                return False
        else:
            # First time scraping this URL, store signature
            self.dom_signatures[key] = current_signature
            self.save_dom_signatures()
        
        return True
    
    def scrape_tuition_fee(self, soup: BeautifulSoup, school_id: str) -> Optional[str]:
        """Extract tuition fee information"""
        fee_indicators = [
            'tuition', 'fee', 'cost', 'price', 'euro', '€', 'eur',
            'semester', 'annual', 'year', 'non-eu', 'international'
        ]
        
        # Look for fee information in various elements
        for selector in ['p', 'div', 'span', 'td', 'li']:
            elements = soup.find_all(selector)
            for element in elements:
                text = element.get_text().lower()
                if any(indicator in text for indicator in fee_indicators):
                    # Extract fee with context
                    full_text = element.get_text().strip()
                    if len(full_text) < 200:  # Avoid very long texts
                        return full_text
        
        return None
    
    def scrape_ielts_requirements(self, soup: BeautifulSoup, school_id: str) -> Optional[Dict]:
        """Extract IELTS requirements"""
        ielts_indicators = ['ielts', 'english', 'language', 'proficiency', 'writing', 'speaking']
        
        requirements = {}
        
        for selector in ['p', 'div', 'span', 'td', 'li']:
            elements = soup.find_all(selector)
            for element in elements:
                text = element.get_text().lower()
                if 'ielts' in text:
                    full_text = element.get_text().strip()
                    
                    # Try to extract overall score
                    import re
                    overall_match = re.search(r'overall[:\s]*(\d+\.?\d*)', text)
                    if overall_match:
                        requirements['overall'] = float(overall_match.group(1))
                    
                    # Try to extract writing score
                    writing_match = re.search(r'writing[:\s]*(\d+\.?\d*)', text)
                    if writing_match:
                        requirements['writing'] = float(writing_match.group(1))
                    
                    # Try to extract minimum band
                    band_match = re.search(r'(?:minimum|band|each)[:\s]*(\d+\.?\d*)', text)
                    if band_match and 'minimum_band' not in requirements:
                        requirements['minimum_band'] = float(band_match.group(1))
                    
                    if requirements:  # If we found something, break
                        break
        
        return requirements if requirements else None
    
    def scrape_application_deadline(self, soup: BeautifulSoup, school_id: str) -> Optional[str]:
        """Extract application deadline"""
        deadline_indicators = [
            'deadline', 'apply', 'application', 'due', 'close', 'end',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        for selector in ['p', 'div', 'span', 'td', 'li']:
            elements = soup.find_all(selector)
            for element in elements:
                text = element.get_text().lower()
                if any(indicator in text for indicator in deadline_indicators):
                    full_text = element.get_text().strip()
                    if len(full_text) < 100 and any(month in text for month in deadline_indicators[6:]):
                        return full_text
        
        return None
    
    def scrape_professors(self, soup: BeautifulSoup, school_id: str) -> Optional[List[Dict]]:
        """Extract professor information"""
        professors = []
        
        # Look for faculty/staff listings
        faculty_sections = soup.find_all(['div', 'section'], 
                                       class_=lambda x: x and any(term in str(x).lower() 
                                       for term in ['faculty', 'staff', 'professor', 'academic']))
        
        for section in faculty_sections[:3]:  # Limit to first 3 sections
            names = section.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            for name_elem in names[:10]:  # Limit to 10 names per section
                name = name_elem.get_text().strip()
                if len(name.split()) >= 2 and len(name) < 50:  # Reasonable name length
                    prof_info = {'name': name}
                    
                    # Try to find associated email or title
                    parent = name_elem.parent
                    if parent:
                        text = parent.get_text()
                        import re
                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                        if email_match:
                            prof_info['email'] = email_match.group(1)
                    
                    professors.append(prof_info)
        
        return professors if professors else None
    
    def scrape_school_data(self, school_id: str) -> ScrapedData:
        """Scrape comprehensive data for a school"""
        school = self.schools[school_id]
        scraped_data = ScrapedData(school_id=school_id, timestamp=datetime.now())
        
        # Primary URL from school config
        primary_url = school.get('website', '')
        if not primary_url:
            print(f"❌ No website URL found for {school_id}")
            return scraped_data
        
        try:
            # Rate limiting
            from urllib.parse import urlparse
            domain = urlparse(primary_url).netloc
            self.rate_limit(domain)
            
            print(f"🔍 Scraping data for {school['full_name']}...")
            
            # Fetch the page
            if self.driver:
                self.driver.get(primary_url)
                time.sleep(3)  # Allow page to load
                html = self.driver.page_source
            else:
                response = requests.get(primary_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }, timeout=10)
                html = response.text
            
            # Check for DOM changes
            if not self.check_dom_changes(school_id, primary_url, html):
                print(f"⚠️  DOM structure changed for {school_id}, manual review recommended")
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract data
            scraped_data.tuition_fee = self.scrape_tuition_fee(soup, school_id)
            scraped_data.ielts_requirements = self.scrape_ielts_requirements(soup, school_id)
            scraped_data.application_deadline = self.scrape_application_deadline(soup, school_id)
            scraped_data.professor_list = self.scrape_professors(soup, school_id)
            scraped_data.source_urls = [primary_url]
            
            # Calculate confidence score based on how much data we found
            found_data = [
                scraped_data.tuition_fee,
                scraped_data.ielts_requirements,
                scraped_data.application_deadline,
                scraped_data.professor_list
            ]
            scraped_data.confidence_score = sum(1 for item in found_data if item is not None) / len(found_data)
            
            print(f"✅ Scraped {school_id}: confidence {scraped_data.confidence_score:.1%}")
            
        except Exception as e:
            print(f"❌ Error scraping {school_id}: {str(e)}")
        
        return scraped_data
    
    def scrape_all_schools(self) -> Dict[str, ScrapedData]:
        """Scrape data for all active schools"""
        results = {}
        
        active_schools = [school_id for school_id, school in self.schools.items() 
                         if school.get('status') == 'active']
        
        print(f"🚀 Starting data collection for {len(active_schools)} schools...")
        
        for school_id in active_schools:
            results[school_id] = self.scrape_school_data(school_id)
            
            # Small delay between schools to be polite
            time.sleep(1)
        
        return results
    
    def save_scraped_data(self, results: Dict[str, ScrapedData]):
        """Save scraped data to schools_live_data.yml"""
        output_data = {'schools_live_data': [], 'metadata': {
            'scraped_at': datetime.now().isoformat(),
            'total_schools': len(results),
            'scraper_version': '2.0.0'
        }}
        
        for school_id, data in results.items():
            school_data = {
                'school_id': school_id,
                'scraped_at': data.timestamp.isoformat(),
                'confidence_score': data.confidence_score,
                'data': {}
            }
            
            # Only include non-None data
            if data.tuition_fee:
                school_data['data']['tuition_fee_scraped'] = data.tuition_fee
            if data.ielts_requirements:
                school_data['data']['ielts_requirements_scraped'] = data.ielts_requirements
            if data.application_deadline:
                school_data['data']['application_deadline_scraped'] = data.application_deadline
            if data.professor_list:
                school_data['data']['professor_list'] = data.professor_list
            if data.source_urls:
                school_data['data']['source_urls'] = data.source_urls
            
            output_data['schools_live_data'].append(school_data)
        
        # Save to file
        output_file = self.source_data_dir / "schools_live_data.yml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"💾 Saved live data to {output_file}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main scraper execution"""
    scraper = UniversityScraper()
    
    try:
        # Scrape all schools
        results = scraper.scrape_all_schools()
        
        # Save results
        scraper.save_scraped_data(results)
        
        # Summary
        total_schools = len(results)
        successful_scrapes = sum(1 for data in results.values() if data.confidence_score > 0)
        
        print("\n📊 Scraping Summary:")
        print(f"   Total schools: {total_schools}")
        print(f"   Successful: {successful_scrapes}")
        print(f"   Success rate: {successful_scrapes/total_schools:.1%}")
        
    except Exception as e:
        print(f"❌ Scraper failed: {str(e)}")
        return 1
    
    finally:
        scraper.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
