import os
from datetime import datetime
import pandas as pd
from typing import List
from .models import SearchResult
from .logger import get_logger

_log = get_logger("Exporter")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

def to_csv(results: List[SearchResult], prefix: str = "resultados_pesquisa", engine_name: str = "google") -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{engine_name}_{ts}.csv"
    path = os.path.join(OUTPUT_DIR, filename)
    
    if not results:
        # Create DataFrame with columns from SearchResult model if results is empty
        df = pd.DataFrame(columns=list(SearchResult.__annotations__.keys()))
    else:
        df = pd.DataFrame([r.__dict__ for r in results])
        
    df.to_csv(path, index=False)
    _log.info(f"CSV salvo em '{path}'")
    return path