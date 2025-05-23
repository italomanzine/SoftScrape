import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

from clients.serpapi_client import SerpApiClient
from extractors import extract_author, extract_year, extract_doc_type, extract_base, extract_abstract
from exporters import to_csv
from models import SearchResult
from config import settings
from logger import get_logger

_log = get_logger("Main")

def run() -> None:
    while True:
        engine_choice = input("Qual buscador você gostaria de usar? (google / scholar): ").strip().lower()
        if engine_choice in ["google", "scholar"]:
            search_engine_api = "google" if engine_choice == "google" else "google_scholar"
            engine_name_for_file = "google" if engine_choice == "google" else "google_scholar"
            break
        else:
            _log.warning("Opção inválida. Por favor, digite 'google' ou 'scholar'.")

    client = SerpApiClient()
    results = []
    # User-Agent comum para parecer um navegador e evitar bloqueios simples
    http_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for page in tqdm(range(settings.PAGES), desc=f"Páginas {engine_choice.capitalize()}"):
        start = page * settings.RESULTS_PER_PAGE # Assumindo que RESULTS_PER_PAGE é 10 ou configurável
        try:
            data = client.search(settings.QUERY, start=start, engine=search_engine_api)
            if not data: # Verifica se data é None ou vazio
                _log.warning(f"Nenhum dado retornado pela API para a página {page+1} no {engine_choice.capitalize()}.")
                continue
        except Exception as e:
            _log.error(f"Erro ao buscar dados da API para a página {page+1} no {engine_choice.capitalize()}: {e}")
            continue # Pula para a próxima página em caso de erro na API

        organic_results = data.get("organic_results", [])
        if not organic_results:
            _log.info(f"Nenhum resultado orgânico encontrado na página {page+1} para {engine_choice.capitalize()}.")
            # Considerar se deve parar ou continuar se uma página não tiver resultados
            # time.sleep(settings.PAUSE_SEC) # Pausa mesmo se não houver resultados para evitar sobrecarga
            # continue

        for item in tqdm(organic_results, desc=f"Resultados Página {page+1}", leave=False):
            title   = item.get("title", "")
            link    = item.get("link", "")
            snippet = item.get("snippet", "") # Usado como fallback para o resumo
            source  = item.get("displayed_link", item.get("source", "")) # Fallback para 'source' se 'displayed_link' não existir

            author = ""
            year = "" # Inicializa o ano
            doc_type = ""
            base = ""
            full_abstract = snippet # Inicializa o resumo com o snippet da API

            if link:
                try:
                    # Tenta obter o ano da URL antes de fazer a requisição, se possível
                    year = extract_year(link) # extract_year agora só usa a URL

                    resp = requests.get(link, timeout=15, headers=http_headers, allow_redirects=True)
                    resp.raise_for_status() # Levanta exceção para códigos de erro HTTP
                    
                    # Determina o tipo de documento ANTES de tentar parsear como HTML
                    # Isso é importante porque não queremos tentar parsear um PDF como HTML
                    content_type_header = resp.headers.get("Content-Type", "").lower()
                    if "pdf" in content_type_header:
                        doc_type = "PDF"
                    elif "html" in content_type_header:
                        doc_type = "HTML"
                        soup = BeautifulSoup(resp.text, "html.parser")
                        
                        # Tenta extrair autor da página HTML
                        author_from_page = extract_author(soup)
                        if author_from_page:
                            author = author_from_page
                        
                        # Tenta extrair resumo completo da página HTML
                        extracted_page_abstract = extract_abstract(soup)
                        if extracted_page_abstract:
                            full_abstract = extracted_page_abstract
                        
                        # Se o ano não foi extraído da URL, tenta extrair do conteúdo (se implementado em extract_year)
                        # if not year and soup:
                        #     year = extract_year_from_soup(soup) # Função hipotética
                    else:
                        # Para outros tipos de conteúdo, tenta obter o tipo principal
                        doc_type = content_type_header.split("/")[0].upper() if "/" in content_type_header else content_type_header.upper()

                    # Se o autor não foi encontrado na página e o buscador é scholar, tenta obter da SerpAPI
                    if not author and search_engine_api == "google_scholar":
                        publication_info = item.get("publication_info", {})
                        if isinstance(publication_info.get("authors"), list):
                            authors_list = [auth.get("name") for auth in publication_info.get("authors") if auth.get("name")]
                            if authors_list:
                                author = ", ".join(authors_list)
                        # Fallback para o sumário da SerpAPI se autores não estiverem em 'authors'
                        elif not author and isinstance(publication_info.get("summary"), str):
                            summary_parts = publication_info.get("summary").split(" - ")
                            if len(summary_parts) > 0:
                                potential_authors = summary_parts[0].strip()
                                # Heurística para evitar nomes de periódicos ou strings muito longas
                                if (',' in potential_authors or ' and ' in potential_authors.lower() or 'et al' in potential_authors.lower() or len(potential_authors.split()) < 7) and \
                                   not any(char.isdigit() for char in potential_authors) and \
                                   len(potential_authors) < 150 and \
                                   potential_authors.lower() != "abstract" and \
                                   potential_authors.lower() != "introduction": # Evitar palavras comuns
                                    author = potential_authors
                    
                    # Se o ano ainda não foi encontrado, tenta obter do snippet do Google Scholar
                    if not year and search_engine_api == "google_scholar" and item.get("snippet"):
                        # Exemplo: "JM Viviescas, A Serna - 2023 - repositorio.unal.edu.co"
                        # Tenta extrair ano do snippet se contiver um padrão como " - ANO - "
                        snippet_year_match = re.search(r'\b(19\d{2}|20\d{2})\b', item.get("snippet", "")) # Use re.search directly
                        if snippet_year_match:
                            year = snippet_year_match.group(1)
                    
                    # Se doc_type ainda não foi definido pela requisição HEAD (ex: se extract_doc_type não foi chamado antes)
                    if not doc_type:
                        doc_type = extract_doc_type(link) # Chama extract_doc_type se ainda não tiver o tipo

                    base = extract_base(link)

                except requests.exceptions.Timeout:
                    _log.warning(f"Timeout ao tentar acessar {link}")
                    doc_type = "TIMEOUT" # Marca como timeout para análise posterior
                except requests.exceptions.HTTPError as http_err:
                    _log.warning(f"Erro HTTP {http_err.response.status_code} ao acessar {link}")
                    doc_type = f"HTTP_ERROR_{http_err.response.status_code}"
                except requests.exceptions.RequestException as req_err:
                    _log.warning(f"Falha na requisição para {link}: {req_err}")
                    doc_type = "REQUEST_ERROR"
                except Exception as e:
                    _log.warning(f"Falha geral ao processar dados de {link}: {e}")
                    doc_type = "PROCESSING_ERROR"
            else:
                _log.info(f"Resultado '{title}' sem link, pulando extração da página.")
                doc_type = "NO_LINK"


            results.append(SearchResult(
                title=title,
                author=author,
                abstract=full_abstract,
                source=source,
                year=year,
                doc_type=doc_type,
                base=base,
                link=link
            ))
            _log.info(f"Processado: {title[:60]}...")

        _log.info(f"Página {page+1} concluída. Pausando por {settings.PAUSE_SEC} segundos...")
        time.sleep(settings.PAUSE_SEC)

    csv_path = to_csv(results, engine_name=engine_name_for_file)
    _log.info(f"Arquivo final em: {csv_path}")

if __name__ == "__main__":
    # Exemplo de como definir settings.RESULTS_PER_PAGE se não estiver em config.py
    # Se settings.RESULTS_PER_PAGE não existir, defina um valor padrão aqui ou em config.py
    if not hasattr(settings, 'RESULTS_PER_PAGE'):
        settings.RESULTS_PER_PAGE = 10 # Valor padrão se não configurado
    run()