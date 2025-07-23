import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from utils import calculate_hours, format_currency

class NurseModule:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_nurses()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nurses list frame
        list_frame = ttk.LabelFrame(main_frame, text="Nurses", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        # Nurses listbox
        self.nurses_listbox = tk.Listbox(list_frame, height=15)
        self.nurses_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.nurses_listbox.bind('<<ListboxSelect>>', self.on_nurse_select)
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Add Nurse", command=self.add_nurse).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit Nurse", command=self.edit_nurse).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Nurse", command=self.delete_nurse).pack(side=tk.LEFT)
        
        # Nurse details frame
        details_frame = ttk.LabelFrame(main_frame, text="Nurse Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # Nurse info
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Level:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.level_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.level_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Hourly Rate:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.rate_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.rate_var, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Shift tracking
        shift_frame = ttk.LabelFrame(details_frame, text="Shift Tracking", padding="5")
        shift_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        shift_frame.columnconfigure(1, weight=1)
        
        ttk.Label(shift_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_var = tk.StringVar()
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(shift_frame, textvariable=self.date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(shift_frame, text="Arrival Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.arrival_var = tk.StringVar()
        ttk.Entry(shift_frame, textvariable=self.arrival_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(shift_frame, text="Leave Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.leave_var = tk.StringVar()
        ttk.Entry(shift_frame, textvariable=self.leave_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Button(shift_frame, text="Add Shift", command=self.add_shift).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Interventions
        interventions_frame = ttk.LabelFrame(details_frame, text="Interventions", padding="5")
        interventions_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        interventions_frame.columnconfigure(1, weight=1)
        
        ttk.Label(interventions_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.intervention_date_var = tk.StringVar()
        self.intervention_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(interventions_frame, textvariable=self.intervention_date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(interventions_frame, text="Intervention:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.intervention_var = tk.StringVar()
        self.intervention_combo = ttk.Combobox(interventions_frame, textvariable=self.intervention_var, state="readonly")
        self.intervention_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.load_interventions()
        
        ttk.Button(interventions_frame, text="Add Intervention", command=self.add_intervention).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Salary calculation
        salary_frame = ttk.LabelFrame(details_frame, text="Salary Calculation", padding="5")
        salary_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(salary_frame, text="Month:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.month_var = tk.StringVar()
        self.month_var.set(datetime.now().strftime("%m"))
        ttk.Entry(salary_frame, textvariable=self.month_var, width=5).grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(salary_frame, text="Year:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.year_var = tk.StringVar()
        self.year_var.set(datetime.now().strftime("%Y"))
        ttk.Entry(salary_frame, textvariable=self.year_var, width=8).grid(row=0, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Button(salary_frame, text="Calculate Salary", command=self.calculate_salary).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(salary_frame, text="Export Salary Sheet", command=self.export_salary_sheet).grid(row=1, column=2, columnspan=2, pady=5)
        
        # Configure grid weights
        details_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def load_nurses(self):
        """Load nurses into listbox"""
        self.nurses_listbox.delete(0, tk.END)
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, level FROM nurses ORDER BY name")
        nurses = cursor.fetchall()
        conn.close()
        
        for nurse in nurses:
            self.nurses_listbox.insert(tk.END, f"{nurse[0]}: {nurse[1]} ({nurse[2]})")
    
    def load_interventions(self):
        """Load interventions into combobox"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        
        self.intervention_combo['values'] = [i[0] for i in interventions]
    
    def on_nurse_select(self, event):
        """Handle nurse selection"""
        selection = self.nurses_listbox.curselection()
        if selection:
            index = selection[0]
            nurse_text = self.nurses_listbox.get(index)
            nurse_id = int(nurse_text.split(":")[0])
            
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, level, hourly_rate FROM nurses WHERE id = ?", (nurse_id,))
            nurse = cursor.fetchone()
            conn.close()
            
            if nurse:
                self.name_var.set(nurse[0])
                self.level_var.set(nurse[1])
                self.rate_var.set(format_currency(nurse[2]))
                self.current_nurse_id = nurse_id
    
    def add_nurse(self):
        """Add a new nurse"""
        # Create a new window for adding nurse
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Nurse")
        add_window.geometry("300x200")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        # Center the window
        add_window.geometry("+%d+%d" % (add_window.winfo_screenwidth()/2 - 150,
                                        add_window.winfo_screenheight()/2 - 100))
        
        ttk.Label(add_window, text="Nurse Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(add_window, text="Level:").pack()
        level_var = tk.StringVar()
        level_combo = ttk.Combobox(add_window, textvariable=level_var, state="readonly", width=28)
        level_combo['values'] = ["ICU", "Medium_ICU"]
        level_combo.pack(pady=5)
        level_combo.set("ICU")
        
        ttk.Label(add_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(add_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, "80.0")
        
        def save_nurse():
            name = name_entry.get().strip()
            level = level_var.get()
            try:
                rate = float(rate_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a nurse name")
                return
            
            if not level:
                messagebox.showerror("Error", "Please select a level")
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
        
        # Bind Enter key to save
        rate_entry.bind("<Return>", lambda event: save_nurse())
    
    def edit_nurse(self):
        """Edit selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse to edit")
            return
        
        # Get current nurse info
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, level, hourly_rate FROM nurses WHERE id = ?", (self.current_nurse_id,))
        nurse = cursor.fetchone()
        conn.close()
        
        if not nurse:
            return
        
        # Create a new window for editing nurse
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Nurse")
        edit_window.geometry("300x200")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (edit_window.winfo_screenwidth()/2 - 150,
                                         edit_window.winfo_screenheight()/2 - 100))
        
        ttk.Label(edit_window, text="Nurse Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, nurse[0])
        name_entry.focus()
        
        ttk.Label(edit_window, text="Level:").pack()
        level_var = tk.StringVar()
        level_combo = ttk.Combobox(edit_window, textvariable=level_var, state="readonly", width=28)
        level_combo['values'] = ["ICU", "Medium_ICU"]
        level_combo.pack(pady=5)
        level_combo.set(nurse[1])
        
        ttk.Label(edit_window, text="Hourly Rate:").pack()
        rate_entry = ttk.Entry(edit_window, width=30)
        rate_entry.pack(pady=5)
        rate_entry.insert(0, str(nurse[2]))
        
        def save_nurse():
            name = name_entry.get().strip()
            level = level_var.get()
            try:
                rate = float(rate_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a nurse name")
                return
            
            if not level:
                messagebox.showerror("Error", "Please select a level")
                return
            
            conn = sqlite3.connect("db/nurses.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE nurses SET name = ?, level = ?, hourly_rate = ? WHERE id = ?", 
                              (name, level, rate, self.current_nurse_id))
                conn.commit()
                messagebox.showinfo("Success", "Nurse updated successfully")
                edit_window.destroy()
                self.load_nurses()
                self.name_var.set(name)
                self.level_var.set(level)
                self.rate_var.set(format_currency(rate))
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update nurse: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_nurse).pack(pady=10)
        
        # Bind Enter key to save
        rate_entry.bind("<Return>", lambda event: save_nurse())
    
    def delete_nurse(self):
        """Delete selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this nurse?")
        if not result:
            return
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            # Delete related records first
            cursor.execute("DELETE FROM nurse_shifts WHERE nurse_id = ?", (self.current_nurse_id,))
            cursor.execute("DELETE FROM nurse_interventions WHERE nurse_id = ?", (self.current_nurse_id,))
            cursor.execute("DELETE FROM nurse_payments WHERE nurse_id = ?", (self.current_nurse_id,))
            
            # Delete the nurse
            cursor.execute("DELETE FROM nurses WHERE id = ?", (self.current_nurse_id,))
            conn.commit()
            
            messagebox.showinfo("Success", "Nurse deleted successfully")
            self.load_nurses()
            
            # Clear details
            self.name_var.set("")
            self.level_var.set("")
            self.rate_var.set("")
            delattr(self, 'current_nurse_id')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete nurse: {e}")
        finally:
            conn.close()
    
    def add_shift(self):
        """Add shift for selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse first")
            return
        
        date = self.date_var.get().strip()
        arrival = self.arrival_var.get().strip()
        leave = self.leave_var.get().strip()
        
        if not date or not arrival or not leave:
            messagebox.showerror("Error", "Please fill in all shift details")
            return
        
        # Calculate hours
        hours = calculate_hours(arrival, leave)
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO nurse_shifts (nurse_id, date, arrival_time, leave_time, hours_worked)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_nurse_id, date, arrival, leave, hours))
            conn.commit()
            messagebox.showinfo("Success", f"Shift added successfully ({hours} hours)")
            
            # Clear fields
            self.arrival_var.set("")
            self.leave_var.set("")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add shift: {e}")
        finally:
            conn.close()
    
    def add_intervention(self):
        """Add intervention for selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse first")
            return
        
        date = self.intervention_date_var.get().strip()
        intervention_name = self.intervention_var.get().strip()
        
        if not date or not intervention_name:
            messagebox.showerror("Error", "Please select date and intervention")
            return
        
        # Get intervention ID
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM interventions WHERE name = ?", (intervention_name,))
        intervention = cursor.fetchone()
        conn.close()
        
        if not intervention:
            messagebox.showerror("Error", "Invalid intervention selected")
            return
        
        intervention_id = intervention[0]
        
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO nurse_interventions (nurse_id, date, intervention_id)
                VALUES (?, ?, ?)
            """, (self.current_nurse_id, date, intervention_id))
            conn.commit()
            messagebox.showinfo("Success", "Intervention added successfully")
            
            # Clear field
            self.intervention_var.set("")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add intervention: {e}")
        finally:
            conn.close()
    
    def calculate_salary(self):
        """Calculate salary for selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse first")
            return
        
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid month and year")
            return
        
        # Get nurse info
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, level, hourly_rate FROM nurses WHERE id = ?", (self.current_nurse_id,))
        nurse = cursor.fetchone()
        
        if not nurse:
            conn.close()
            return
        
        nurse_name, level, hourly_rate = nurse
        
        # Calculate total hours
        cursor.execute("""
            SELECT SUM(hours_worked) FROM nurse_shifts 
            WHERE nurse_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        """, (self.current_nurse_id, f"{month:02d}", str(year)))
        
        total_hours_result = cursor.fetchone()[0]
        total_hours = total_hours_result if total_hours_result else 0.0
        
        # Calculate total bonus from interventions
        cursor.execute("""
            SELECT SUM(i.bonus_amount) 
            FROM nurse_interventions ni
            JOIN interventions i ON ni.intervention_id = i.id
            WHERE ni.nurse_id = ? AND strftime('%m', ni.date) = ? AND strftime('%Y', ni.date) = ?
        """, (self.current_nurse_id, f"{month:02d}", str(year)))
        
        total_bonus_result = cursor.fetchone()[0]
        total_bonus = total_bonus_result if total_bonus_result else 0.0
        
        # Calculate total salary
        base_salary = total_hours * hourly_rate
        total_salary = base_salary + total_bonus
        
        conn.close()
        
        # Show results
        result_text = f"""
Nurse: {nurse_name} ({level})
Period: {month:02d}/{year}

Total Hours: {total_hours:.2f}
Hourly Rate: {format_currency(hourly_rate)}
Base Salary: {format_currency(base_salary)}

Bonus from Interventions: {format_currency(total_bonus)}
Total Salary: {format_currency(total_salary)}
        """
        
        messagebox.showinfo("Salary Calculation", result_text)
    
    def export_salary_sheet(self):
        """Export salary sheet for selected nurse"""
        if not hasattr(self, 'current_nurse_id'):
            messagebox.showwarning("Warning", "Please select a nurse first")
            return
        
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid month and year")
            return
        
        # In a real implementation, this would generate an Excel/CSV file
        messagebox.showinfo("Export", "Salary sheet exported successfully!\n(In a real implementation, this would create an Excel file)")