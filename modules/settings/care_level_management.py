import tkinter as tk
from tkinter import ttk, messagebox
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
        """Load care levels from the database"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        care_levels = cursor.fetchall()
        conn.close()
        return care_levels

    def add_care_level(self, name, rate):
        """Add a new care level"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO care_levels (name, daily_rate) VALUES (?, ?)", (name, rate))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "CREATE_CARE_LEVEL", f"Created care level: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding care level: {e}")
            return False
        finally:
            conn.close()

    def get_care_level(self, care_level_id):
        """Get a single care level by ID"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels WHERE id = ?", (care_level_id,))
        care_level = cursor.fetchone()
        conn.close()
        return care_level

    def edit_care_level(self, care_level_id, name, rate):
        """Edit a care level"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE care_levels SET name = ?, daily_rate = ? WHERE id = ?", (name, rate, care_level_id))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "UPDATE_CARE_LEVEL", f"Updated care level: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating care level: {e}")
            return False
        finally:
            conn.close()

    def delete_care_level(self, care_level_id):
        """Delete a care level"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM care_levels WHERE id = ?", (care_level_id,))
            name = cursor.fetchone()[0]
            cursor.execute("DELETE FROM care_levels WHERE id = ?", (care_level_id,))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "DELETE_CARE_LEVEL", f"Deleted care level: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting care level: {e}")
            return False
        finally:
            conn.close()
