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
        """Check for overlapping shifts with a 20-minute tolerance."""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT arrival_datetime, leave_datetime FROM nurse_shifts WHERE nurse_id = ?", (nurse_id,))
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

    def get_shifts_for_nurse(self, nurse_id):
        """Fetch all shifts for a specific nurse."""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, patient_id, arrival_datetime, leave_datetime, nurse_level_id 
                FROM nurse_shifts 
                WHERE nurse_id = ?
            """, (nurse_id,))
            shifts = cursor.fetchall()
            return shifts
        except sqlite3.Error as e:
            print(f"Error fetching shifts: {e}")
            return []
        finally:
            conn.close()

    def add_shift(self, nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id):
        """Add a new shift for a nurse"""
        if self.check_shift_overlap(nurse_id, arrival_datetime, leave_datetime):
            return False

        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO nurse_shifts (nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id)
                VALUES (?, ?, ?, ?, ?)
            """, (nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id))
            conn.commit()
            self.nurse_module.auth_module.log_action(self.nurse_module.auth_module.current_user, "ADD_SHIFT", f"Added shift for nurse ID {nurse_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding shift: {e}")
            return False
        finally:
            conn.close()

    def remove_shift(self, shift_id):
        """Remove a shift"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nurse_id FROM nurse_shifts WHERE id = ?", (shift_id,))
            nurse_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM nurse_shifts WHERE id = ?", (shift_id,))
            conn.commit()
            self.nurse_module.auth_module.log_action(self.nurse_module.auth_module.current_user, "REMOVE_SHIFT", f"Removed shift for nurse ID {nurse_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error removing shift: {e}")
            return False
        finally:
            conn.close()
