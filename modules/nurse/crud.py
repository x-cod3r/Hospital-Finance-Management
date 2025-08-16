import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message
from ..utils import format_currency

class NurseCRUD:
    def __init__(self, nurse_module, auth_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent
        self.auth_module = auth_module

    def get_selected_nurses(self):
        """Get a list of selected nurse IDs"""
        return [nurse_id for nurse_id, var in self.nurse_module.nurse_vars.items() if var.get()]

    def load_nurses(self):
        """Load nurses from the database"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level, hourly_rate FROM nurses ORDER BY name")
        nurses = cursor.fetchall()
        conn.close()
        return nurses

    def on_nurse_select(self, nurse_id):
        """Handle nurse selection from checkbox"""
        if self.nurse_module.nurse_vars[nurse_id].get():
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, level, hourly_rate FROM nurses WHERE id = ?", (nurse_id,))
            nurse = cursor.fetchone()
            conn.close()
            
            if nurse:
                self.nurse_module.name_var.set(nurse[0])
                self.nurse_module.rate_var.set(format_currency(nurse[2]))
                self.nurse_module.current_nurse_id = nurse_id
        else:
            if hasattr(self.nurse_module, 'current_nurse_id') and self.nurse_module.current_nurse_id == nurse_id:
                self.nurse_module.name_var.set("")
                self.nurse_module.rate_var.set("")
                delattr(self.nurse_module, 'current_nurse_id')

    def add_nurse(self, name, level, rate):
        """Add a new nurse"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO nurses (name, level, hourly_rate) VALUES (?, ?, ?)", (name, level, rate))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "CREATE_NURSE", f"Created nurse: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding nurse: {e}")
            return False
        finally:
            conn.close()

    def get_nurse(self, nurse_id):
        """Get a single nurse by ID"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level, hourly_rate FROM nurses WHERE id = ?", (nurse_id,))
        nurse = cursor.fetchone()
        conn.close()
        return nurse

    def edit_nurse(self, nurse_id, name, level, rate):
        """Edit a nurse"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE nurses SET name = ?, level = ?, hourly_rate = ? WHERE id = ?", 
                          (name, level, rate, nurse_id))
            conn.commit()
            self.auth_module.log_action(self.auth_module.current_user, "UPDATE_NURSE", f"Updated nurse: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating nurse: {e}")
            return False
        finally:
            conn.close()

    def delete_nurse(self, nurse_id):
        """Delete a nurse"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM nurses WHERE id = ?", (nurse_id,))
            nurse = cursor.fetchone()
            if nurse:
                nurse_name = nurse[0]
                cursor.execute("DELETE FROM nurse_shifts WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurse_interventions WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurse_payments WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurses WHERE id = ?", (nurse_id,))
                conn.commit()
                self.auth_module.log_action(self.auth_module.current_user, "DELETE_NURSE", f"Deleted nurse: {nurse_name}")
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"Error deleting nurse: {e}")
            return False
        finally:
            conn.close()
