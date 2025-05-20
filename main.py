import requests
from bs4 import BeautifulSoup
import pandas as pd
from htmldate import find_date
from urllib.parse import urlparse
from tqdm import tqdm
import logging
import time

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Sua chave de API do SerpApi
API_KEY = '701a34750412f80527d6a45394bd0fdd7eeef89bce0a1a9393ff1ba62274693f'

# String de busca
query = '("Generative AI" OR "LLM" OR "Large Language Model" OR "AI Generative" OR "GENAI") AND ("productivity" OR "Efficiency") AND ("development teams" OR "software development" OR "software teams" OR developers)'

# Lista para armazenar os resultados
resultados = []

# Função para extrair o autor da página
def extrair_autor(soup):
    metadados_autor = [
        {'name': 'author'},
        {'property': 'article:author'},
        {'name': 'dc.creator'},
        {'name': 'byline'},
        {'name': 'sailthru.author'}
    ]
    for metadado in metadados_autor:
        tag = soup.find('meta', attrs=metadado)
        if tag and tag.get('content'):
            return tag['content'].strip()
    return ''

# Função para extrair o ano de publicação
def extrair_ano(url):
    try:
        data = find_date(url)
        if data:
            return data[:4]  # Retorna apenas o ano
    except:
        pass
    return ''

# Função para determinar o tipo de documento
def determinar_tipo_documento(url):
    try:
        response = requests.head(url, timeout=10)
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' in content_type:
            return 'PDF'
        elif 'html' in content_type:
            return 'HTML'
        elif 'json' in content_type:
            return 'JSON'
        else:
            return content_type.split('/')[0].upper()
    except:
        return ''

# Função para extrair a base (domínio) da URL
def extrair_base(url):
    try:
        dominio = urlparse(url).netloc
        return dominio
    except:
        return ''

# Percorrer as 10 primeiras páginas (0 a 9)
for page in tqdm(range(10), desc="Páginas do Google"):
    params = {
        'engine': 'google',
        'q': query,
        'api_key': API_KEY,
        'start': page * 10,
        'num': 10,
        'hl': 'pt',
        'gl': 'br'
    }

    try:
        response = requests.get('https://serpapi.com/search', params=params)
        data = response.json()
    except Exception as e:
        logging.error(f"Erro ao buscar dados da página {page + 1}: {e}")
        continue

    # Verificar se há resultados orgânicos
    if 'organic_results' in data:
        for result in tqdm(data['organic_results'], desc=f"Resultados da página {page + 1}", leave=False):
            titulo = result.get('title')
            link = result.get('link')
            snippet = result.get('snippet')
            fonte = result.get('displayed_link')

            # Inicializa os campos adicionais
            autor = ''
            ano = ''
            tipo_documento = ''
            base = ''

            # Tenta acessar a página para extrair informações adicionais
            try:
                pagina = requests.get(link, timeout=10)
                soup = BeautifulSoup(pagina.text, 'html.parser')

                autor = extrair_autor(soup)
                ano = extrair_ano(link)
                tipo_documento = determinar_tipo_documento(link)
                base = extrair_base(link)
            except Exception as e:
                logging.warning(f"Erro ao processar o link {link}: {e}")

            resultados.append({
                'Nome do Artigo': titulo,
                'Autor': autor,
                'Resumo (Abstract)': snippet,
                'Fonte': fonte,
                'Ano': ano,
                'Tipo de Documento': tipo_documento,
                'Base': base,
                'Link': link
            })

            logging.info(f"Processado: {titulo}")

    time.sleep(1)  # Pausa para evitar sobrecarga nas requisições

# Criar DataFrame e salvar em CSV
df = pd.DataFrame(resultados)
df.to_csv('resultados_pesquisa.csv', index=False)
logging.info("Arquivo CSV 'resultados_pesquisa.csv' criado com sucesso.")
