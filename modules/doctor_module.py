import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from .utils import calculate_hours, format_currency

class DoctorModule:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_doctors()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Doctors list frame
        list_frame = ttk.LabelFrame(main_frame, text="Doctors", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        # Doctors listbox
        self.doctors_listbox = tk.Listbox(list_frame, height=15)
        self.doctors_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.doctors_listbox.bind('<<ListboxSelect>>', self.on_doctor_select)
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Add Doctor", command=self.add_doctor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit Doctor", command=self.edit_doctor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Doctor", command=self.delete_doctor).pack(side=tk.LEFT)
        
        # Doctor details frame
        details_frame = ttk.LabelFrame(main_frame, text="Doctor Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # Doctor info
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Hourly Rate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rate_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.rate_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Shift tracking
        shift_frame = ttk.LabelFrame(details_frame, text="Shift Tracking", padding="5")
        shift_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        shift_frame.columnconfigure(1, weight=1)

        ttk.Label(shift_frame, text="Arrival Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.arrival_date_var = tk.StringVar()
        self.arrival_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(shift_frame, textvariable=self.arrival_date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(shift_frame, text="Arrival Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.arrival_time_var = tk.StringVar()
        ttk.Entry(shift_frame, textvariable=self.arrival_time_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(shift_frame, text="AM/PM:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(5, 0))
        self.arrival_ampm_var = tk.StringVar()
        self.arrival_ampm_var.set("AM")
        ttk.Combobox(shift_frame, textvariable=self.arrival_ampm_var, values=["AM", "PM"], width=5).grid(row=1, column=3, sticky=tk.W, pady=2)

        ttk.Label(shift_frame, text="Leave Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.leave_date_var = tk.StringVar()
        self.leave_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(shift_frame, textvariable=self.leave_date_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(shift_frame, text="Leave Time (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.leave_time_var = tk.StringVar()
        ttk.Entry(shift_frame, textvariable=self.leave_time_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        ttk.Label(shift_frame, text="AM/PM:").grid(row=3, column=2, sticky=tk.W, pady=2, padx=(5, 0))
        self.leave_ampm_var = tk.StringVar()
        self.leave_ampm_var.set("AM")
        ttk.Combobox(shift_frame, textvariable=self.leave_ampm_var, values=["AM", "PM"], width=5).grid(row=3, column=3, sticky=tk.W, pady=2)
        
        ttk.Button(shift_frame, text="Add Shift", command=self.add_shift).grid(row=4, column=0, columnspan=4, pady=5)
        
        # Interventions
        interventions_frame = ttk.LabelFrame(details_frame, text="Interventions", padding="5")
        interventions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
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
        salary_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
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
    
    def load_doctors(self):
        """Load doctors into listbox"""
        self.doctors_listbox.delete(0, tk.END)
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM doctors ORDER BY name")
        doctors = cursor.fetchall()
        conn.close()
        
        for doctor in doctors:
            self.doctors_listbox.insert(tk.END, f"{doctor[0]}: {doctor[1]}")
    
    def load_interventions(self):
        """Load interventions into combobox"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        
        self.intervention_combo['values'] = [i[0] for i in interventions]
    
    def on_doctor_select(self, event):
        """Handle doctor selection"""
        selection = self.doctors_listbox.curselection()
        if selection:
            index = selection[0]
            doctor_text = self.doctors_listbox.get(index)
            doctor_id = int(doctor_text.split(":")[0])
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (doctor_id,))
            doctor = cursor.fetchone()
            conn.close()
            
            if doctor:
                self.name_var.set(doctor[0])
                self.rate_var.set(format_currency(doctor[1]))
                self.current_doctor_id = doctor_id
    
    def add_doctor(self):
        """Add a new doctor"""
        # Create a new window for adding doctor
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Doctor")
        add_window.geometry("300x150")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        # Center the window
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
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a doctor name")
                return
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO doctors (name, hourly_rate) VALUES (?, ?)", (name, rate))
                conn.commit()
                messagebox.showinfo("Success", "Doctor added successfully")
                add_window.destroy()
                self.load_doctors()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add doctor: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_doctor).pack(pady=10)
        
        # Bind Enter key to save
        rate_entry.bind("<Return>", lambda event: save_doctor())
    
    def edit_doctor(self):
        """Edit selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor to edit")
            return
        
        # Get current doctor info
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (self.current_doctor_id,))
        doctor = cursor.fetchone()
        conn.close()
        
        if not doctor:
            return
        
        # Create a new window for editing doctor
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Doctor")
        edit_window.geometry("300x150")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Center the window
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
                messagebox.showerror("Error", "Please enter a valid hourly rate")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a doctor name")
                return
            
            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE doctors SET name = ?, hourly_rate = ? WHERE id = ?", 
                              (name, rate, self.current_doctor_id))
                conn.commit()
                messagebox.showinfo("Success", "Doctor updated successfully")
                edit_window.destroy()
                self.load_doctors()
                self.name_var.set(name)
                self.rate_var.set(format_currency(rate))
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update doctor: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_doctor).pack(pady=10)
        
        # Bind Enter key to save
        rate_entry.bind("<Return>", lambda event: save_doctor())
    
    def delete_doctor(self):
        """Delete selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this doctor?")
        if not result:
            return
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            # Delete related records first
            cursor.execute("DELETE FROM doctor_shifts WHERE doctor_id = ?", (self.current_doctor_id,))
            cursor.execute("DELETE FROM doctor_interventions WHERE doctor_id = ?", (self.current_doctor_id,))
            cursor.execute("DELETE FROM doctor_payments WHERE doctor_id = ?", (self.current_doctor_id,))
            
            # Delete the doctor
            cursor.execute("DELETE FROM doctors WHERE id = ?", (self.current_doctor_id,))
            conn.commit()
            
            messagebox.showinfo("Success", "Doctor deleted successfully")
            self.load_doctors()
            
            # Clear details
            self.name_var.set("")
            self.rate_var.set("")
            delattr(self, 'current_doctor_id')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete doctor: {e}")
        finally:
            conn.close()
    
    def add_shift(self):
        """Add shift for selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor first")
            return

        try:
            arrival_date_str = self.arrival_date_var.get().strip()
            arrival_time_str = self.arrival_time_var.get().strip()
            arrival_ampm = self.arrival_ampm_var.get()

            leave_date_str = self.leave_date_var.get().strip()
            leave_time_str = self.leave_time_var.get().strip()
            leave_ampm = self.leave_ampm_var.get()

            if not all([arrival_date_str, arrival_time_str, leave_date_str, leave_time_str]):
                messagebox.showerror("Error", "Please fill in all shift details")
                return

            arrival_datetime_str = f"{arrival_date_str} {arrival_time_str} {arrival_ampm}"
            leave_datetime_str = f"{leave_date_str} {leave_time_str} {leave_ampm}"

            arrival_datetime = datetime.strptime(arrival_datetime_str, "%Y-%m-%d %I:%M %p")
            leave_datetime = datetime.strptime(leave_datetime_str, "%Y-%m-%d %I:%M %p")

            hours = calculate_hours(arrival_datetime, leave_datetime)

            conn = sqlite3.connect("db/doctors.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctor_shifts (doctor_id, arrival_datetime, leave_datetime)
                VALUES (?, ?, ?)
            """, (self.current_doctor_id, arrival_datetime, leave_datetime))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Shift added successfully ({hours} hours)")

            # Clear fields
            self.arrival_time_var.set("")
            self.leave_time_var.set("")

        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add shift: {e}")
    
    def add_intervention(self):
        """Add intervention for selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor first")
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
        
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO doctor_interventions (doctor_id, date, intervention_id)
                VALUES (?, ?, ?)
            """, (self.current_doctor_id, date, intervention_id))
            conn.commit()
            messagebox.showinfo("Success", "Intervention added successfully")
            
            # Clear field
            self.intervention_var.set("")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add intervention: {e}")
        finally:
            conn.close()
    
    def calculate_salary(self):
        """Calculate salary for selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor first")
            return
        
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid month and year")
            return
        
        # Get doctor info
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (self.current_doctor_id,))
        doctor = cursor.fetchone()
        
        if not doctor:
            conn.close()
            return
        
        doctor_name, hourly_rate = doctor
        
        # Calculate total hours
        cursor.execute("""
            SELECT arrival_datetime, leave_datetime FROM doctor_shifts
            WHERE doctor_id = ? AND
                  strftime('%m', arrival_datetime) = ? AND
                  strftime('%Y', arrival_datetime) = ?
        """, (self.current_doctor_id, f"{month:02d}", str(year)))
        
        shifts = cursor.fetchall()
        total_hours = 0.0
        for shift in shifts:
            arrival_datetime = datetime.strptime(shift[0], "%Y-%m-%d %H:%M:%S")
            leave_datetime = datetime.strptime(shift[1], "%Y-%m-%d %H:%M:%S")
            total_hours += calculate_hours(arrival_datetime, leave_datetime)
        
        # Calculate total bonus from interventions
        cursor.execute("""
            SELECT SUM(i.bonus_amount) 
            FROM doctor_interventions di
            JOIN interventions i ON di.intervention_id = i.id
            WHERE di.doctor_id = ? AND strftime('%m', di.date) = ? AND strftime('%Y', di.date) = ?
        """, (self.current_doctor_id, f"{month:02d}", str(year)))
        
        total_bonus_result = cursor.fetchone()[0]
        total_bonus = total_bonus_result if total_bonus_result else 0.0
        
        # Calculate total salary
        base_salary = total_hours * hourly_rate
        total_salary = base_salary + total_bonus
        
        conn.close()
        
        # Show results
        result_text = f"""
Doctor: {doctor_name}
Period: {month:02d}/{year}

Total Hours: {total_hours:.2f}
Hourly Rate: {format_currency(hourly_rate)}
Base Salary: {format_currency(base_salary)}

Bonus from Interventions: {format_currency(total_bonus)}
Total Salary: {format_currency(total_salary)}
        """
        
        messagebox.showinfo("Salary Calculation", result_text)
    

    def export_salary_sheet(self):

        
        """Export salary sheet for selected doctor"""
        if not hasattr(self, 'current_doctor_id'):
            messagebox.showwarning("Warning", "Please select a doctor first")
            return
        
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid month and year")
            return
        
        # Get doctor info
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (self.current_doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            conn.close()
            return
        doctor_name, hourly_rate = doctor

        # Calculate total hours
        cursor.execute("""
        SELECT arrival_datetime, leave_datetime FROM doctor_shifts 
        WHERE doctor_id = ? AND strftime('%m', arrival_datetime) = ? AND strftime('%Y', arrival_datetime) = ?
        """, (self.current_doctor_id, f"{month:02d}", str(year)))
        
        shifts = cursor.fetchall()
        total_hours = sum(calculate_hours(datetime.strptime(shift[0], "%Y-%m-%d %H:%M:%S"), 
                                          datetime.strptime(shift[1], "%Y-%m-%d %H:%M:%S")) for shift in shifts)

        # Calculate bonus from interventions
        cursor.execute("""
        SELECT i.bonus_amount FROM doctor_interventions di
        JOIN interventions i ON di.intervention_id = i.id
        WHERE di.doctor_id = ? AND strftime('%m', di.date) = ? AND strftime('%Y', di.date) = ?
        """, (self.current_doctor_id, f"{month:02d}", str(year)))
        
        interventions = cursor.fetchall()
        total_bonus = sum(intervention[0] for intervention in interventions)

        base_salary = total_hours * hourly_rate
        total_salary = base_salary + total_bonus
        conn.close()

        # Export to CSV
        import csv
        from datetime import datetime as dt
        filename = f"doctor_{self.current_doctor_id}_salary_{year}_{month:02d}.csv"
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Doctor Salary Sheet"])
                writer.writerow([])
                writer.writerow(["Doctor Name:", doctor_name])
                writer.writerow(["Period:", f"{month:02d}/{year}"])
                writer.writerow([])
                writer.writerow(["Total Hours:", f"{total_hours:.2f}"])
                writer.writerow(["Hourly Rate:", format_currency(hourly_rate)])
                writer.writerow(["Base Salary:", format_currency(base_salary)])
                writer.writerow(["Bonus from Interventions:", format_currency(total_bonus)])
                writer.writerow(["Total Salary:", format_currency(total_salary)])
            
            messagebox.showinfo("Export Success", f"Salary sheet exported to {filename}")
        except Exception as e:
             messagebox.showerror("Export Error", f"Failed to export salary sheet: {e}")