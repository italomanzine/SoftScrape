import unittest
from dataclasses import fields
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from softscrape.models import SearchResult

class TestModels(unittest.TestCase):

    def test_search_result_creation_and_attributes(self):
        title = "Test Title"
        author = "Test Author"
        abstract = "Test Abstract"
        source = "Test Source"
        year = "2023"
        doc_type = "Test Doc Type"
        base = "Test Base"
        link = "http://example.com/test"

        result = SearchResult(
            title=title,
            author=author,
            abstract=abstract,
            source=source,
            year=year,
            doc_type=doc_type,
            base=base,
            link=link
        )

        self.assertEqual(result.title, title)
        self.assertEqual(result.author, author)
        self.assertEqual(result.abstract, abstract)
        self.assertEqual(result.source, source)
        self.assertEqual(result.year, year)
        self.assertEqual(result.doc_type, doc_type)
        self.assertEqual(result.base, base)
        self.assertEqual(result.link, link)

    def test_search_result_dataclass_fields(self):
        expected_fields = ['title', 'author', 'abstract', 'source', 'year', 'doc_type', 'base', 'link']
        actual_fields = [field.name for field in fields(SearchResult)]
        self.assertListEqual(sorted(actual_fields), sorted(expected_fields))

    def test_search_result_empty_values(self):
        result = SearchResult(
            title="",
            author="",
            abstract="",
            source="",
            year="",
            doc_type="",
            base="",
            link=""
        )
        self.assertEqual(result.title, "")
        self.assertEqual(result.author, "")
        self.assertEqual(result.abstract, "")
        self.assertEqual(result.source, "")
        self.assertEqual(result.year, "")
        self.assertEqual(result.doc_type, "")
        self.assertEqual(result.base, "")
        self.assertEqual(result.link, "")
