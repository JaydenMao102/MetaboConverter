import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from MetaboConverter import MetaboConverter  # Assume the GUI is saved as `ExcelSheetViewer.py`
import os

class TestProgram(unittest.TestCase):

    def setUp(self):
        """Set up the application for testing"""
        self.root = tk.Tk()
        self.app = MetaboConverter()
        self.app.master = self.root

        # Initializing StringVar attributes to avoid AttributeErrors
        self.app.selected_raw_data_sheet = tk.StringVar()
        self.app.selected_name_column = tk.StringVar()
        self.app.selected_sample_info_sheet = tk.StringVar()

        # Mock some data
        self.app.imported_data = {
            "Sheet1": MagicMock(),  # Mocking data for tests
            "Sheet2": MagicMock()
        }

    def tearDown(self):
        """Destroy the Tkinter root after each test"""
        self.app.destroy()
        self.root.destroy()

    @patch('tkinter.filedialog.askopenfilename')
    def test_load_file_successful(self, mock_askopenfilename):
        """Test if the load_file function correctly loads data"""
        mock_askopenfilename.return_value = 'test.xlsx'

        with patch('pandas.read_excel', return_value={"Sheet1": MagicMock()}):
            self.app.load_file()
        
        self.assertTrue(self.app.imported_data)
        self.assertEqual(self.app.file_label['text'], 'test.xlsx')
        self.assertIn('Sheet1', self.app.imported_data)

    def test_process_raw_data_with_valid_sheet(self):
        """Test the process_raw_data method with a valid sheet selection"""
        self.app.selected_raw_data_sheet.set("Sheet1")

        # Mock the window parameter
        mock_window = MagicMock()
        self.app.process_raw_data(mock_window)  # Using mock instead of None

        self.assertEqual(self.app.raw_data, self.app.imported_data["Sheet1"])
        mock_window.destroy.assert_called_once()  # Check if destroy was called

    @patch('tkinter.messagebox.showwarning')
    def test_process_raw_data_with_invalid_sheet(self, mock_showwarning):
        """Test if warning is displayed when no sheet is selected in process_raw_data"""
        self.app.selected_raw_data_sheet.set("")
        mock_window = MagicMock()
        self.app.process_raw_data(mock_window)
        mock_showwarning.assert_called_once_with("Warning", "Please select a raw data sheet.")

    @patch('tkinter.filedialog.askdirectory')
    def test_export_saved_groups(self, mock_askdirectory):
        """Test the export_saved_groups method for valid directory selection"""
        self.app.saved_groups = {
            'Group1': MagicMock(),
            'Group2': MagicMock()
        }
        mock_askdirectory.return_value = 'test_directory'

        with patch('pandas.ExcelWriter') as mock_writer:
            self.app.export_saved_groups()
            expected_path = os.path.normpath('test_directory/saved_groups.xlsx')
            mock_writer.assert_called_once_with(expected_path, engine='xlsxwriter')

    def test_clear_sheets(self):
        """Test if the clear_sheets method resets all data correctly"""
        self.app.cleaned_data = MagicMock()
        self.app.saved_groups = {"Group1": MagicMock()}
        self.app.clear_sheets()
        
        self.assertEqual(self.app.imported_data, {})
        self.assertIsNone(self.app.cleaned_data)
        self.assertEqual(self.app.saved_groups, {})
        self.assertEqual(self.app.file_label['text'], "No file selected")

    @patch('tkinter.messagebox.showinfo')
    def test_remove_duplicates_successful(self, mock_showinfo):
        """Test if duplicates are removed successfully and the appropriate message is shown"""
        self.app.raw_data = MagicMock()
        self.app.raw_data.drop_duplicates.return_value = MagicMock()
        self.app.selected_name_column.set('Name')

        # Mock the window parameter
        mock_window = MagicMock()
        self.app.remove_duplicates(mock_window)

        mock_showinfo.assert_called_once_with("Info", "Duplicates removed. Data has been cleaned.")
        mock_window.destroy.assert_called_once()  # Check if destroy was called
        self.assertIsNotNone(self.app.cleaned_data)

if __name__ == '__main__':
    unittest.main()
