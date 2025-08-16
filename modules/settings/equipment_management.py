import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message

class EquipmentManagementHandler:
    def __init__(self, settings_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent

    def setup_equipment_tab(self, parent):
        """Setup equipment management UI"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Equipment list
        equipment_frame = ttk.LabelFrame(main_frame, text="Master Equipment List", padding="10")
        equipment_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.equipment_tree = ttk.Treeview(equipment_frame, columns=("Name", "Daily Price"), show="headings")
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Daily Price", text="Daily Price")
        self.equipment_tree.pack(fill=tk.BOTH, expand=True)
        self.load_equipment()

        buttons_frame = ttk.Frame(equipment_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_equipment).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_equipment).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_equipment).pack(side=tk.LEFT)

        # Care level equipment assignment
        assignment_frame = ttk.LabelFrame(main_frame, text="Assign to Care Level", padding="10")
        assignment_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        ttk.Label(assignment_frame, text="Care Level:").pack(anchor=tk.W)
        self.care_level_var = tk.StringVar()
        self.care_level_combo = ttk.Combobox(assignment_frame, textvariable=self.care_level_var, state="readonly")
        self.care_level_combo.pack(fill=tk.X, pady=(0, 10))
        self.load_care_levels()
        self.care_level_combo.bind("<<ComboboxSelected>>", self.load_assigned_equipment)

        self.assigned_equipment_tree = ttk.Treeview(assignment_frame, columns=("Name",), show="headings")
        self.assigned_equipment_tree.heading("Name", text="Assigned Equipment")
        self.assigned_equipment_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(assignment_frame, text="Assign Selected Equipment", command=self.assign_equipment).pack(pady=5)
        ttk.Button(assignment_frame, text="Unassign Selected Equipment", command=self.unassign_equipment).pack()

    def load_equipment(self):
        """Load equipment from the database"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rental_price FROM equipment ORDER BY name")
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def add_equipment(self, name, price):
        """Add new equipment"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO equipment (name, daily_rental_price) VALUES (?, ?)", (name, price))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "CREATE_EQUIPMENT", f"Created equipment: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding equipment: {e}")
            return False
        finally:
            conn.close()

    def get_equipment(self, equipment_id):
        """Get a single piece of equipment by ID"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rental_price FROM equipment WHERE id = ?", (equipment_id,))
        equipment = cursor.fetchone()
        conn.close()
        return equipment

    def edit_equipment(self, equipment_id, name, price):
        """Edit equipment"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE equipment SET name = ?, daily_rental_price = ? WHERE id = ?", (name, price, equipment_id))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "UPDATE_EQUIPMENT", f"Updated equipment: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating equipment: {e}")
            return False
        finally:
            conn.close()

    def delete_equipment(self, equipment_id):
        """Delete equipment"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM equipment WHERE id = ?", (equipment_id,))
            name = cursor.fetchone()[0]
            cursor.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
            cursor.execute("DELETE FROM care_level_equipment WHERE equipment_id = ?", (equipment_id,))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "DELETE_EQUIPMENT", f"Deleted equipment: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting equipment: {e}")
            return False
        finally:
            conn.close()

    def load_care_levels(self):
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM care_levels ORDER BY name")
        self.care_levels = cursor.fetchall()
        conn.close()
        self.care_level_combo['values'] = [name for id, name in self.care_levels]

    def load_assigned_equipment(self, event=None):
        for i in self.assigned_equipment_tree.get_children():
            self.assigned_equipment_tree.delete(i)

        care_level_name = self.care_level_var.get()
        if not care_level_name:
            return

        care_level_id = [id for id, name in self.care_levels if name == care_level_name][0]

        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.name FROM care_level_equipment cle
            JOIN equipment e ON cle.equipment_id = e.id
            WHERE cle.care_level_id = ?
        """, (care_level_id,))
        for row in cursor.fetchall():
            self.assigned_equipment_tree.insert("", "end", values=(row[0],))
        conn.close()

    def assign_equipment(self):
        selected_equipment = self.equipment_tree.focus()
        if not selected_equipment:
            messagebox.showwarning("Warning", "Please select equipment to assign.")
            return

        care_level_name = self.care_level_var.get()
        if not care_level_name:
            messagebox.showwarning("Warning", "Please select a care level.")
            return

        care_level_id = [id for id, name in self.care_levels if name == care_level_name][0]

        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO care_level_equipment (care_level_id, equipment_id) VALUES (?, ?)", (care_level_id, selected_equipment))
            conn.commit()
            item = self.equipment_tree.item(selected_equipment)
            name, _ = item['values']
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "ASSIGN_EQUIPMENT", f"Assigned equipment '{name}' to care level '{care_level_name}'")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Info", "Equipment already assigned to this care level.")
        finally:
            conn.close()
        self.load_assigned_equipment()

    def unassign_equipment(self):
        selected_assigned = self.assigned_equipment_tree.focus()
        if not selected_assigned:
            messagebox.showwarning("Warning", "Please select assigned equipment to unassign.")
            return

        equipment_name = self.assigned_equipment_tree.item(selected_assigned)['values'][0]
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM equipment WHERE name = ?", (equipment_name,))
        equipment_id = cursor.fetchone()[0]
        
        care_level_name = self.care_level_var.get()
        care_level_id = [id for id, name in self.care_levels if name == care_level_name][0]

        cursor.execute("DELETE FROM care_level_equipment WHERE care_level_id = ? AND equipment_id = ?", (care_level_id, equipment_id))
        conn.commit()
        conn.close()
        self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "UNASSIGN_EQUIPMENT", f"Unassigned equipment '{equipment_name}' from care level '{care_level_name}'")
        self.load_assigned_equipment()
