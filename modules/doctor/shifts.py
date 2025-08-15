import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ..utils import show_error_message
from ..utils import calculate_hours

class ShiftsHandler:
    def __init__(self, doctor_module):
        self.doctor_module = doctor_module
        self.parent = doctor_module.parent

    def check_shift_overlap(self, doctor_id, arrival_datetime, leave_datetime):
        """Check for overlapping shifts with a 20-minute tolerance."""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT arrival_datetime, leave_datetime FROM doctor_shifts WHERE doctor_id = ?", (doctor_id,))
        existing_shifts = cursor.fetchall()
        conn.close()

        for existing_arrival_str, existing_leave_str in existing_shifts:
            existing_arrival = datetime.strptime(existing_arrival_str, "%Y-%m-%d %H:%M:%S")
            existing_leave = datetime.strptime(existing_leave_str, "%Y-%m-%d %H:%M:%S")

            overlap_start = max(arrival_datetime, existing_arrival)
            overlap_end = min(leave_datetime, existing_leave)

            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                if overlap_duration.total_seconds() / 60 > 20:
                    return True  # Overlap is more than 20 minutes
        
        return False # No overlap or overlap is within tolerance

    def add_shift(self):
        """Add shift for selected doctors"""
        selected_doctors = self.doctor_module.crud_handler.get_selected_doctors()
        if not selected_doctors:
            messagebox.showwarning("Warning", "Please select at least one doctor")
            return

        try:
            arrival_date_str = self.doctor_module.arrival_date_var.get().strip()
            arrival_time_str = self.doctor_module.arrival_time_var.get().strip() or "09:00"
            arrival_ampm = self.doctor_module.arrival_ampm_var.get()

            leave_date_str = self.doctor_module.leave_date_var.get().strip()
            leave_time_str = self.doctor_module.leave_time_var.get().strip() or "09:00"
            leave_ampm = self.doctor_module.leave_ampm_var.get()

            if not all([arrival_date_str, arrival_time_str, leave_date_str, leave_time_str]):
                show_error_message("Error", "Please fill in all shift details")
                return

            arrival_datetime_str = f"{arrival_date_str} {arrival_time_str} {arrival_ampm}"
            leave_datetime_str = f"{leave_date_str} {leave_time_str} {leave_ampm}"

            arrival_datetime = datetime.strptime(arrival_datetime_str, "%Y-%m-%d %I:%M %p")
            leave_datetime = datetime.strptime(leave_datetime_str, "%Y-%m-%d %I:%M %p")

            patient_text = self.doctor_module.shift_patient_var.get()
            if not patient_text:
                show_error_message("Error", "Please select a patient")
                return
            patient_id = int(patient_text.split(":")[0])

            hours = calculate_hours(arrival_datetime, leave_datetime)
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            
            success_count = 0
            fail_count = 0

            for doctor_id in selected_doctors:
                if self.check_shift_overlap(doctor_id, arrival_datetime, leave_datetime):
                    fail_count += 1
                    continue

                cursor.execute("""
                    INSERT INTO doctor_shifts (doctor_id, patient_id, arrival_datetime, leave_datetime)
                    VALUES (?, ?, ?, ?)
                """, (doctor_id, patient_id, arrival_datetime, leave_datetime))
                success_count += 1
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Shifts added for {success_count} doctors. Failed for {fail_count} doctors. ({hours} hours each)")

            self.doctor_module.arrival_time_var.set("")
            self.doctor_module.leave_time_var.set("")

        except ValueError:
            show_error_message("Error", "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.")
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to add shift: {e}")

    def remove_shift(self):
        """Remove selected shift"""
        selected_items = self.doctor_module.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a shift to remove")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to remove the selected shift(s)?"):
            return

        try:
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            
            for item in selected_items:
                shift_id = self.doctor_module.tree.item(item, "values")[0]
                cursor.execute("DELETE FROM doctor_shifts WHERE id = ?", (shift_id,))
            
            conn.commit()
            conn.close()
            
            self.doctor_module.crud_handler.view_doctors() # Refresh view
            messagebox.showinfo("Success", "Shift(s) removed successfully")

        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to remove shift: {e}")
