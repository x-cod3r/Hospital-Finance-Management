import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message

class InterventionsHandler:
    def __init__(self, nurse_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent

    def load_interventions(self):
        """Load interventions from the database"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        return interventions

    def add_intervention(self, nurse_id, patient_id, date, intervention_id):
        """Add a new intervention for a nurse"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO nurse_interventions (nurse_id, patient_id, date, intervention_id)
                VALUES (?, ?, ?, ?)
            """, (nurse_id, patient_id, date, intervention_id))
            conn.commit()
            
            cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor.execute("SELECT name FROM interventions_db.interventions WHERE id = ?", (intervention_id,))
            intervention_name = cursor.fetchone()[0]
            self.nurse_module.auth_module.log_action(self.nurse_module.auth_module.current_user, "ADD_INTERVENTION", f"Added intervention {intervention_name} for nurse ID {nurse_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding intervention: {e}")
            return False
        finally:
            conn.close()
