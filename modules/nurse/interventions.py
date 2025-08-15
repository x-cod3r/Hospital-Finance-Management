import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class InterventionsHandler:
    def __init__(self, nurse_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent

    def load_interventions(self):
        """Load interventions into combobox"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        
        self.nurse_module.intervention_combo['values'] = [i[0] for i in interventions]

    def add_intervention(self):
        """Add intervention for selected nurses"""
        selected_nurses = self.nurse_module.crud_handler.get_selected_nurses()
        if not selected_nurses:
            messagebox.showwarning("Warning", "Please select at least one nurse")
            return
        
        date = self.nurse_module.intervention_date_var.get().strip()
        intervention_name = self.nurse_module.intervention_var.get().strip()
        
        if not date or not intervention_name:
            messagebox.showerror("Error", "Please select date and intervention")
            return
        
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM interventions WHERE name = ?", (intervention_name,))
        intervention = cursor.fetchone()
        conn.close()
        
        if not intervention:
            messagebox.showerror("Error", "Invalid intervention selected")
            return
        
        intervention_id = intervention[0]

        patient_text = self.nurse_module.intervention_patient_var.get()
        if not patient_text:
            messagebox.showerror("Error", "Please select a patient")
            return
        patient_id = int(patient_text.split(":")[0])
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            for nurse_id in selected_nurses:
                cursor.execute("""
                    INSERT INTO nurse_interventions (nurse_id, patient_id, date, intervention_id)
                    VALUES (?, ?, ?, ?)
                """, (nurse_id, patient_id, date, intervention_id))
            conn.commit()
            messagebox.showinfo("Success", f"Intervention added for {len(selected_nurses)} nurses successfully")
            
            self.nurse_module.intervention_var.set("")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add intervention: {e}")
        finally:
            conn.close()
