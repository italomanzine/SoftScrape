from bs4 import BeautifulSoup
from htmldate import find_date
from urllib.parse import urlparse
import requests

def extract_author(soup: BeautifulSoup) -> str:
    """
    Extrai o nome do autor de uma página HTML usando várias meta tags e seletores CSS.
    """
    meta_tags_author = [
        {'name': 'author'},
        {'property': 'article:author'},
        {'name': 'citation_author'},
        {'name': 'dc.creator'},
        {'name': 'DC.creator'},
        {'name': 'DC.Creator'},
        {'name': 'byline'},
        {'name': 'sailthru.author'}
    ]
    for attrs in meta_tags_author:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            author_content = tag["content"].strip()
            if author_content and not author_content.lower().startswith("http"):
                return author_content

    author_css_selectors = [
        '.author-name',
        '.author',
        '[itemprop="author"] .name',
        '[itemprop="author"] span[itemprop="name"]',
        'a[rel="author"]',
        '.byline .author',
        '.post-author .fn',
        '.entry-author .author-name',
        'meta[property="article:author_name"]'
    ]
    for selector in author_css_selectors:
        author_tag = soup.select_one(selector)
        if author_tag:
            if author_tag.name == 'meta' and author_tag.get('content'):
                author_text = author_tag.get('content', '').strip()
            else:
                author_text = author_tag.get_text(strip=True)
            if author_text and not author_text.lower().startswith("http"):
                return author_text

    return ""

def extract_abstract(soup: BeautifulSoup) -> str:
    """
    Extrai o resumo/abstract de uma página HTML usando várias meta tags e seletores CSS.
    """
    meta_tags_abstract = [
        {"name": "description"},
        {"property": "og:description"},
        {"name": "twitter:description"},
        {"name": "DC.Description"},
        {"name": "DC.description"},
        {"name": "citation_abstract"}
    ]
    for attrs in meta_tags_abstract:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return tag["content"].strip()

    abstract_css_selectors = [
        'div.abstract > p',
        'section.abstract > p',
        'div[class*="abstract"] p',
        'p[class*="abstract"]',
        'div#abstract p',
        'article .entry-content p',
        'div.article-content p',
        'section[property="schema:abstract"] p',
        'div[property="schema:abstract"]'
    ]
    for selector in abstract_css_selectors:
        elements = soup.select(selector)
        if elements:
            abstract_parts = []
            for element in elements:
                if element.name == 'meta' and element.get('content'):
                    return element.get('content', '').strip()
                text = element.get_text(separator=" ", strip=True)
                if text:
                    abstract_parts.append(text)
            if abstract_parts:
                full_abstract = " ".join(abstract_parts)
                return full_abstract[:2000] + "..." if len(full_abstract) > 2000 else full_abstract

    return ""

def extract_year(url: str) -> str:
    """
    Extrai o ano de publicação da URL ou do conteúdo da página.
    """
    try:
        import re
        match = re.search(r'/(19\d{2}|20\d{2})/', url)
        if match:
            return match.group(1)
    except Exception:
        pass
    return ""

def extract_doc_type(url: str, timeout: int = 10) -> str:
    """
    Determina o tipo de documento (PDF, HTML, etc.) com base no Content-Type.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        head = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        head.raise_for_status()
        ctype = head.headers.get("Content-Type", "").lower()
        if "pdf" in ctype:
            return "PDF"
        if "html" in ctype:
            return "HTML"
        if "json" in ctype:
            return "JSON"
        if "xml" in ctype:
            return "XML"
        return ctype.split("/")[0].upper() if "/" in ctype else ctype.upper()
    except requests.exceptions.RequestException:
        return ""
    except Exception:
        return ""

def extract_base(url: str) -> str:
    """
    Extrai o domínio base (netloc) de uma URL.
    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except Exception:
        return ""
