import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from ..utils import format_currency, show_error_message

class EquipmentHandler:
    def __init__(self, patient_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent

    def setup_equipment_tab(self, parent):
        """Setup the patient equipment tab"""
        add_frame = ttk.Frame(parent, padding="5")
        add_frame.pack(fill=tk.X)

        ttk.Label(add_frame, text="Equipment:").pack(side=tk.LEFT, padx=(0, 5))
        self.equipment_var = tk.StringVar()
        self.equipment_combo = ttk.Combobox(add_frame, textvariable=self.equipment_var, state="readonly")
        self.equipment_combo.pack(side=tk.LEFT)
        self.load_equipment_for_combo()

        ttk.Button(add_frame, text="Add Equipment for Today", command=self.add_equipment).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_frame, text="Remove Selected", command=self.remove_equipment).pack(side=tk.LEFT, padx=(5, 0))

        self.confirm_button = ttk.Button(add_frame, text="Confirm Stay & Equipment", command=self.confirm_stay_and_equipment)
        self.confirm_button.pack(side=tk.LEFT, padx=(10, 0))
        self.confirm_button.pack_forget()

        list_frame = ttk.LabelFrame(parent, text="Assigned Equipment", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.equipment_tree = ttk.Treeview(list_frame, columns=("Name", "Start Date", "End Date", "Daily Price"), show="headings")
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Start Date", text="Start Date")
        self.equipment_tree.heading("End Date", text="End Date")
        self.equipment_tree.heading("Daily Price", text="Daily Price")
        self.equipment_tree.pack(fill=tk.BOTH, expand=True)

    def load_equipment(self):
        """Load equipment from the database"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rental_price FROM equipment ORDER BY name")
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def add_equipment(self, patient_id, equipment_id, start_date, end_date, daily_price):
        """Add a new equipment record for a patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO patient_equipment (patient_id, equipment_id, start_date, end_date, daily_rental_price) VALUES (?, ?, ?, ?, ?)", 
                           (patient_id, equipment_id, start_date, end_date, daily_price))
            conn.commit()
            
            cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
            cursor.execute("SELECT name FROM items_db.equipment WHERE id = ?", (equipment_id,))
            equipment_name = cursor.fetchone()[0]
            self.patient_module.auth_module.log_action(self.patient_module.auth_module.current_user, "ADD_EQUIPMENT", f"Added equipment {equipment_name} for patient ID {patient_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding equipment: {e}")
            return False
        finally:
            conn.close()

    def remove_equipment(self, record_id):
        """Remove an equipment record"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT patient_id, equipment_id FROM patient_equipment WHERE id = ?", (record_id,))
            patient_id, equipment_id = cursor.fetchone()
            
            cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
            cursor.execute("SELECT name FROM items_db.equipment WHERE id = ?", (equipment_id,))
            equipment_name = cursor.fetchone()[0]

            cursor.execute("DELETE FROM patient_equipment WHERE id = ?", (record_id,))
            conn.commit()
            self.patient_module.auth_module.log_action(self.patient_module.auth_module.current_user, "REMOVE_EQUIPMENT", f"Removed equipment {equipment_name} for patient ID {patient_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error removing equipment: {e}")
            return False
        finally:
            conn.close()

    def load_patient_equipment(self, patient_id):
        """Load equipment records for a specific patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT pe.id, e.name, pe.start_date, pe.end_date, pe.daily_rental_price
            FROM patient_equipment pe
            JOIN items_db.equipment e ON pe.equipment_id = e.id
            WHERE pe.patient_id = ?
            ORDER BY pe.start_date
        """, (patient_id,))
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def load_defaults_for_stay(self, stay_date, care_level_id):
        """Load default equipment for a new stay."""
        self.stay_date = stay_date
        self.care_level_id = care_level_id
        self.confirm_button.pack(side=tk.LEFT, padx=(10, 0))

        for i in self.equipment_tree.get_children():
            self.equipment_tree.delete(i)

        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.name, e.daily_rental_price
            FROM care_level_equipment cle
            JOIN equipment e ON cle.equipment_id = e.id
            WHERE cle.care_level_id = ?
        """, (care_level_id,))
        
        for row in cursor.fetchall():
            self.equipment_tree.insert("", "end", iid=row[0], values=(row[1], stay_date.strftime('%Y-%m-%d'), "", format_currency(row[2])))
        conn.close()

    def confirm_stay_and_equipment(self):
        """Save the stay and the equipment list to the database."""
        patient_id = self.patient_module.current_patient_id
        stay_date = self.stay_date
        end_date = stay_date + timedelta(days=1)
        stay_date_str = stay_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            # Add the stay
            cursor.execute("INSERT INTO patient_stays (patient_id, stay_date, care_level_id) VALUES (?, ?, ?)",
                           (patient_id, stay_date_str, self.care_level_id))
            self.patient_module.auth_module.log_action(self.patient_module.auth_module.current_user, "ADD_STAY", f"Added stay for patient ID {patient_id} on {stay_date_str}")

            # Add the equipment
            for item in self.equipment_tree.get_children():
                values = self.equipment_tree.item(item, 'values')
                equipment_name = values[0]
                price_str = values[3]
                price = float(price_str.replace("$", "").replace(",", ""))

                # Get equipment_id from the equipment_list
                equipment_id = None
                for eid, name, _ in self.equipment_list:
                    if name == equipment_name:
                        equipment_id = eid
                        break
                
                if equipment_id:
                    cursor.execute("""
                        INSERT INTO patient_equipment 
                        (patient_id, equipment_id, start_date, end_date, daily_rental_price, stay_date) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (patient_id, equipment_id, stay_date_str, end_date_str, price, stay_date_str))

            conn.commit()
            messagebox.showinfo("Success", "Stay and equipment confirmed successfully.")
            self.confirm_button.pack_forget()
            self.patient_module.stays_handler.load_stays()
            self.load_patient_equipment()
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to confirm stay: {e}")
        finally:
            conn.close()
