import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from ..utils import show_error_message

class PatientCRUD:
    def __init__(self, patient_module, auth_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent
        self.auth_module = auth_module

    def get_selected_patients(self):
        """Get a list of selected patient IDs"""
        return [patient_id for patient_id, var in self.patient_module.patient_vars.items() if var.get()]

    def load_patients(self):
        """Load patients from the database"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, admission_date, discharge_date FROM patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        return patients

    def on_patient_select(self):
        """Handle patient selection from checkbox"""
        selected_patients = self.get_selected_patients()
        
        if len(selected_patients) == 1:
            patient_id = selected_patients[0]
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            if patient:
                self.patient_module.name_var.set(patient[0])
                self.patient_module.admission_date_var.set(patient[1])
                self.patient_module.discharge_date_var.set(patient[2] or "")
                self.patient_module.current_patient_id = patient_id
                
                # Load items for all categories
                self.patient_module.stays_handler.load_stays()
                self.patient_module.items_handler.load_category_items("labs")
                self.patient_module.items_handler.load_category_items("drugs")
                self.patient_module.items_handler.load_category_items("radiology")
                self.patient_module.items_handler.load_category_items("consultations")
                self.patient_module.equipment_handler.load_patient_equipment()
        else:
            # Clear details if none or multiple are selected
            self.patient_module.name_var.set("")
            self.patient_module.admission_date_var.set("")
            self.patient_module.discharge_date_var.set("")
            if hasattr(self.patient_module, 'current_patient_id'):
                delattr(self.patient_module, 'current_patient_id')
            
            # Clear category lists
            self.patient_module.clear_all_tabs()

    def add_patient(self, name, admission_date):
        """Add a new patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO patients (name, admission_date) VALUES (?, ?)", (name, admission_date))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "CREATE_PATIENT", f"Created patient: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding patient: {e}")
            return False
        finally:
            conn.close()

    def get_patient(self, patient_id):
        """Get a single patient by ID"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, admission_date, discharge_date FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return patient

    def edit_patient(self, patient_id, name, admission_date, discharge_date):
        """Edit a patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE patients SET name = ?, admission_date = ?, discharge_date = ? WHERE id = ?", 
                           (name, admission_date, discharge_date, patient_id))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "UPDATE_PATIENT", f"Updated patient: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating patient: {e}")
            return False
        finally:
            conn.close()

    def delete_patient(self, patient_id):
        """Delete a patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
            patient_name = cursor.fetchone()[0]
            cursor.execute("DELETE FROM patient_stays WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patient_labs WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patient_drugs WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patient_radiology WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patient_consultations WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patient_equipment WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "DELETE_PATIENT", f"Deleted patient: {patient_name}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting patient: {e}")
            return False
        finally:
            conn.close()
