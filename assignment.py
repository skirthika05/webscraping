import time
import random
import requests
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import sys


if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SimpleZaubacorpScraper:
    def __init__(self):
        self.base_url = "https://www.zaubacorp.com"
        self.session = cloudscraper.create_scraper()
    def get_page(self, url):
        """Get page content"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_companies_from_listing(self, html_content):
        """Extract company links from the listing page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        
        try:
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("HTML saved to debug_page.html")
        except Exception as e:
            print(f"Could not save HTML file: {e}")
        
        
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        companies = []
        
        
        all_links = soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip()
            
           
            if (text and len(text) > 5 and 
                any(word in text.lower() for word in ['private', 'limited', 'ltd', 'pvt', 'company', 'corp'])):
                
                full_url = urljoin(self.base_url, href)
                companies.append({
                    'name': text,
                    'url': full_url
                })
                print(f"Found company: {text[:50]}")
        
       
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                link = row.find('a')
                
                if link and link.get('href'):
                    text = link.get_text().strip()
                    href = link.get('href')
                    
                    if (text and len(text) > 3 and 
                        any(word in text.lower() for word in ['private', 'limited', 'ltd', 'pvt'])):
                        
                        full_url = urljoin(self.base_url, href)
                        companies.append({
                            'name': text,
                            'url': full_url
                        })
                        print(f"Table company: {text[:50]}")
        
       
        unique_companies = []
        seen_urls = set()
        
        for company in companies:
            if company['url'] not in seen_urls:
                seen_urls.add(company['url'])
                unique_companies.append(company)
        
        print(f"Total unique companies found: {len(unique_companies)}")
        return unique_companies
    
    def decode_cfemail(self, encoded_string):
        """Decode Cloudflare's obfuscated email addresses"""
        try:
            r = int(encoded_string[:2], 16)
            email = ''.join(
                chr(int(encoded_string[i:i+2], 16) ^ r)
                for i in range(2, len(encoded_string), 2)
            )
            return email
        except Exception as e:
            print(f"Error decoding cfemail: {e}")
            return ""

    def extract_company_details(self, html_content, company_url):
        """Extract detailed info from company page"""
        soup = BeautifulSoup(html_content, 'html.parser')

        details = {
            'URL': company_url,
            'Company Name': '',
            'CIN': '',
            'Status': '',
            'Date of Incorporation': '',
            'Email': '',
            'Phone': '',
            'Address': '',
            'ROC': '',
            'Registration Number': '',
            'Paid Up Capital': ''
        }

        
        page_text = soup.get_text()

        title = soup.find('title')
        if title:
            company_name = re.sub(r'\s*-\s*.*$', '', title.get_text()).strip()
            details['Company Name'] = company_name

        cin_match = re.search(r'CIN[:\s]*([A-Z]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})', page_text, re.IGNORECASE)
        if cin_match:
            details['CIN'] = cin_match.group(1)

        if re.search(r'\bactive\b', page_text, re.IGNORECASE):
            details['Status'] = 'Active'
        elif re.search(r'\binactive\b', page_text, re.IGNORECASE):
            details['Status'] = 'Inactive'

      
        date_match = re.search(r'(?:incorporation|incorporated)[:\s]*(\d{4}-\d{2}-\d{2})', page_text, re.IGNORECASE)
        if date_match:
            details['Date of Incorporation'] = date_match.group(1)

     
        cf_email_tag = soup.find('a', class_="__cf_email__")
        if cf_email_tag and cf_email_tag.get("data-cfemail"):
            encoded = cf_email_tag["data-cfemail"]
            decoded_email = self.decode_cfemail(encoded)
            details["Email"] = decoded_email
        else:
           
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
            if email_match:
                details["Email"] = email_match.group()

     
        phone_match = re.search(r'\+91[- ]?\d{10}|\b\d{10}\b', page_text)
        if phone_match:
            details['Phone'] = phone_match.group()

        
        address_tag = soup.find(text=re.compile("Address", re.IGNORECASE))
        if address_tag:
            parent = address_tag.find_parent()
            if parent:
                next_span = parent.find_next_sibling('span')
                if next_span:
                    details['Address'] = next_span.get_text(strip=True)

       
        roc_match = re.search(r'ROC[:\s]*([^,\n]+)', page_text, re.IGNORECASE)
        if roc_match:
            details['ROC'] = roc_match.group(1).strip()

        return details

    
    def scrape_recent_companies(self, max_companies=20):
        """Main scraping function"""
        url = "https://www.zaubacorp.com/companies-list/age-A-company.html"
        
       
        html_content = self.get_page(url)
        if not html_content:
            print("Failed to get listing page")
            return []
       
        companies = self.extract_companies_from_listing(html_content)
        if not companies:
            print("No companies found on listing page")
            return []
        
      
        companies = companies[:max_companies]
        print(f"Processing {len(companies)} companies...")
        
        detailed_companies = []
        
        for i, company in enumerate(companies):
            print(f"Processing {i+1}/{len(companies)}: {company['name'][:50]}")
            
            detail_html = self.get_page(company['url'])
            if detail_html:
                details = self.extract_company_details(detail_html, company['url'])
                detailed_companies.append(details)
                
                print(f"  Name: {details['Company Name'][:40]}")
                if details['CIN']:
                    print(f"  CIN: {details['CIN']}")
                if details['Email']:
                    print(f"  Email: {details['Email']}")
                if details['Date of Incorporation']:
                    print(f"  Incorporated: {details['Date of Incorporation']}")
            
            
            time.sleep(random.uniform(2, 4))
        
        return detailed_companies
    
    def save_to_csv(self, companies, filename='recent_companies.csv'):
        """Save to CSV file"""
        if not companies:
            print("No data to save")
            return
        
        df = pd.DataFrame(companies)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")
        return df

def main():
    scraper = SimpleZaubacorpScraper()
    

    companies = scraper.scrape_recent_companies(max_companies=10)  # Start with 10
    
    if companies:
        print(f"\nTotal companies scraped: {len(companies)}")
        
        # Save to CSV
        df = scraper.save_to_csv(companies)
        
        if df is not None:
            print("\nSample data:")
            print(df[['Company Name', 'CIN', 'Email', 'Date of Incorporation']].head())
    else:
        print("No companies were scraped successfully")

if __name__ == "__main__":
    main()