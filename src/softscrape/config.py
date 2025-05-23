import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    # COLOQUE AQUI A QUERY QUE DESEJA PESQUISAR
    # Exemplo: "Generative AI" AND "productivity" AND "software development"
    QUERY: str = (
        '("Generative AI" OR "LLM" OR "Large Language Model" OR "AI Generative" OR "GENAI") '
        'AND ("productivity" OR "Efficiency") '
        'AND ("development teams" OR "software development" OR "software teams" OR developers)'
    )
    # COLOQUE AQUI O NUMERO DE PÁGINAS QUE DESEJA PESQUISAR
    # Exemplo: 10
    PAGES: int = 10
    PAUSE_SEC: float = 1.0

settings = Settings()