import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from clients.serpapi_client import SerpApiClient
from extractors import extract_author, extract_year, extract_doc_type, extract_base
from exporters import to_csv
from models import SearchResult
from config import settings
from logger import get_logger

_log = get_logger("Main")

def run() -> None:
    client = SerpApiClient()
    results = []

    for page in tqdm(range(settings.PAGES), desc="Páginas Google"):
        start = page * 10
        try:
            data = client.search(settings.QUERY, start=start)
        except Exception as e:
            _log.error(f"Erro busca página {page}: {e}")
            continue

        for item in tqdm(data.get("organic_results", []), desc=f"Resultados {page+1}", leave=False):
            title   = item.get("title", "")
            link    = item.get("link", "")
            snippet = item.get("snippet", "")
            source  = item.get("displayed_link", "")

            author = year = doc_type = base = ""
            try:
                resp = requests.get(link, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                author   = extract_author(soup)
                year     = extract_year(link)
                doc_type = extract_doc_type(link)
                base     = extract_base(link)
            except Exception as e:
                _log.warning(f"Falha em {link}: {e}")

            results.append(SearchResult(
                title=title,
                author=author,
                abstract=snippet,
                source=source,
                year=year,
                doc_type=doc_type,
                base=base,
                link=link
            ))
            _log.info(f"Processado: {title}")

        time.sleep(settings.PAUSE_SEC)

    csv_path = to_csv(results)
    _log.info(f"Arquivo final em: {csv_path}")

if __name__ == "__main__":
    run()