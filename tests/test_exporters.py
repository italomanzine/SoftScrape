import unittest
import os
import pandas as pd
from datetime import datetime
from typing import List
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from softscrape.models import SearchResult
from softscrape.exporters import to_csv, OUTPUT_DIR

class TestExporters(unittest.TestCase):

    def setUp(self):
        self.results = [
            SearchResult(title="Test Title 1", author="Author A", abstract="Abstract 1", source="Source X", year="2023", doc_type="Article", base="DB1", link="http://example.com/1"),
            SearchResult(title="Test Title 2", author="Author B", abstract="Abstract 2", source="Source Y", year="2024", doc_type="Paper", base="DB2", link="http://example.com/2")
        ]
        self.prefix = "test_export"
        self.engine_name = "test_engine"
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def tearDown(self):
        for item in os.listdir(OUTPUT_DIR):
            if item.startswith(self.prefix) and item.endswith(".csv"):
                os.remove(os.path.join(OUTPUT_DIR, item))

    def test_to_csv_creates_file(self):
        path = to_csv(self.results, prefix=self.prefix, engine_name=self.engine_name)
        self.assertTrue(os.path.exists(path))

    def test_to_csv_filename_convention(self):
        ts_before = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = to_csv(self.results, prefix=self.prefix, engine_name=self.engine_name)
        ts_after = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = os.path.basename(path)
        
        # Extract timestamp string (e.g., YYYYMMDD_HHMMSS)
        # The timestamp consists of two parts: date and time, joined by an underscore.
        parts_for_ts = filename.replace(".csv", "").split('_')
        file_ts_str = "_".join(parts_for_ts[-2:]) # Gets the last two elements (date_time)

        # Expected name part before timestamp
        expected_name_part = f"{self.prefix}_{self.engine_name}"
        # Actual name part from filename by removing the timestamp and .csv extension
        actual_name_part = filename.replace(f"_{file_ts_str}.csv", "")
        
        self.assertEqual(actual_name_part, expected_name_part)
        
        # Check if the time part of the timestamp in the filename is plausible
        # We compare the HHMMSS part.
        self.assertTrue(ts_before.split('_')[1] <= file_ts_str.split('_')[1] <= ts_after.split('_')[1])
        self.assertTrue(filename.endswith(".csv"))

    def test_to_csv_content_correct(self):
        path = to_csv(self.results, prefix=self.prefix, engine_name=self.engine_name)
        df = pd.read_csv(path)
        
        self.assertEqual(len(df), len(self.results))
        for i, res in enumerate(self.results):
            self.assertEqual(df.loc[i, 'title'], res.title)
            self.assertEqual(df.loc[i, 'author'], res.author)
            self.assertEqual(df.loc[i, 'abstract'], res.abstract)
            self.assertEqual(df.loc[i, 'source'], res.source)
            self.assertEqual(str(df.loc[i, 'year']), res.year) # Convert df value to string
            self.assertEqual(df.loc[i, 'doc_type'], res.doc_type)
            self.assertEqual(df.loc[i, 'base'], res.base)
            self.assertEqual(df.loc[i, 'link'], res.link)

    def test_to_csv_empty_results(self):
        empty_results: List[SearchResult] = []
        path = to_csv(empty_results, prefix=self.prefix, engine_name=self.engine_name)
        self.assertTrue(os.path.exists(path))
        df = pd.read_csv(path) # This should now work due to the fix in exporters.py
        self.assertEqual(len(df), 0)
        expected_columns = list(SearchResult.__annotations__.keys())
        self.assertListEqual(list(df.columns), expected_columns)
