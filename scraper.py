import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

scraper = Blueprint('scraper', __name__)

@scraper.route('/scrape_jobs')
def scrape_jobs():
    url = "https://remoteok.com"  # Example
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = [tag.text.strip() for tag in soup.select('tr.job h2')]
    return jsonify(jobs=jobs)