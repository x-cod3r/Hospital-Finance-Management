import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message

class InterventionsHandler:
    def __init__(self, doctor_module):
        self.doctor_module = doctor_module
        self.parent = doctor_module.parent

    def load_interventions(self):
        """Load interventions from the database"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        return interventions

    def add_intervention(self, doctor_id, patient_id, date, intervention_id):
        """Add a new intervention for a doctor"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO doctor_interventions (doctor_id, patient_id, date, intervention_id)
                VALUES (?, ?, ?, ?)
            """, (doctor_id, patient_id, date, intervention_id))
            conn.commit()
            
            cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor.execute("SELECT name FROM interventions_db.interventions WHERE id = ?", (intervention_id,))
            intervention_name = cursor.fetchone()[0]
            self.doctor_module.auth_module.log_action(self.doctor_module.auth_module.current_user, "ADD_INTERVENTION", f"Added intervention {intervention_name} for doctor ID {doctor_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding intervention: {e}")
            return False
        finally:
            conn.close()
