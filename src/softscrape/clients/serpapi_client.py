import requests
from typing import Any, Dict
from config import settings
from logger import get_logger

_log = get_logger("SerpApiClient")

class SerpApiClient:
    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str = settings.SERPAPI_API_KEY):
        if not api_key:
            raise ValueError("SERPAPI_API_KEY não definido.")
        self.api_key = api_key

    def search(
        self,
        query: str,
        start: int,
        num: int = 10,
        hl: str = "pt",
        gl: str = "br"
    ) -> Dict[str, Any]:
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "start": start,
            "num": num,
            "hl": hl,
            "gl": gl
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()