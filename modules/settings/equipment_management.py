import tkinter as tk
from tkinter import ttk
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
        """Load equipment into the treeview"""
        for i in self.equipment_tree.get_children():
            self.equipment_tree.delete(i)
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rental_price FROM equipment ORDER BY name")
        for row in cursor.fetchall():
            self.equipment_tree.insert("", "end", values=(row[1], f"{row[2]:.2f}"), iid=row[0])
        conn.close()

    def add_equipment(self):
        self.equipment_dialog("Add Equipment")

    def edit_equipment(self):
        selected_item = self.equipment_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select equipment to edit.")
            return
        
        item = self.equipment_tree.item(selected_item)
        name, price = item['values']
        self.equipment_dialog("Edit Equipment", item_id=selected_item, name=name, price=price)

    def delete_equipment(self):
        selected_item = self.equipment_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select equipment to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this equipment?"):
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipment WHERE id = ?", (selected_item,))
            cursor.execute("DELETE FROM care_level_equipment WHERE equipment_id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.load_equipment()
            self.load_assigned_equipment()

    def equipment_dialog(self, title, item_id=None, name="", price=""):
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Daily Rental Price:").pack(pady=(10, 0))
        price_var = tk.StringVar(value=price)
        ttk.Entry(dialog, textvariable=price_var).pack(fill=tk.X, padx=10)

        def save():
            new_name = name_var.get().strip()
            new_price = price_var.get().strip()

            if not new_name or not new_price:
                show_error_message("Error", "All fields are required.")
                return

            try:
                new_price = float(new_price)
            except ValueError:
                show_error_message("Error", "Price must be a number.")
                return

            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE equipment SET name = ?, daily_rental_price = ? WHERE id = ?", (new_name, new_price, item_id))
            else:
                cursor.execute("INSERT INTO equipment (name, daily_rental_price) VALUES (?, ?)", (new_name, new_price))
            conn.commit()
            conn.close()
            self.load_equipment()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

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
        self.load_assigned_equipment()
