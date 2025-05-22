from bs4 import BeautifulSoup
from htmldate import find_date
from urllib.parse import urlparse
import requests

def extract_author(soup: BeautifulSoup) -> str:
    metas = [
        {'name': 'author'},
        {'property': 'article:author'},
        {'name': 'dc.creator'},
        {'name': 'byline'},
        {'name': 'sailthru.author'}
    ]
    for attrs in metas:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""

def extract_year(url: str) -> str:
    try:
        date = find_date(url)
        return date[:4] if date else ""
    except:
        return ""

def extract_doc_type(url: str, timeout: int = 10) -> str:
    try:
        head = requests.head(url, timeout=timeout)
        ctype = head.headers.get("Content-Type", "").lower()
        if "pdf" in ctype:
            return "PDF"
        if "html" in ctype:
            return "HTML"
        if "json" in ctype:
            return "JSON"
        return ctype.split("/")[0].upper()
    except:
        return ""

def extract_base(url: str) -> str:
    try:
        return urlparse(url).netloc
    except:
        return ""