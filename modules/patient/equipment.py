import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from ..utils import format_currency

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

        ttk.Label(add_frame, text="Start Date:").pack(side=tk.LEFT, padx=(10, 5))
        self.start_date_entry = DateEntry(add_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.start_date_entry.pack(side=tk.LEFT)

        ttk.Button(add_frame, text="Add Equipment", command=self.add_equipment).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_frame, text="Remove Selected", command=self.remove_equipment).pack(side=tk.LEFT, padx=(5, 0))

        list_frame = ttk.LabelFrame(parent, text="Assigned Equipment", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.equipment_tree = ttk.Treeview(list_frame, columns=("Name", "Start Date", "End Date", "Daily Price"), show="headings")
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Start Date", text="Start Date")
        self.equipment_tree.heading("End Date", text="End Date")
        self.equipment_tree.heading("Daily Price", text="Daily Price")
        self.equipment_tree.pack(fill=tk.BOTH, expand=True)

    def load_equipment_for_combo(self):
        """Load equipment into the combobox"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rental_price FROM equipment ORDER BY name")
        self.equipment_list = cursor.fetchall()
        conn.close()
        
        equipment_names = [f"{name} ({format_currency(price)})" for id, name, price in self.equipment_list]
        self.equipment_combo['values'] = equipment_names
        if equipment_names:
            self.equipment_combo.current(0)

    def add_equipment(self):
        """Add a new equipment record for the selected patient"""
        selected_patients = self.patient_module.crud_handler.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient.")
            return

        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        selected_equipment_text = self.equipment_var.get()
        
        if not start_date or not selected_equipment_text:
            messagebox.showerror("Error", "Please select a date and equipment.")
            return

        equipment_id = None
        daily_price = None
        for id, name, price in self.equipment_list:
            if f"{name} ({format_currency(price)})" == selected_equipment_text:
                equipment_id = id
                daily_price = price
                break
        
        if not equipment_id:
            messagebox.showerror("Error", "Invalid equipment selected.")
            return

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            for patient_id in selected_patients:
                cursor.execute("INSERT INTO patient_equipment (patient_id, equipment_id, start_date, daily_rental_price) VALUES (?, ?, ?, ?)", 
                               (patient_id, equipment_id, start_date, daily_price))
            conn.commit()
            messagebox.showinfo("Success", "Equipment added successfully.")
            if len(selected_patients) == 1:
                self.load_patient_equipment()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add equipment: {e}")
        finally:
            conn.close()

    def remove_equipment(self):
        """Remove the selected equipment record"""
        selected_item = self.equipment_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select equipment to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this equipment?"):
            record_id = self.equipment_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM patient_equipment WHERE id = ?", (record_id,))
                conn.commit()
                messagebox.showinfo("Success", "Equipment removed successfully.")
                self.load_patient_equipment()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to remove equipment: {e}")
            finally:
                conn.close()

    def load_patient_equipment(self):
        """Load equipment records for the selected patient"""
        for i in self.equipment_tree.get_children():
            self.equipment_tree.delete(i)

        if not hasattr(self.patient_module, 'current_patient_id'):
            return

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT pe.id, e.name, pe.start_date, pe.end_date, pe.daily_rental_price
            FROM patient_equipment pe
            JOIN items_db.equipment e ON pe.equipment_id = e.id
            WHERE pe.patient_id = ?
            ORDER BY pe.start_date
        """, (self.patient_module.current_patient_id,))
        
        for row in cursor.fetchall():
            self.equipment_tree.insert("", "end", values=row)
        conn.close()
