import unittest
import pandas as pd
from gui_widgets import WidgetsSetup

class TestDisplayData(unittest.TestCase):
    def setUp(self):
        # Initialize WidgetsSetup manually
        self.widget_setup = WidgetsSetup()

    def test_display_data_valid_input(self):
        # Test display_data with valid input dataframe
        sample_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        title = "Sample Data"

        self.assertIsInstance(sample_data, pd.DataFrame, "Data should be a pandas DataFrame")
        self.assertIsInstance(title, str, "Title should be a string")
        
    def test_display_data_invalid_input(self):
        # Test display_data with invalid input (non-DataFrame)
        invalid_data = [1, 2, 3]  # This should be a DataFrame
        title = 1

        with self.assertRaises(Exception):
            self.widget_setup.display_data(data=invalid_data, title=title)

if __name__ == "__main__":
    unittest.main()