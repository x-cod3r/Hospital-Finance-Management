import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message
from ..utils import format_currency

class DoctorCRUD:
    def __init__(self, doctor_module, auth_module):
        self.doctor_module = doctor_module
        self.parent = doctor_module.parent
        self.auth_module = auth_module

    def get_selected_doctors(self):
        """Get a list of selected doctor IDs"""
        return [doc_id for doc_id, var in self.doctor_module.doctor_vars.items() if var.get()]

    def load_doctors(self):
        """Load doctors from the database"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, hourly_rate FROM doctors ORDER BY name")
        doctors = cursor.fetchall()
        conn.close()
        return doctors

    def on_doctor_select(self, doctor_id):
        """Handle doctor selection from checkbox"""
        if self.doctor_module.doctor_vars[doctor_id].get():
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (doctor_id,))
            doctor = cursor.fetchone()
            conn.close()
            
            if doctor:
                self.doctor_module.name_var.set(doctor[0])
                self.doctor_module.rate_var.set(format_currency(doctor[1]))
                self.doctor_module.current_doctor_id = doctor_id
        else:
            if hasattr(self.doctor_module, 'current_doctor_id') and self.doctor_module.current_doctor_id == doctor_id:
                self.doctor_module.name_var.set("")
                self.doctor_module.rate_var.set("")
                delattr(self.doctor_module, 'current_doctor_id')

    def add_doctor(self, name, rate):
        """Add a new doctor"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO doctors (name, hourly_rate) VALUES (?, ?)", (name, rate))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "CREATE_DOCTOR", f"Created doctor: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding doctor: {e}")
            return False
        finally:
            conn.close()

    def get_doctor(self, doctor_id):
        """Get a single doctor by ID"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, hourly_rate FROM doctors WHERE id = ?", (doctor_id,))
        doctor = cursor.fetchone()
        conn.close()
        return doctor

    def edit_doctor(self, doctor_id, name, rate):
        """Edit a doctor"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE doctors SET name = ?, hourly_rate = ? WHERE id = ?", (name, rate, doctor_id))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "UPDATE_DOCTOR", f"Updated doctor: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating doctor: {e}")
            return False
        finally:
            conn.close()

    def delete_doctor(self, doctor_id):
        """Delete a doctor"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM doctors WHERE id = ?", (doctor_id,))
            doctor_name = cursor.fetchone()[0]
            cursor.execute("DELETE FROM doctor_shifts WHERE doctor_id = ?", (doctor_id,))
            cursor.execute("DELETE FROM doctor_interventions WHERE doctor_id = ?", (doctor_id,))
            cursor.execute("DELETE FROM doctor_payments WHERE doctor_id = ?", (doctor_id,))
            cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "DELETE_DOCTOR", f"Deleted doctor: {doctor_name}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting doctor: {e}")
            return False
        finally:
            conn.close()
