import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message
from ..utils import format_currency

class DoctorCRUD:
    def __init__(self, doctor_module, auth_module):
        self.doctor_module = doctor_module
        self.parent = doctor_module.parent
        self.auth_module = auth_module

    def get_selected_doctors(self):
        """Get a list of selected doctor IDs"""
        return [doc_id for doc_id, var in self.doctor_module.doctor_vars.items() if var.get()]

    def load_doctors(self):
        """Load doctors into a list of checkboxes"""
        for widget in self.doctor_module.scrollable_frame.winfo_children():
            widget.destroy()
        self.doctor_module.doctor_vars = {}
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM doctors ORDER BY name")
        doctors = cursor.fetchall()
        conn.close()
        
        for doctor in doctors:
            doctor_id, doctor_name = doctor
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.doctor_module.scrollable_frame, text=doctor_name, variable=var,
                                 command=lambda doc_id=doctor_id: self.on_doctor_select(doc_id))
            cb.pack(fill='x', padx=5, pady=2)
            self.doctor_module.doctor_vars[doctor_id] = var

    def on_doctor_select(self, doctor_id):
        """Handle doctor selection from checkbox"""
        if self.doctor_module.doctor_vars[doctor_id].get():
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (doctor_id,))
            doctor = cursor.fetchone()
            conn.close()
            
            if doctor:
                self.doctor_module.name_var.set(doctor[0])
                self.doctor_module.rate_var.set(format_currency(doctor[1]))
                self.doctor_module.current_doctor_id = doctor_id
        else:
            if hasattr(self.doctor_module, 'current_doctor_id') and self.doctor_module.current_doctor_id == doctor_id:
                self.doctor_module.name_var.set("")
                self.doctor_module.rate_var.set("")
                delattr(self.doctor_module, 'current_doctor_id')

    def add_doctor(self):
        """Add a new doctor"""
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Doctor")
        add_window.geometry("300x150")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        add_window.geometry("+%d+%d" % (add_window.winfo_screenwidth()/2 - 150,
                                        add_window.winfo_screenheight()/2 - 75))
        
        ttk.Label(add_window, text="Doctor Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(add_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(add_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, "100.0")
        
        def save_doctor():
            name = name_entry.get().strip()
            try:
                rate = float(rate_entry.get())
            except ValueError:
                show_error_message("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                show_error_message("Error", "Please enter a doctor name")
                return
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO doctors (name, hourly_rate) VALUES (?, ?)", (name, rate))
                conn.commit()
                self.auth_module.log_action(self.auth_module.current_user, "CREATE_DOCTOR", f"Created doctor: {name}")
                messagebox.showinfo("Success", "Doctor added successfully")
                add_window.destroy()
                self.load_doctors()
            except sqlite3.Error as e:
                show_error_message("Error", f"Failed to add doctor: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_doctor).pack(pady=10)
        rate_entry.bind("<Return>", lambda event: save_doctor())

    def edit_doctor(self):
        """Edit selected doctor"""
        selected_doctors = self.get_selected_doctors()
        if len(selected_doctors) != 1:
            messagebox.showwarning("Warning", "Please select exactly one doctor to edit")
            return
        self.doctor_module.current_doctor_id = selected_doctors[0]
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (self.doctor_module.current_doctor_id,))
        doctor = cursor.fetchone()
        conn.close()
        
        if not doctor:
            return
        
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Doctor")
        edit_window.geometry("300x150")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        edit_window.geometry("+%d+%d" % (edit_window.winfo_screenwidth()/2 - 150,
                                         edit_window.winfo_screenheight()/2 - 75))
        
        ttk.Label(edit_window, text="Doctor Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, doctor[0])
        name_entry.focus()
        
        ttk.Label(edit_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(edit_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, str(doctor[1]))
        
        def save_doctor():
            name = name_entry.get().strip()
            try:
                rate = float(rate_entry.get())
            except ValueError:
                show_error_message("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                show_error_message("Error", "Please enter a doctor name")
                return
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE doctors SET name = ?, hourly_rate = ? WHERE id = ?", 
                              (name, rate, self.doctor_module.current_doctor_id))
                conn.commit()
                self.auth_module.log_action(self.auth_module.current_user, "UPDATE_DOCTOR", f"Updated doctor: {name}")
                messagebox.showinfo("Success", "Doctor updated successfully")
                edit_window.destroy()
                self.load_doctors()
                self.doctor_module.name_var.set(name)
                self.doctor_module.rate_var.set(format_currency(rate))
            except sqlite3.Error as e:
                show_error_message("Error", f"Failed to update doctor: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_doctor).pack(pady=10)
        rate_entry.bind("<Return>", lambda event: save_doctor())

    def delete_doctor(self):
        """Delete selected doctor(s)"""
        selected_doctors = self.get_selected_doctors()
        if not selected_doctors:
            messagebox.showwarning("Warning", "Please select at least one doctor to delete")
            return
        
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_doctors)} doctor(s)?")
        if not result:
            return
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            for doctor_id in selected_doctors:
                cursor.execute("SELECT name FROM doctors WHERE id = ?", (doctor_id,))
                doctor_name = cursor.fetchone()[0]
                cursor.execute("DELETE FROM doctor_shifts WHERE doctor_id = ?", (doctor_id,))
                cursor.execute("DELETE FROM doctor_interventions WHERE doctor_id = ?", (doctor_id,))
                cursor.execute("DELETE FROM doctor_payments WHERE doctor_id = ?", (doctor_id,))
                cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
                self.auth_module.log_action(self.auth_module.current_user, "DELETE_DOCTOR", f"Deleted doctor: {doctor_name}")
            conn.commit()
            
            messagebox.showinfo("Success", f"{len(selected_doctors)} doctor(s) deleted successfully")
            self.load_doctors()
            
            self.doctor_module.name_var.set("")
            self.doctor_module.rate_var.set("")
            if hasattr(self.doctor_module, 'current_doctor_id'):
                delattr(self.doctor_module, 'current_doctor_id')
            self.load_doctors()
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to delete doctor: {e}")
        finally:
            conn.close()
