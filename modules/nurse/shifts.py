import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ..utils import show_error_message
from ..utils import calculate_hours

class ShiftsHandler:
    def __init__(self, nurse_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent
        self.nurse_levels = self.get_nurse_levels()

    def get_nurse_levels(self):
        """Fetch nurse levels from the database"""
        try:
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, level_name, hourly_rate FROM nurse_levels")
            levels = {f"{name} ({rate}/hr)": id for id, name, rate in cursor.fetchall()}
            conn.close()
            return levels
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to fetch nurse levels: {e}")
            return {}

    def check_shift_overlap(self, nurse_id, arrival_datetime, leave_datetime):
        """Check for overlapping shifts"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM nurse_shifts
            WHERE nurse_id = ? AND (
                (arrival_datetime <= ? AND leave_datetime >= ?) OR
                (arrival_datetime <= ? AND leave_datetime >= ?) OR
                (arrival_datetime >= ? AND leave_datetime <= ?)
            )
        """, (nurse_id, arrival_datetime, arrival_datetime, leave_datetime, leave_datetime, arrival_datetime, leave_datetime))
        overlap = cursor.fetchone()
        conn.close()
        return overlap is not None

    def add_shift(self):
        """Add shift for selected nurses"""
        selected_nurses = self.nurse_module.crud_handler.get_selected_nurses()
        if not selected_nurses:
            messagebox.showwarning("Warning", "Please select at least one nurse")
            return

        try:
            arrival_date_str = self.nurse_module.arrival_date_var.get().strip()
            arrival_time_str = self.nurse_module.arrival_time_var.get().strip() or "09:00"
            arrival_ampm = self.nurse_module.arrival_ampm_var.get()

            leave_date_str = self.nurse_module.leave_date_var.get().strip()
            leave_time_str = self.nurse_module.leave_time_var.get().strip() or "09:00"
            leave_ampm = self.nurse_module.leave_ampm_var.get()

            if not all([arrival_date_str, leave_date_str, leave_time_str]):
                show_error_message("Error", "Please fill in all shift details")
                return

            arrival_datetime_str = f"{arrival_date_str} {arrival_time_str} {arrival_ampm}"
            leave_datetime_str = f"{leave_date_str} {leave_time_str} {leave_ampm}"

            arrival_datetime = datetime.strptime(arrival_datetime_str, "%Y-%m-%d %I:%M %p")
            leave_datetime = datetime.strptime(leave_datetime_str, "%Y-%m-%d %I:%M %p")

            patient_text = self.nurse_module.shift_patient_var.get()
            if not patient_text:
                show_error_message("Error", "Please select a patient")
                return
            patient_id = int(patient_text.split(":")[0])

            level_text = self.nurse_module.nurse_level_var.get()
            if not level_text:
                show_error_message("Error", "Please select a nurse level")
                return
            nurse_level_id = self.nurse_levels.get(level_text)

            hours = calculate_hours(arrival_datetime, leave_datetime)
            
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            
            success_count = 0
            fail_count = 0

            for nurse_id in selected_nurses:
                if self.check_shift_overlap(nurse_id, arrival_datetime, leave_datetime):
                    fail_count += 1
                    continue

                cursor.execute("""
                    INSERT INTO nurse_shifts (nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id))
                success_count += 1
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Shifts added for {success_count} nurses. Failed for {fail_count} nurses. ({hours} hours each)")

            self.nurse_module.arrival_time_var.set("")
            self.nurse_module.leave_time_var.set("")

        except ValueError:
            show_error_message("Error", "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.")
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to add shift: {e}")

    def remove_shift(self):
        """Remove selected shift"""
        selected_items = self.nurse_module.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a shift to remove")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to remove the selected shift(s)?"):
            return

        try:
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            
            for item in selected_items:
                shift_id = self.nurse_module.tree.item(item, "values")[0]
                cursor.execute("DELETE FROM nurse_shifts WHERE id = ?", (shift_id,))
            
            conn.commit()
            conn.close()
            
            self.nurse_module.crud_handler.view_nurses() # Refresh view
            messagebox.showinfo("Success", "Shift(s) removed successfully")

        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to remove shift: {e}")
