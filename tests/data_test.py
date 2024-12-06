import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from main import MetaboConverter, AdditionalFeatures  # Assume the GUI is saved as `ExcelSheetViewer.py`
import os
import pandas as pd

class TestProgram(unittest.TestCase):

    def setUp(self):
        """Set up the application for testing"""
        self.root = tk.Tk()
        self.app = MetaboConverter()
        self.app.master = self.root
        self.additional_features = AdditionalFeatures()
        self.additional_features.master = self.root

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

    @patch('tkinter.Toplevel')
    @patch('tkinter.ttk.Combobox')
    def test_select_sample_info_sheet(self, mock_combobox, mock_toplevel):
        """Test if the select_sample_info_sheet method opens a new window and initializes widgets properly"""
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window
        self.app.select_sample_info_sheet()
        mock_combobox.assert_called_once()
        mock_window.title.assert_called_once_with("Select Sample Info Sheet")

    @patch('tkinter.messagebox.showwarning')
    def test_process_sample_info_sheet_no_selection(self, mock_showwarning):
        """Test if the process_sample_info_sheet method shows warning when no sheet is selected"""
        self.app.selected_sample_info_sheet.set("")
        mock_window = MagicMock()
        self.app.process_sample_info_sheet(mock_window)
        mock_showwarning.assert_called_once_with("Warning", "Please select a sample info sheet.")

    @patch('tkinter.Toplevel')
    @patch('tkinter.Listbox')
    def test_group_intestine_groups(self, mock_listbox, mock_toplevel):
        """Test if the group_intestine_groups method opens a new window and initializes widgets properly"""
        mock_window = MagicMock()
        mock_toplevel.return_value = mock_window
        self.additional_features.cleaned_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.additional_features.group_intestine_groups()

        mock_listbox.assert_called_once()
        mock_window.title.assert_called_once_with("Select Intestine Groups to Group")

    @patch('tkinter.messagebox.showwarning')
    def test_save_grouped_columns_no_selection(self, mock_showwarning):
        """Test if the save_grouped_columns method shows warning when no columns are selected"""
        mock_listbox = MagicMock()
        mock_listbox.curselection.return_value = []
        self.additional_features.name_column = 'Name'
        self.additional_features.cleaned_data = pd.DataFrame({'Name': [1, 2, 3]})

        self.additional_features.save_grouped_columns(mock_listbox)
        mock_showwarning.assert_called_once_with("Warning", "Please select columns to group and ensure a name column was set.")

    @patch('tkinter.messagebox.showinfo')
    def test_perform_t_test_successful(self, mock_showinfo):
        """Test if the perform_t_test method completes successfully with two saved groups"""
        self.additional_features.saved_groups = {
            'Group1': pd.DataFrame({'Name': ['A', 'B'], 'Value': [1, 2]}),
            'Group2': pd.DataFrame({'Name': ['A', 'B'], 'Value': [3, 4]})
        }
        self.additional_features.name_column = 'Name'
        self.additional_features.perform_t_test()
        mock_showinfo.assert_called_once_with("T-Test Completed", "T-tests performed and significant results saved to Excel file.")
        
'''
@patch('tkinter.messagebox.showinfo')
@patch('tkinter.messagebox.showerror')
def test_normalize_concentration_successful(self, mock_showerror, mock_showinfo):
    """Test if the normalize_concentration method normalizes the data correctly and shows appropriate message"""
    # Adjusted DataFrame to match expected indexing in the normalize_concentration method
    self.app.sample_info_sheet = pd.DataFrame({
        'Intestine_Group': ['A', 'B', 'C'],
        'Weight': [1.0, 2.0, 3.0]
    })
    self.app.cleaned_data = pd.DataFrame({
        'A': [10, 20, 30],
        'B': [40, 50, 60],
        'C': [70, 80, 90]
    })
    self.app.group_intestine_button = MagicMock()  # Mock group_intestine_button

    # Ensure that the columns in cleaned_data match those in Intestine_Group
    self.app.cleaned_data = self.app.cleaned_data[['A', 'B', 'C']]

    try:
        self.app.normalize_concentration()
        mock_showinfo.assert_called_once_with("Info", "Normalization complete.")
        self.assertIsNotNone(self.app.cleaned_data)
    except Exception as e:
        mock_showerror.assert_called_once_with("Error", f"An error occurred during normalization: {e}")
'''

if __name__ == '__main__':
    unittest.main()
