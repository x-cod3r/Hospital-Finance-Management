import tkinter as tk
from tkinter import ttk
import sqlite3
from ..utils import show_error_message

class CareLevelManagementHandler:
    def __init__(self, settings_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent

    def setup_care_level_tab(self, parent):
        """Setup care level management UI"""
        list_frame = ttk.LabelFrame(parent, text="Care Levels", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.care_levels_tree = ttk.Treeview(list_frame, columns=("Name", "Daily Rate"), show="headings")
        self.care_levels_tree.heading("Name", text="Name")
        self.care_levels_tree.heading("Daily Rate", text="Daily Rate")
        self.care_levels_tree.pack(fill=tk.BOTH, expand=True)
        self.load_care_levels()

        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_care_level).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_care_level).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_care_level).pack(side=tk.LEFT)

    def load_care_levels(self):
        """Load care levels into the treeview"""
        for i in self.care_levels_tree.get_children():
            self.care_levels_tree.delete(i)
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        for row in cursor.fetchall():
            self.care_levels_tree.insert("", "end", values=(row[1], f"{row[2]:.2f}"), iid=row[0])
        conn.close()

    def add_care_level(self):
        """Show dialog to add a new care level"""
        self.care_level_dialog("Add Care Level")

    def edit_care_level(self):
        """Show dialog to edit the selected care level"""
        selected_item = self.care_levels_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a care level to edit.")
            return
        
        item = self.care_levels_tree.item(selected_item)
        name, rate = item['values']
        self.care_level_dialog("Edit Care Level", item_id=selected_item, name=name, rate=rate)

    def delete_care_level(self):
        """Delete the selected care level"""
        selected_item = self.care_levels_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a care level to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this care level?"):
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM care_levels WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.load_care_levels()
            self.settings_module._refresh_other_modules()

    def care_level_dialog(self, title, item_id=None, name="", rate=""):
        """Dialog for adding/editing care levels"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Daily Rate:").pack(pady=(10, 0))
        rate_var = tk.StringVar(value=rate)
        ttk.Entry(dialog, textvariable=rate_var).pack(fill=tk.X, padx=10)

        def save():
            new_name = name_var.get().strip()
            new_rate = rate_var.get().strip()

            if not new_name or not new_rate:
                show_error_message("Error", "All fields are required.")
                return

            try:
                new_rate = float(new_rate)
            except ValueError:
                show_error_message("Error", "Rate must be a number.")
                return

            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE care_levels SET name = ?, daily_rate = ? WHERE id = ?", (new_name, new_rate, item_id))
            else:
                cursor.execute("INSERT INTO care_levels (name, daily_rate) VALUES (?, ?)", (new_name, new_rate))
            conn.commit()
            conn.close()
            self.load_care_levels()
            self.settings_module._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
