import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import format_currency

class NurseCRUD:
    def __init__(self, nurse_module):
        self.nurse_module = nurse_module
        self.parent = nurse_module.parent

    def get_selected_nurses(self):
        """Get a list of selected nurse IDs"""
        return [nurse_id for nurse_id, var in self.nurse_module.nurse_vars.items() if var.get()]

    def load_nurses(self):
        """Load nurses into a list of checkboxes"""
        for widget in self.nurse_module.scrollable_frame.winfo_children():
            widget.destroy()
        self.nurse_module.nurse_vars = {}
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level FROM nurses ORDER BY name")
        nurses = cursor.fetchall()
        conn.close()
        
        for nurse in nurses:
            nurse_id, nurse_name, nurse_level = nurse
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.nurse_module.scrollable_frame, text=f"{nurse_id}: {nurse_name} ({nurse_level})", variable=var,
                                 command=lambda nurse_id=nurse_id: self.on_nurse_select(nurse_id))
            cb.pack(fill='x', padx=5, pady=2)
            self.nurse_module.nurse_vars[nurse_id] = var

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
                self.nurse_module.level_var.set(nurse[1])
                self.nurse_module.rate_var.set(format_currency(nurse[2]))
                self.nurse_module.current_nurse_id = nurse_id
        else:
            if hasattr(self.nurse_module, 'current_nurse_id') and self.nurse_module.current_nurse_id == nurse_id:
                self.nurse_module.name_var.set("")
                self.nurse_module.level_var.set("")
                self.nurse_module.rate_var.set("")
                delattr(self.nurse_module, 'current_nurse_id')

    def add_nurse(self):
        """Add a new nurse"""
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Nurse")
        add_window.geometry("300x150")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        add_window.geometry("+%d+%d" % (add_window.winfo_screenwidth()/2 - 150,
                                        add_window.winfo_screenheight()/2 - 75))
        
        ttk.Label(add_window, text="Nurse Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(add_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(add_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, "80.0")
        
        def save_nurse():
            name = name_entry.get().strip()
            level = "ICU"  # Default level
            try:
                rate = float(rate_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a nurse name")
                return
            
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO nurses (name, level, hourly_rate) VALUES (?, ?, ?)", (name, level, rate))
                conn.commit()
                messagebox.showinfo("Success", "Nurse added successfully")
                add_window.destroy()
                self.load_nurses()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add nurse: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_nurse).pack(pady=10)
        rate_entry.bind("<Return>", lambda event: save_nurse())

    def edit_nurse(self):
        """Edit selected nurse"""
        selected_nurses = self.get_selected_nurses()
        if len(selected_nurses) != 1:
            messagebox.showwarning("Warning", "Please select exactly one nurse to edit")
            return
        self.nurse_module.current_nurse_id = selected_nurses[0]
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, level, hourly_rate FROM nurses WHERE id = ?", (self.nurse_module.current_nurse_id,))
        nurse = cursor.fetchone()
        conn.close()
        
        if not nurse:
            return
        
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Nurse")
        edit_window.geometry("300x150")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        edit_window.geometry("+%d+%d" % (edit_window.winfo_screenwidth()/2 - 150,
                                         edit_window.winfo_screenheight()/2 - 75))
        
        ttk.Label(edit_window, text="Nurse Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, nurse[0])
        name_entry.focus()
        
        ttk.Label(edit_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(edit_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, str(nurse[2]))
        
        def save_nurse():
            name = name_entry.get().strip()
            level = nurse[1] # Keep the existing level
            try:
                rate = float(rate_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a nurse name")
                return
            
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE nurses SET name = ?, level = ?, hourly_rate = ? WHERE id = ?", 
                              (name, level, rate, self.nurse_module.current_nurse_id))
                conn.commit()
                messagebox.showinfo("Success", "Nurse updated successfully")
                edit_window.destroy()
                self.load_nurses()
                self.nurse_module.name_var.set(name)
                self.nurse_module.level_var.set(level)
                self.nurse_module.rate_var.set(format_currency(rate))
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update nurse: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_nurse).pack(pady=10)
        rate_entry.bind("<Return>", lambda event: save_nurse())

    def delete_nurse(self):
        """Delete selected nurse(s)"""
        selected_nurses = self.get_selected_nurses()
        if not selected_nurses:
            messagebox.showwarning("Warning", "Please select at least one nurse to delete")
            return
        
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_nurses)} nurse(s)?")
        if not result:
            return
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            for nurse_id in selected_nurses:
                cursor.execute("DELETE FROM nurse_shifts WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurse_interventions WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurse_payments WHERE nurse_id = ?", (nurse_id,))
                cursor.execute("DELETE FROM nurses WHERE id = ?", (nurse_id,))
            conn.commit()
            
            messagebox.showinfo("Success", f"{len(selected_nurses)} nurse(s) deleted successfully")
            self.load_nurses()
            
            self.nurse_module.name_var.set("")
            self.nurse_module.level_var.set("")
            self.nurse_module.rate_var.set("")
            if hasattr(self.nurse_module, 'current_nurse_id'):
                delattr(self.nurse_module, 'current_nurse_id')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete nurse: {e}")
        finally:
            conn.close()
