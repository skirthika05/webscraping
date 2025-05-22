# Web Scraper

A Python-based web scraper that extracts recently registered Indian company information from [ZaubaCorp](https://www.zaubacorp.com). It uses `cloudscraper`, `BeautifulSoup`, and regular expressions to gather structured data such as company names, CINs, incorporation dates, email addresses (even obfuscated via Cloudflare), phone numbers, and more.

---

## 📌 Features

-  Scrapes company listings and details from ZaubaCorp
-  Saves extracted data to a clean CSV file
-  Adds random delays to avoid detection or rate-limiting
-  Debug-friendly HTML output for troubleshooting

---

## 🛠️ Tech Stack

- Python 3.x
- [cloudscraper](https://pypi.org/project/cloudscraper/) — for bypassing Cloudflare protection
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) — for HTML parsing
- [pandas](https://pandas.pydata.org/) — for tabular data handling and CSV export
- `re` and `urllib.parse` — for regex-based extraction and URL resolution

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/zaubacorp-scraper.git
cd zaubacorp-scraper
