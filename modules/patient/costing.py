import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ..utils import format_currency, calculate_hours
from .costing_export import CostingExportHandler

class CostingHandler:
    def __init__(self, patient_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent
        self.export_handler = CostingExportHandler(patient_module)

    def calculate_cost(self):
        """Calculate total cost for selected patient"""
        selected_patients = self.patient_module.crud_handler.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to calculate cost")
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

        cursor_patients.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor_patients.execute("""
            SELECT cl.daily_rate, ps.stay_date
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
        """, (self.patient_module.current_patient_id,))
        stays_data = cursor_patients.fetchall()
        stay_costs = [row[0] for row in stays_data]
        stay_dates = [datetime.strptime(row[1], "%Y-%m-%d").date() for row in stays_data]
        total_stay_cost = sum(stay_costs)

        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0

        for category in categories:
            cursor_patients.execute(f"SELECT item_id, quantity FROM patient_{category} WHERE patient_id = ?", (self.patient_module.current_patient_id,))
            items = cursor_patients.fetchall()
            category_cost = 0.0
            if items:
                conn_items = sqlite3.connect("db/items.db")
                cursor_items = conn_items.cursor()
                for item_id, quantity in items:
                    cursor_items.execute("SELECT price FROM items WHERE id = ?", (item_id,))
                    price_result = cursor_items.fetchone()
                    if price_result:
                        category_cost += quantity * price_result[0]
                conn_items.close()
            category_costs[category] = category_cost
            total_category_cost += category_cost
        conn_patients.close()

        total_doctor_cost = self.calculate_staff_cost("doctor")
        total_nurse_cost = self.calculate_staff_cost("nurse")
        total_equipment_cost = self.calculate_equipment_cost(stay_dates)

        total_cost = total_stay_cost + total_category_cost + total_doctor_cost + total_nurse_cost + total_equipment_cost

        result_text = f"""
Patient: {name}
Admission: {admission_date}
Discharge: {discharge_date or 'N/A'}

Cost Breakdown:
Stays ({len(stay_costs)} days): {format_currency(total_stay_cost)}
Labs: {format_currency(category_costs['labs'])}
Drugs: {format_currency(category_costs['drugs'])}
Radiology: {format_currency(category_costs['radiology'])}
Consultations: {format_currency(category_costs['consultations'])}
Doctor Costs: {format_currency(total_doctor_cost)}
Nurse Costs: {format_currency(total_nurse_cost)}
Equipment Costs: {format_currency(total_equipment_cost)}

Total Cost: {format_currency(total_cost)}
        """
        messagebox.showinfo("Cost Calculation", result_text)

    def calculate_equipment_cost(self, stay_dates):
        """Calculate total equipment cost for the selected patient for the duration of their stay"""
        total_cost = 0.0
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT daily_rental_price FROM patient_equipment WHERE patient_id = ?", (self.patient_module.current_patient_id,))
        equipment_rentals = cursor.fetchall()
        conn.close()

        for rental in equipment_rentals:
            total_cost += rental[0]

        return total_cost

    def calculate_staff_cost(self, staff_type):
        total_cost = 0.0
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
                cursor.execute(f"SELECT hourly_rate FROM {staff_type}s WHERE id = ?", (staff_id,))
                rate_res = cursor.fetchone()
                if rate_res:
                    total_shift_cost += hours * rate_res[0]
            
            cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor.execute(f"SELECT i.bonus_amount FROM {staff_type}_interventions si JOIN interventions_db.interventions i ON si.intervention_id = i.id WHERE si.patient_id = ?", (self.patient_module.current_patient_id,))
            interventions = cursor.fetchall()
            total_intervention_cost = sum(i[0] for i in interventions)
            total_cost = total_shift_cost + total_intervention_cost
            conn.close()
        except sqlite3.Error as e:
            print(f"Error calculating {staff_type} costs: {e}")
        return total_cost

    def export_cost_sheet(self):
        """Export cost sheet for selected patient"""
        self.export_handler.export_cost_sheet()
