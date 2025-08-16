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

    def load_care_levels(self):
        """Load care levels from the database"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        care_levels = cursor.fetchall()
        conn.close()
        return care_levels

    def add_stay(self, patient_id, stay_date, care_level_id, current_user):
        """Add a new stay for a patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO patient_stays (patient_id, stay_date, care_level_id) VALUES (?, ?, ?)",
                           (patient_id, stay_date, care_level_id))
            conn.commit()
            self.patient_module.auth_module.log_action(current_user, "ADD_STAY", f"Added stay for patient ID {patient_id} on {stay_date}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding stay: {e}")
            return False
        finally:
            conn.close()

    def remove_stay(self, stay_id, current_user):
        """Remove a stay record"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT patient_id, stay_date FROM patient_stays WHERE id = ?", (stay_id,))
            result = cursor.fetchone()
            if result:
                patient_id, stay_date = result
                cursor.execute("DELETE FROM patient_stays WHERE id = ?", (stay_id,))
                conn.commit()
                self.patient_module.auth_module.log_action(current_user, "REMOVE_STAY", f"Removed stay for patient ID {patient_id} on {stay_date}")
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"Error removing stay: {e}")
            return False
        finally:
            conn.close()

    def load_stays(self, patient_id):
        """Load stay records for a specific patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT ps.id, ps.stay_date, cl.name, cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
            ORDER BY ps.stay_date
        """, (patient_id,))
        stays = cursor.fetchall()
        conn.close()
        return stays
