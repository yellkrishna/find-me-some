# tests/test_data_collection.py
import unittest
from ai_modules.data_collection import get_google_places_details

class TestDataCollection(unittest.TestCase):
    def test_get_google_places_details_valid(self):
        business_name = "Example Business"
        address = "123 Example Street"
        result = get_google_places_details(business_name, address)
        self.assertIn("name", result)
        self.assertIn("formatted_address", result)

    def test_get_google_places_details_invalid(self):
        business_name = "Nonexistent Business"
        address = "Nowhere"
        with self.assertRaises(Exception):
            get_google_places_details(business_name, address)

if __name__ == '__main__':
    unittest.main()
