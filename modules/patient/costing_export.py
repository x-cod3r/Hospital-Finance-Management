import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import openpyxl
from ..utils import format_currency, calculate_hours

class CostingExportHandler:
    def __init__(self, patient_module):
        self.patient_module = patient_module

    def export_cost_sheet(self):
        """Export cost sheet for selected patient"""
        selected_patients = self.patient_module.crud_handler.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to export a cost sheet")
            return
        self.patient_module.current_patient_id = selected_patients[0]

        conn_patients = sqlite3.connect("db/patients.db")
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (self.patient_module.current_patient_id,))
        patient = cursor_patients.fetchone()
        if not patient:
            conn_patients.close()
            return
        name, admission_date, discharge_date = patient

        conn_items = sqlite3.connect("db/items.db")
        cursor_items = conn_items.cursor()
        cursor_patients.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor_patients.execute("""
            SELECT ps.stay_date, cl.name, cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
            ORDER BY ps.stay_date
        """, (self.patient_module.current_patient_id,))
        stays = cursor_patients.fetchall()
        total_stay_cost = sum(row[2] for row in stays)

        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0
        category_details = {}
        for category in categories:
            cursor_patients.execute(f"SELECT item_id, quantity, date FROM patient_{category} WHERE patient_id = ? ORDER BY date", (self.patient_module.current_patient_id,))
            items = cursor_patients.fetchall()
            category_cost = 0.0
            details = []
            if items:
                for item_id, quantity, date in items:
                    cursor_items.execute("SELECT name, price FROM items WHERE id = ?", (item_id,))
                    item_result = cursor_items.fetchone()
                    if item_result:
                        item_name, price = item_result
                        total = quantity * price
                        category_cost += total
                        details.append((date, item_name, quantity, price, total))
            category_costs[category] = category_cost
            category_details[category] = details
            total_category_cost += category_cost
        conn_items.close()
        conn_patients.close()

        doctor_details = self.get_staff_cost_details("doctor")
        nurse_details = self.get_staff_cost_details("nurse")
        equipment_details = self.get_equipment_cost_details()
        total_doctor_cost = doctor_details["total_cost"]
        total_nurse_cost = nurse_details["total_cost"]
        total_equipment_cost = equipment_details["total_cost"]

        total_cost = total_stay_cost + total_category_cost + total_doctor_cost + total_nurse_cost + total_equipment_cost

        filename = f"{name}_cost_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Cost Sheet"
            
            sheet.append(["Patient Cost Sheet"])
            sheet.append([])
            sheet.append(["Patient Name:", name])
            sheet.append(["Admission Date:", admission_date])
            sheet.append(["Discharge Date:", discharge_date or 'N/A'])
            sheet.append([])
            sheet.append(["Cost Breakdown:"])
            sheet.append([f"Stays ({len(stays)} days):", format_currency(total_stay_cost)])
            if stays:
                sheet.append(["  Date", "Care Level", "Cost"])
                for date, level, cost in stays:
                    sheet.append([f"  {date}", level, format_currency(cost)])
            sheet.append([])
            for category in categories:
                sheet.append([f"{category.capitalize()}:", format_currency(category_costs[category])])
                if category_details[category]:
                    sheet.append(["  Date", "Item", "Quantity", "Price", "Total"])
                    for item in category_details[category]:
                        date, item_name, qty, price, total = item
                        sheet.append([f"  {date}", item_name, qty, format_currency(price), format_currency(total)])
                sheet.append([])
            
            self.append_staff_details_to_sheet(sheet, "Doctor", doctor_details)
            self.append_staff_details_to_sheet(sheet, "Nurse", nurse_details)
            self.append_equipment_details_to_sheet(sheet, "Equipment", equipment_details)

            sheet.append(["Total Cost:", format_currency(total_cost)])

            workbook.save(filename)
            messagebox.showinfo("Export Success", f"Cost sheet exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export cost sheet: {e}")

    def get_equipment_cost_details(self):
        details = {"total_cost": 0.0, "equipment": []}
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT e.name, pe.start_date, pe.end_date, pe.daily_rental_price
            FROM patient_equipment pe
            JOIN items_db.equipment e ON pe.equipment_id = e.id
            WHERE pe.patient_id = ?
        """, (self.patient_module.current_patient_id,))
        
        for name, start_date, end_date, daily_price in cursor.fetchall():
            # Since each record is a daily charge, days is always 1
            days = 1
            cost = daily_price
            details["total_cost"] += cost
            details["equipment"].append((name, start_date, end_date, days, daily_price, cost))
            
        conn.close()
        return details

    def get_staff_cost_details(self, staff_type):
        details = {"total_cost": 0.0, "shifts": [], "interventions": []}
        try:
            conn = sqlite3.connect(f"db/{staff_type}s.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT {staff_type}_id, arrival_datetime, leave_datetime FROM {staff_type}_shifts WHERE patient_id = ?", (self.patient_module.current_patient_id,))
            shifts = cursor.fetchall()
            total_shift_cost = 0.0
            for staff_id, arrival, leave in shifts:
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                leave_dt = datetime.strptime(leave, "%Y-%m-%d %H:%M:%S")
                hours = calculate_hours(arrival_dt, leave_dt)
                cursor.execute(f"SELECT name, hourly_rate FROM {staff_type}s WHERE id = ?", (staff_id,))
                rate_res = cursor.fetchone()
                if rate_res:
                    staff_name, rate = rate_res
                    cost = hours * rate
                    total_shift_cost += cost
                    details["shifts"].append((arrival, leave, staff_name, hours, rate, cost))
            
            cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor.execute(f"SELECT i.name, i.bonus_amount, si.date, s.name FROM {staff_type}_interventions si JOIN interventions_db.interventions i ON si.intervention_id = i.id JOIN {staff_type}s s ON si.{staff_type}_id = s.id WHERE si.patient_id = ?", (self.patient_module.current_patient_id,))
            interventions = cursor.fetchall()
            total_intervention_cost = sum(i[1] for i in interventions)
            details["interventions"] = [(date, name, staff_name, bonus) for name, bonus, date, staff_name in interventions]
            details["total_cost"] = total_shift_cost + total_intervention_cost
            conn.close()
        except sqlite3.Error as e:
            print(f"Error calculating {staff_type} costs: {e}")
        return details

    def append_staff_details_to_sheet(self, sheet, staff_title, details):
        sheet.append([f"{staff_title} Costs:", format_currency(details['total_cost'])])
        if details['shifts']:
            sheet.append([f"  {staff_title} Shifts"])
            sheet.append(["    Arrival", "Leave", staff_title, "Hours", "Rate", "Cost"])
            for arrival, leave, name, hours, rate, cost in details['shifts']:
                sheet.append([f"    {arrival}", leave, name, f"{hours:.2f}", format_currency(rate), format_currency(cost)])
        if details['interventions']:
            sheet.append([f"  {staff_title} Interventions"])
            sheet.append(["    Date", "Intervention", staff_title, "Bonus"])
            for date, int_name, name, bonus in details['interventions']:
                sheet.append([f"    {date}", int_name, name, format_currency(bonus)])
        sheet.append([])

    def append_equipment_details_to_sheet(self, sheet, title, details):
        sheet.append([f"{title} Costs:", format_currency(details['total_cost'])])
        if details['equipment']:
            sheet.append([f"  {title}"])
            sheet.append(["    Name", "Start Date", "End Date", "Days", "Daily Price", "Cost"])
            for name, start_date, end_date, days, daily_price, cost in details['equipment']:
                sheet.append([f"    {name}", start_date, end_date or 'N/A', days, format_currency(daily_price), format_currency(cost)])
        sheet.append([])
