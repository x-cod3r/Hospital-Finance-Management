import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from ..utils import show_error_message

class PatientCRUD:
    def __init__(self, patient_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent

    def get_selected_patients(self):
        """Get a list of selected patient IDs"""
        return [patient_id for patient_id, var in self.patient_module.patient_vars.items() if var.get()]

    def load_patients(self):
        """Load patients into a list of checkboxes"""
        for widget in self.patient_module.scrollable_frame.winfo_children():
            widget.destroy()
        self.patient_module.patient_vars = {}
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        
        for patient in patients:
            patient_id, patient_name = patient
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.patient_module.scrollable_frame, text=patient_name, variable=var,
                                 command=self.on_patient_select)
            cb.pack(fill='x', padx=5, pady=2)
            self.patient_module.patient_vars[patient_id] = var

    def on_patient_select(self):
        """Handle patient selection from checkbox"""
        selected_patients = self.get_selected_patients()
        
        if len(selected_patients) == 1:
            patient_id = selected_patients[0]
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            if patient:
                self.patient_module.name_var.set(patient[0])
                self.patient_module.admission_date_var.set(patient[1])
                self.patient_module.discharge_date_var.set(patient[2] or "")
                self.patient_module.current_patient_id = patient_id
                
                # Load items for all categories
                self.patient_module.stays_handler.load_stays()
                self.patient_module.items_handler.load_category_items("labs")
                self.patient_module.items_handler.load_category_items("drugs")
                self.patient_module.items_handler.load_category_items("radiology")
                self.patient_module.items_handler.load_category_items("consultations")
                self.patient_module.equipment_handler.load_patient_equipment()
        else:
            # Clear details if none or multiple are selected
            self.patient_module.name_var.set("")
            self.patient_module.admission_date_var.set("")
            self.patient_module.discharge_date_var.set("")
            if hasattr(self.patient_module, 'current_patient_id'):
                delattr(self.patient_module, 'current_patient_id')
            
            # Clear category lists
            self.patient_module.clear_all_tabs()

    def add_patient(self):
        """Add a new patient"""
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Patient")
        add_window.geometry("400x250")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        add_window.geometry("+%d+%d" % (add_window.winfo_screenwidth()/2 - 200,
                                        add_window.winfo_screenheight()/2 - 125))
        
        ttk.Label(add_window, text="Patient Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(add_window, text="Admission Date:").pack()
        admission_entry = DateEntry(add_window, width=38, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        admission_entry.pack(pady=5)
        
        def save_patient():
            name = name_entry.get().strip()
            admission_date = admission_entry.get_date().strftime('%Y-%m-%d')
            
            if not name:
                show_error_message("Error", "Please enter a patient name")
                return
            
            if not admission_date:
                show_error_message("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO patients (name, admission_date) VALUES (?, ?)", (name, admission_date))
                conn.commit()
                messagebox.showinfo("Success", "Patient added successfully")
                add_window.destroy()
                self.load_patients()
                self.patient_module._refresh_other_modules()
            except sqlite3.Error as e:
                show_error_message("Error", f"Failed to add patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_patient).pack(pady=10)
        admission_entry.bind("<Return>", lambda event: save_patient())

    def edit_patient(self):
        """Edit selected patient"""
        selected_patients = self.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to edit")
            return
        self.patient_module.current_patient_id = selected_patients[0]
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (self.patient_module.current_patient_id,))
        patient = cursor.fetchone()
        conn.close()
        
        if not patient:
            return
        
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Patient")
        edit_window.geometry("400x300")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        edit_window.geometry("+%d+%d" % (edit_window.winfo_screenwidth()/2 - 200,
                                         edit_window.winfo_screenheight()/2 - 150))
        
        ttk.Label(edit_window, text="Patient Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, patient[0])
        name_entry.focus()
        
        ttk.Label(edit_window, text="Admission Date:").pack()
        admission_entry = DateEntry(edit_window, width=38, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        admission_entry.pack(pady=5)
        admission_entry.set_date(patient[1])
        
        ttk.Label(edit_window, text="Discharge Date:").pack()
        discharge_entry = DateEntry(edit_window, width=38, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        discharge_entry.pack(pady=5)
        if patient[2]:
            discharge_entry.set_date(patient[2])
        else:
            discharge_entry.set_date(None)
        
        def save_patient():
            name = name_entry.get().strip()
            admission_date = admission_entry.get_date().strftime('%Y-%m-%d')
            discharge_date = discharge_entry.get_date().strftime('%Y-%m-%d') if discharge_entry.get() else None
            
            if not name:
                show_error_message("Error", "Please enter a patient name")
                return
            
            if not admission_date:
                show_error_message("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE patients SET name = ?, admission_date = ?, discharge_date = ? WHERE id = ?", 
                               (name, admission_date, discharge_date, self.patient_module.current_patient_id))
                conn.commit()
                messagebox.showinfo("Success", "Patient updated successfully")
                edit_window.destroy()
                self.load_patients()
                self.patient_module._refresh_other_modules()
                self.patient_module.name_var.set(name)
                self.patient_module.admission_date_var.set(admission_date)
                self.patient_module.discharge_date_var.set(discharge_date or "")
            except sqlite3.Error as e:
                show_error_message("Error", f"Failed to update patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_patient).pack(pady=10)
        discharge_entry.bind("<Return>", lambda event: save_patient())

    def delete_patient(self):
        """Delete selected patient(s)"""
        selected_patients = self.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient to delete")
            return
        
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_patients)} patient(s)?")
        if not result:
            return
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            for patient_id in selected_patients:
                cursor.execute("DELETE FROM patient_stays WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_labs WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_drugs WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_radiology WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_consultations WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
            
            messagebox.showinfo("Success", f"{len(selected_patients)} patient(s) deleted successfully")
            self.load_patients()
            self.patient_module._refresh_other_modules()
            self.on_patient_select()
            self.load_patients()
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to delete patient: {e}")
        finally:
            conn.close()
