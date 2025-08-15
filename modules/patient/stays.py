import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from ..utils import format_currency, show_error_message

class StaysHandler:
    def __init__(self, patient_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent

    def setup_stays_tab(self, parent):
        """Setup the patient stays tab"""
        add_frame = ttk.Frame(parent, padding="5")
        add_frame.pack(fill=tk.X)

        ttk.Label(add_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.stay_date_entry = DateEntry(add_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.stay_date_entry.pack(side=tk.LEFT)

        ttk.Label(add_frame, text="Care Level:").pack(side=tk.LEFT, padx=(10, 5))
        self.stay_care_level_var = tk.StringVar()
        self.stay_care_level_combo = ttk.Combobox(add_frame, textvariable=self.stay_care_level_var, state="readonly")
        self.stay_care_level_combo.pack(side=tk.LEFT)
        self.load_care_levels_for_combo()

        ttk.Button(add_frame, text="Add Stay", command=self.add_stay).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_frame, text="Remove Selected Stay", command=self.remove_stay).pack(side=tk.LEFT, padx=(5, 0))

        list_frame = ttk.LabelFrame(parent, text="Recorded Stays", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.stays_tree = ttk.Treeview(list_frame, columns=("Date", "Care Level", "Cost"), show="headings")
        self.stays_tree.heading("Date", text="Date")
        self.stays_tree.heading("Care Level", text="Care Level")
        self.stays_tree.heading("Cost", text="Cost")
        self.stays_tree.pack(fill=tk.BOTH, expand=True)

    def load_care_levels_for_combo(self):
        """Load care levels into the combobox"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        self.care_levels = cursor.fetchall()
        conn.close()
        
        level_names = [f"{name} ({format_currency(rate)})" for id, name, rate in self.care_levels]
        self.stay_care_level_combo['values'] = level_names
        if level_names:
            self.stay_care_level_combo.current(0)

    def add_stay(self):
        """Start the process of adding a new stay by switching to the equipment tab."""
        selected_patients = self.patient_module.crud_handler.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to add a stay.")
            return

        stay_date = self.stay_date_entry.get_date()
        selected_level_text = self.stay_care_level_var.get()
        
        if not stay_date or not selected_level_text:
            show_error_message("Error", "Please select a date and care level.")
            return

        care_level_id = None
        for id, name, rate in self.care_levels:
            if f"{name} ({format_currency(rate)})" == selected_level_text:
                care_level_id = id
                break
        
        if not care_level_id:
            show_error_message("Error", "Invalid care level selected.")
            return

        self.patient_module.switch_to_equipment_tab_for_stay(stay_date, care_level_id)

    def remove_stay(self):
        """Remove the selected stay record"""
        selected_item = self.stays_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stay to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this stay record?"):
            item_data = self.stays_tree.item(selected_item)
            stay_date = item_data['values'][0]

            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM patient_stays WHERE patient_id = ? AND stay_date = ?", (self.patient_module.current_patient_id, stay_date))
                conn.commit()
                messagebox.showinfo("Success", "Stay record removed successfully.")
                self.load_stays()
            except sqlite3.Error as e:
                show_error_message("Error", f"Failed to remove stay: {e}")
            finally:
                conn.close()

    def load_stays(self):
        """Load stay records for the selected patient"""
        for i in self.stays_tree.get_children():
            self.stays_tree.delete(i)

        if not hasattr(self.patient_module, 'current_patient_id'):
            return

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT ps.stay_date, cl.name, cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
            ORDER BY ps.stay_date
        """, (self.patient_module.current_patient_id,))
        
        for row in cursor.fetchall():
            self.stays_tree.insert("", "end", values=(row[0], row[1], format_currency(row[2])))
        conn.close()
