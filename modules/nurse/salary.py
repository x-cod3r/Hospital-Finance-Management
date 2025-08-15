import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl
from ..utils import format_currency, calculate_salary_details, export_to_pdf, show_error_message

class SalaryHandler:
    def __init__(self, nurse_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent

    def calculate_salary(self):
        """Calculate salary for selected nurse"""
        selected_nurses = self.nurse_module.crud_handler.get_selected_nurses()
        if len(selected_nurses) != 1:
            messagebox.showwarning("Warning", "Please select exactly one nurse to calculate salary")
            return
        self.nurse_module.current_nurse_id = selected_nurses[0]

        start_date = self.nurse_module.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.nurse_module.end_date_entry.get_date().strftime('%Y-%m-%d')

        salary_details = calculate_salary_details("nurse", self.nurse_module.current_nurse_id, start_date, end_date)

        if not salary_details:
            show_error_message("Error", "Could not calculate salary.")
            return

        result_text = f"""
Nurse: {salary_details['name']}
Period: {start_date} to {end_date}

Total Hours: {salary_details['total_hours']:.2f}
Hourly Rate: {format_currency(salary_details['hourly_rate'])}
Base Salary: {format_currency(salary_details['base_salary'])}

Bonus from Interventions: {format_currency(salary_details['total_bonus'])}
Total Salary: {format_currency(salary_details['total_salary'])}
        """

        messagebox.showinfo("Salary Calculation", result_text)

    def export_salary_sheet(self, export_format):
        """Export salary sheet for selected nurse"""
        selected_nurses = self.nurse_module.crud_handler.get_selected_nurses()
        if len(selected_nurses) != 1:
            messagebox.showwarning("Warning", "Please select exactly one nurse to export salary sheet")
            return
        self.nurse_module.current_nurse_id = selected_nurses[0]

        start_date = self.nurse_module.start_date_entry.get_date().strftime('%Y-%m-%d')
        end_date = self.nurse_module.end_date_entry.get_date().strftime('%Y-%m-%d')

        salary_details = calculate_salary_details("nurse", self.nurse_module.current_nurse_id, start_date, end_date)

        if not salary_details:
            show_error_message("Error", "Could not export salary sheet.")
            return

        filename = f"{salary_details['name']}_salary_{start_date}_to_{end_date}.{export_format}"

        if export_format == 'xlsx':
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Salary Sheet"

                sheet.append(["Nurse Salary Sheet"])
                sheet.append([])
                sheet.append(["Nurse Name:", salary_details['name']])
                sheet.append(["Period:", f"{start_date} to {end_date}"])
                sheet.append([])
                sheet.append(["Total Hours:", f"{salary_details['total_hours']:.2f}"])
                sheet.append(["Hourly Rate:", format_currency(salary_details['hourly_rate'])])
                sheet.append(["Base Salary:", format_currency(salary_details['base_salary'])])
                sheet.append(["Bonus from Interventions:", format_currency(salary_details['total_bonus'])])
                sheet.append(["Total Salary:", format_currency(salary_details['total_salary'])])
                sheet.append([])
                sheet.append(["Shifts"])
                sheet.append(["Arrival", "Leave", "Patient", "Hours"])
                for shift in salary_details['shifts']:
                    sheet.append([shift['arrival'], shift['leave'], shift['patient'], shift['hours']])
                sheet.append([])
                sheet.append(["Interventions"])
                sheet.append(["Date", "Intervention", "Patient", "Bonus"])
                for intervention in salary_details['interventions']:
                    sheet.append([intervention['date'], intervention['name'], intervention['patient'], format_currency(intervention['bonus'])])

                workbook.save(filename)
                messagebox.showinfo("Export Success", f"Salary sheet exported to {filename}")
            except Exception as e:
                show_error_message("Export Error", f"Failed to export salary sheet: {e}")
        elif export_format == 'pdf':
            data = [
                "Nurse Salary Sheet",
                "",
                f"Nurse Name: {salary_details['name']}",
                f"Period: {start_date} to {end_date}",
                "",
                f"Total Hours: {salary_details['total_hours']:.2f}",
                f"Hourly Rate: {format_currency(salary_details['hourly_rate'])}",
                f"Base Salary: {format_currency(salary_details['base_salary'])}",
                f"Bonus from Interventions: {format_currency(salary_details['total_bonus'])}",
                f"Total Salary: {format_currency(salary_details['total_salary'])}",
            ]
            try:
                export_to_pdf(filename, data)
                messagebox.showinfo("Export Success", f"Salary sheet exported to {filename}")
            except Exception as e:
                show_error_message("Export Error", f"Failed to export salary sheet: {e}")
