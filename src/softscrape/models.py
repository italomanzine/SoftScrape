from dataclasses import dataclass

@dataclass
class SearchResult:
    title: str
    author: str
    abstract: str
    source: str
    year: str
    doc_type: str
    base: str
    link: str