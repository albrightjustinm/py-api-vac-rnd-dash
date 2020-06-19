"""
Basic unittests for Various Tranform Helper in Common object standardization
"""

import unittest
from api.utils.transform import clean_country



class CommonObjectStandardizationTest(unittest.TestCase):

    def setUp(self):
        self.set_countries_null = ''
        self.set_countries_null_multiple = ','
        self.set_countries_simple = 'United States, united kingdom'
        self.set_countries_with_null = 'Australia,, United States'
        self.set_countries_full = 'Japan, japn, Korea, north korea, netherlands'

    def test_null_countries(self):
        self.assertIsNone(clean_country(self.set_countries_null))
        self.assertIsNone(clean_country(self.set_countries_null_multiple))

    def test_country_lookup(self):
        print(clean_country(self.set_countries_simple))
        print(clean_country(self.set_countries_full))
        
        # Test with partial null fields
        lc = clean_country(self.set_countries_with_null)
        print(lc)
