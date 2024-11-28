import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import numpy as np
from scipy.stats import ttest_ind

class ExcelSheetViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Excel Sheet Viewer")
        self.geometry("600x600")
        # Your original code continues here...

        self.create_widgets()

        # Data Storage
        self.imported_data = {}
        self.cleaned_data = None
        self.sample_info_sheet = None
        self.weights = None
        self.saved_groups = {}

    def create_widgets(self):
         # Button to open the file
         self.open_button = tk.Button(self, text="Open Excel File", command=self.load_file)
         self.open_button.pack(pady=10)

         # Label for file path
         self.file_label = tk.Label(self, text="No file selected", wraplength=400)
         self.file_label.pack(pady=10)

         # Button to select sample info sheet (added)
         self.sample_info_button = tk.Button(self, text="Select Sample Info Sheet", command=self.select_sample_info_sheet, state='disabled')
         self.sample_info_button.pack(pady=5)

         # Button to select intestine groups to group (added)
         self.group_intestine_button = tk.Button(self, text="Group Intestine Groups", command=self.group_intestine_groups, state='disabled')
         self.group_intestine_button.pack(pady=5)

         # Button to clear data
         self.clear_button = tk.Button(self, text="Clear Data", command=self.clear_sheets)
         self.clear_button.pack(pady=10)

         # Button to view saved groups
         self.view_groups_button = tk.Button(self, text="View Saved Groups", command=self.view_saved_groups)
         self.view_groups_button.pack(pady=5)

         # Button to export saved groups
         self.export_groups_button = tk.Button(self, text="Export Saved Groups", command=self.export_saved_groups, state='disabled')
         self.export_groups_button.pack(pady=5)

         # Button to perform t-test analysis
         self.t_test_button = tk.Button(self, text="Perform T-Test", command=self.perform_t_test, state='disabled')
         self.t_test_button.pack(pady=5)

    def load_file(self):
         # Open file dialog to load Excel file
         file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

         if file_path:
             # Load Excel sheets
             try:
                 excel_data = pd.read_excel(file_path, sheet_name=None)
                 self.imported_data = excel_data
                 self.file_label.config(text=file_path)

                 # Step 1: Select raw data sheet
                 self.select_raw_data_sheet()

             except Exception as e:
                 messagebox.showerror("Error", f"Failed to load the file: {e}")

    def select_raw_data_sheet(self):
         # Ask user to select raw data sheet
         raw_data_window = tk.Toplevel(self)
         raw_data_window.title("Select Raw Data Sheet")
         raw_data_window.geometry("400x200")

         sheet_label = tk.Label(raw_data_window, text="Select the raw data sheet:")
         sheet_label.pack(pady=5)

         self.selected_raw_data_sheet = tk.StringVar(raw_data_window)
         sheet_dropdown = ttk.Combobox(raw_data_window, textvariable=self.selected_raw_data_sheet)
         sheet_dropdown['values'] = list(self.imported_data.keys())
         sheet_dropdown.pack(pady=5)

         select_button = tk.Button(raw_data_window, text="Select Sheet", command=lambda: self.process_raw_data(raw_data_window))
         select_button.pack(pady=10)

    def process_raw_data(self, raw_data_window):
         sheet_name = self.selected_raw_data_sheet.get()
         if sheet_name:
             self.raw_data = self.imported_data[sheet_name]
             raw_data_window.destroy()

             # Step 2: Ask user to select name column for removing duplicates
             self.select_name_column()
         else:
             messagebox.showwarning("Warning", "Please select a raw data sheet.")

    def select_name_column(self):
         # Ask user to select the name column
         name_window = tk.Toplevel(self)
         name_window.title("Select Name Column")
         name_window.geometry("400x200")

         column_label = tk.Label(name_window, text="Select the column for removing duplicates (e.g., Name column):")
         column_label.pack(pady=5)

         self.selected_name_column = tk.StringVar(name_window)
         column_dropdown = ttk.Combobox(name_window, textvariable=self.selected_name_column)
         column_dropdown['values'] = list(self.raw_data.columns)
         column_dropdown.pack(pady=5)

         remove_button = tk.Button(name_window, text="Remove Duplicates", command=lambda: self.remove_duplicates(name_window))
         remove_button.pack(pady=10)

    def remove_duplicates(self, name_window):
         selected_column = self.selected_name_column.get()
         if selected_column:
             # Remove duplicates based on selected column, keep first
             self.cleaned_data = self.raw_data.drop_duplicates(subset=[selected_column], keep='first')
             self.name_column = selected_column

             # Close window and proceed to next step
             name_window.destroy()
             messagebox.showinfo("Info", "Duplicates removed. Data has been cleaned.")

             # Step 3: Display cleaned data
             self.display_data(self.cleaned_data, "Cleaned Raw Data")

             # Enable button to select sample info sheet
             self.sample_info_button.config(state='normal')
         else:
             messagebox.showwarning("Warning", "Please select a column to proceed.")
    
    def select_sample_info_sheet(self):
         # Ask user to select sample info sheet
         sample_info_window = tk.Toplevel(self)
         sample_info_window.title("Select Sample Info Sheet")
         sample_info_window.geometry("400x200")

         sheet_label = tk.Label(sample_info_window, text="Select the sample info sheet:")
         sheet_label.pack(pady=5)

         self.selected_sample_info_sheet = tk.StringVar(sample_info_window)
         sheet_dropdown = ttk.Combobox(sample_info_window, textvariable=self.selected_sample_info_sheet)
         sheet_dropdown['values'] = list(self.imported_data.keys())
         sheet_dropdown.pack(pady=5)

         select_button = tk.Button(sample_info_window, text="Select Sheet", command=lambda: self.process_sample_info_sheet(sample_info_window))
         select_button.pack(pady=10)

    def process_sample_info_sheet(self, sample_info_window):
         sheet_name = self.selected_sample_info_sheet.get()
         if sheet_name:
             self.sample_info_sheet = self.imported_data[sheet_name]
             sample_info_window.destroy()

             # Step 5: Normalize concentration data by weight
             self.normalize_concentration()
         else:
             messagebox.showwarning("Warning", "Please select a sample info sheet.")

    def normalize_concentration(self):
         # Extract specific columns from sample info sheet
         try:
             group_names = self.sample_info_sheet.iloc[1:, 0].values
             intestine_groups = self.sample_info_sheet.iloc[1:, 3].values
             weights = self.sample_info_sheet.iloc[1:, 4].values

             # Normalize raw data by weight
             concentration_columns = [col for col in self.cleaned_data.columns if col in intestine_groups]
             normalized_data = self.cleaned_data.copy()

             for idx, group in enumerate(intestine_groups):
                 if group in concentration_columns:
                     normalized_data[group] = normalized_data[group] / weights[idx]

             self.cleaned_data = normalized_data
             messagebox.showinfo("Info", "Normalization complete.")

             # Step 6: Display normalized data
             self.display_data(self.cleaned_data, "Normalized Data")

             # Enable button to group intestine groups
             self.group_intestine_button.config(state='normal')
         except Exception as e:
             messagebox.showerror("Error", f"An error occurred during normalization: {e}")

    def group_intestine_groups(self):
         # Create a new window to select columns to group
         group_window = tk.Toplevel(self)
         group_window.title("Select Intestine Groups to Group")
         group_window.geometry("800x400")

         # Add a listbox to select multiple columns for grouping
         grouping_label = tk.Label(group_window, text="Select the intestine groups to group together:")
         grouping_label.pack(pady=5)

         self.selected_columns = tk.StringVar(value=list(self.cleaned_data.columns))
         column_listbox = tk.Listbox(group_window, listvariable=self.selected_columns, selectmode='multiple', exportselection=False)
         column_listbox.pack(pady=5, expand=True, fill='both')

         # Add an entry field to input the group name
         group_name_label = tk.Label(group_window, text="Enter a name for the grouped columns:")
         group_name_label.pack(pady=5)

         self.group_name_entry = tk.Entry(group_window)
         self.group_name_entry.pack(pady=5)

         # Add a button to save the selected columns as a separate table
         save_button = tk.Button(group_window, text="Save Grouped Columns", command=lambda: self.save_grouped_columns(column_listbox))
         save_button.pack(pady=10)

    def save_grouped_columns(self, column_listbox):
         selected_indices = column_listbox.curselection()
         selected_columns = [column_listbox.get(i) for i in selected_indices]

         if not selected_columns or not self.name_column:
             messagebox.showwarning("Warning", "Please select columns to group and ensure a name column was set.")
             return

         group_name = self.group_name_entry.get()

         if not group_name:
             messagebox.showwarning("Warning", "Please provide a name for the group.")
             return

         # Ensure that the Name column is included in the grouped columns
         if self.name_column not in selected_columns:
             selected_columns.insert(0, self.name_column)

         # Save the selected columns as a separate DataFrame
         grouped_data = self.cleaned_data[selected_columns]
         self.saved_groups[group_name] = grouped_data

         messagebox.showinfo("Group Saved", f"Grouped columns have been saved as '{group_name}'.")

         # Enable button to export saved groups and perform t-test
         self.export_groups_button.config(state='normal')
         self.t_test_button.config(state='normal')

    def perform_t_test(self):
         if len(self.saved_groups) < 2:
             messagebox.showwarning("Warning", "At least two groups are required to perform t-tests.")
             return

         results = []
         group_names = list(self.saved_groups.keys())

         # Compare each pair of saved groups
         for i in range(len(group_names)):
             for j in range(i + 1, len(group_names)):
                 group_1 = self.saved_groups[group_names[i]]
                 group_2 = self.saved_groups[group_names[j]]

                 common_metabolites = group_1[self.name_column]
                 t_test_results = []

                 # Perform t-test for each metabolite
                 for metabolite in common_metabolites:
                     values_1 = group_1.loc[group_1[self.name_column] == metabolite].iloc[:, 1:].values.flatten()
                     values_2 = group_2.loc[group_2[self.name_column] == metabolite].iloc[:, 1:].values.flatten()
                     t_stat, p_val = ttest_ind(values_1, values_2, equal_var=False)
                     t_test_results.append([metabolite, t_stat, p_val])

                 t_test_df = pd.DataFrame(t_test_results, columns=['Metabolite', 'T-Statistic', 'P-Value'])

                 # Adjust p-values using Benjamini-Hochberg correction
                 t_test_df['Adjusted P-Value'] = np.minimum(1, t_test_df['P-Value'] * len(t_test_df) / (np.arange(1, len(t_test_df) + 1)))

                 # Separate upregulators and downregulators
                 significant_up = t_test_df[(t_test_df['Adjusted P-Value'] < 0.05) & (t_test_df['T-Statistic'] > 0)]
                 significant_down = t_test_df[(t_test_df['Adjusted P-Value'] < 0.05) & (t_test_df['T-Statistic'] < 0)]

                 # Convert names to common names using PubChemPy
                 #significant_up['Common Name'] = significant_up['Metabolite'].apply(self.get_common_name)
                 #significant_down['Common Name'] = significant_down['Metabolite'].apply(self.get_common_name)

                 results.append((group_names[i], group_names[j], significant_up, significant_down))

         # Save the t-test results in an Excel file with separate sheets for upregulated and downregulated results
         directory_path = filedialog.askdirectory()
         if directory_path:
             file_path = os.path.join(directory_path, "t_test_significant_results.xlsx")
             with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                 for group_1, group_2, significant_up, significant_down in results:
                     # Save significant upregulators and downregulators in separate sheets
                     up_sheet_name = f"{group_1}_vs_{group_2}_upregulated"
                     down_sheet_name = f"{group_1}_vs_{group_2}_downregulated"
                     significant_up.to_excel(writer, sheet_name=up_sheet_name, index=False)
                     significant_down.to_excel(writer, sheet_name=down_sheet_name, index=False)

             messagebox.showinfo("T-Test Completed", "T-tests performed and significant results saved to Excel file.")

    # def get_common_name(self, compound_name):
    #     try:
    #         compound = pcp.get_compounds(compound_name, 'name')
    #        if compound:
    #             return compound[0].iupac_name
    #         else:
    #             return "Common name not found"
    #     except Exception as e:
    #         return "Error: " + str(e)

    def display_data(self, data, title):
         # Create a new top-level window for displaying data
         display_window = tk.Toplevel(self)
         display_window.title(title)
         display_window.geometry("800x400")

         # Create a Treeview widget for displaying the data
         tree = ttk.Treeview(display_window)
         tree.pack(expand=True, fill='both', pady=10)

         # Define columns
         tree["column"] = list(data.columns)
         tree["show"] = "headings"

         # Create headings based on the columns of the dataframe
         for col in data.columns:
             tree.heading(col, text=col)

         # Insert rows into the treeview
         for index, row in data.iterrows():
             tree.insert("", "end", values=list(row))

    def view_saved_groups(self):
         if not self.saved_groups:
             messagebox.showinfo("No Saved Groups", "No groups have been saved yet.")
             return

         # Create a new window to display saved groups
         saved_window = tk.Toplevel(self)
         saved_window.title("Saved Groups")
         saved_window.geometry("400x300")

         # Create buttons to display each saved group
         for group_name in self.saved_groups.keys():
             group_button = tk.Button(saved_window, text=f"View {group_name}", command=lambda name=group_name: self.display_saved_group(name))
             group_button.pack(pady=5)

    def display_saved_group(self, group_name):
         grouped_data = self.saved_groups[group_name]
         self.display_data(grouped_data, group_name)

    def export_saved_groups(self):
         if not self.saved_groups:
             messagebox.showinfo("No Saved Groups", "No groups have been saved yet.")
             return

         # Ask user to select a directory to save the Excel file
         directory_path = filedialog.askdirectory()

         if directory_path:
             # Create a file path in the selected directory
             file_path = os.path.join(directory_path, "saved_groups.xlsx")

             # Create an Excel writer object
             with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                 # Write each group to a separate sheet
                 for group_name, grouped_data in self.saved_groups.items():
                     grouped_data.to_excel(writer, sheet_name=group_name, index=False)

             messagebox.showinfo("Export Successful", f"Saved groups have been exported to '{file_path}'.")

    def clear_sheets(self):
         # Clear all data and reset UI
         self.imported_data = {}
         self.cleaned_data = None
         self.sample_info_sheet = None
         self.weights = None
         self.saved_groups = {}
         self.file_label.config(text="No file selected")

         # Disable buttons
         self.sample_info_button.config(state='disabled')
         self.group_intestine_button.config(state='disabled')
         self.export_groups_button.config(state='disabled')
         self.t_test_button.config(state='disabled')

         messagebox.showinfo("Cleared", "All data has been cleared.")

def runApp():
    app = ExcelSheetViewer()
    app.mainloop()