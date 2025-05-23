import unittest
import os
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from softscrape.config import Settings

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

    def test_serpapi_api_key_default(self):
        self.assertIsInstance(self.settings.SERPAPI_API_KEY, str)

    def test_query_default(self):
        expected_query = (
            '("Generative AI" OR "LLM" OR "Large Language Model" OR "AI Generative" OR "GENAI") '
            'AND ("productivity" OR "Efficiency") '
            'AND ("development teams" OR "software development" OR "software teams" OR developers)'
        )
        self.assertEqual(self.settings.QUERY, expected_query)

    def test_pages_default(self):
        self.assertEqual(self.settings.PAGES, 10)

    def test_pause_sec_default(self):
        self.assertEqual(self.settings.PAUSE_SEC, 1.0)

    def test_settings_instance_type(self):
        from softscrape.config import settings as global_settings
        self.assertIsInstance(global_settings, Settings)
