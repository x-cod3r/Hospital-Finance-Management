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

    def get_shifts_for_doctor(self, doctor_id):
        """Fetch all shifts for a specific doctor."""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, patient_id, arrival_datetime, leave_datetime 
                FROM doctor_shifts 
                WHERE doctor_id = ?
            """, (doctor_id,))
            shifts = cursor.fetchall()
            return shifts
        except sqlite3.Error as e:
            print(f"Error fetching shifts: {e}")
            return []
        finally:
            conn.close()

    def add_shift(self, doctor_id, patient_id, arrival_datetime, leave_datetime):
        """Add a new shift for a doctor"""
        if self.check_shift_overlap(doctor_id, arrival_datetime, leave_datetime):
            return False

        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO doctor_shifts (doctor_id, patient_id, arrival_datetime, leave_datetime)
                VALUES (?, ?, ?, ?)
            """, (doctor_id, patient_id, arrival_datetime, leave_datetime))
            conn.commit()
            self.doctor_module.auth_module.log_action(self.doctor_module.auth_module.current_user, "ADD_SHIFT", f"Added shift for doctor ID {doctor_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding shift: {e}")
            return False
        finally:
            conn.close()

    def remove_shift(self, shift_id):
        """Remove a shift"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT doctor_id FROM doctor_shifts WHERE id = ?", (shift_id,))
            doctor_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM doctor_shifts WHERE id = ?", (shift_id,))
            conn.commit()
            self.doctor_module.auth_module.log_action(self.doctor_module.auth_module.current_user, "REMOVE_SHIFT", f"Removed shift for doctor ID {doctor_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error removing shift: {e}")
            return False
        finally:
            conn.close()
