import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import sqlite3

from .doctor.crud import DoctorCRUD
from .doctor.shifts import ShiftsHandler
from .doctor.interventions import InterventionsHandler
from .doctor.salary import SalaryHandler

class DoctorModule:
    def __init__(self, parent, auth_module):
        self.parent = parent
        self.auth_module = auth_module
        self.crud_handler = DoctorCRUD(self, auth_module)
        self.shifts_handler = ShiftsHandler(self)
        self.interventions_handler = InterventionsHandler(self)
        self.salary_handler = SalaryHandler(self)
        
        self.setup_ui()
        self.crud_handler.load_doctors()
        self.load_patients()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        list_frame = ttk.LabelFrame(main_frame, text="Doctors", padding="10")
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.doctor_vars = {}
        
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        current_user = self.auth_module.current_user
        
        if self.auth_module.has_privilege(current_user, 'add_doctor'):
            ttk.Button(buttons_frame, text="Add Doctor", command=self.crud_handler.add_doctor).pack(fill=tk.X, pady=(0, 5))
        if self.auth_module.has_privilege(current_user, 'edit_doctor'):
            ttk.Button(buttons_frame, text="Edit Doctor", command=self.crud_handler.edit_doctor).pack(fill=tk.X, pady=(0, 5))
        if self.auth_module.has_privilege(current_user, 'delete_doctor'):
            ttk.Button(buttons_frame, text="Delete Doctor", command=self.crud_handler.delete_doctor).pack(fill=tk.X)
        
        details_frame = ttk.LabelFrame(main_frame, text="Doctor Details", padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.rate_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.rate_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(details_frame, text="Hourly Rate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        shift_frame = ttk.LabelFrame(details_frame, text="Shift Tracking", padding="5")
        shift_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        shift_frame.columnconfigure(1, weight=1)

        self.arrival_date_var = tk.StringVar()
        self.arrival_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(shift_frame, textvariable=self.arrival_date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(shift_frame, text="Arrival Date:").grid(row=0, column=0, sticky=tk.W, pady=2)

        self.arrival_time_var = tk.StringVar()
        self.arrival_time_var.set("09:00")
        ttk.Entry(shift_frame, textvariable=self.arrival_time_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(shift_frame, text="Arrival Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=2)

        self.arrival_ampm_var = tk.StringVar()
        self.arrival_ampm_var.set("AM")
        ttk.Combobox(shift_frame, textvariable=self.arrival_ampm_var, values=["AM", "PM"], width=5).grid(row=1, column=3, sticky=tk.W, pady=2)
        ttk.Label(shift_frame, text="AM/PM:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(5, 0))

        self.leave_date_var = tk.StringVar()
        self.leave_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(shift_frame, textvariable=self.leave_date_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(shift_frame, text="Leave Date:").grid(row=2, column=0, sticky=tk.W, pady=2)

        self.leave_time_var = tk.StringVar()
        self.leave_time_var.set("09:00")
        ttk.Entry(shift_frame, textvariable=self.leave_time_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(shift_frame, text="Leave Time (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=2)

        self.leave_ampm_var = tk.StringVar()
        self.leave_ampm_var.set("AM")
        ttk.Combobox(shift_frame, textvariable=self.leave_ampm_var, values=["AM", "PM"], width=5).grid(row=3, column=3, sticky=tk.W, pady=2)
        ttk.Label(shift_frame, text="AM/PM:").grid(row=3, column=2, sticky=tk.W, pady=2, padx=(5, 0))
        
        self.shift_patient_var = tk.StringVar()
        self.shift_patient_combo = ttk.Combobox(shift_frame, textvariable=self.shift_patient_var, state="readonly")
        self.shift_patient_combo.grid(row=4, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(shift_frame, text="Patient:").grid(row=4, column=0, sticky=tk.W, pady=2)

        ttk.Button(shift_frame, text="Add Shift", command=self.shifts_handler.add_shift).grid(row=5, column=0, columnspan=4, pady=5)
        
        interventions_frame = ttk.LabelFrame(details_frame, text="Interventions", padding="5")
        interventions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        interventions_frame.columnconfigure(1, weight=1)
        
        self.intervention_date_var = tk.StringVar()
        self.intervention_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(interventions_frame, textvariable=self.intervention_date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(interventions_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.intervention_var = tk.StringVar()
        self.intervention_combo = ttk.Combobox(interventions_frame, textvariable=self.intervention_var, state="readonly")
        self.intervention_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.interventions_handler.load_interventions()
        ttk.Label(interventions_frame, text="Intervention:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.intervention_patient_var = tk.StringVar()
        self.intervention_patient_combo = ttk.Combobox(interventions_frame, textvariable=self.intervention_patient_var, state="readonly")
        self.intervention_patient_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(interventions_frame, text="Patient:").grid(row=2, column=0, sticky=tk.W, pady=2)

        ttk.Button(interventions_frame, text="Add Intervention", command=self.interventions_handler.add_intervention).grid(row=3, column=0, columnspan=2, pady=5)
        
        salary_frame = ttk.LabelFrame(details_frame, text="Salary Calculation", padding="5")
        salary_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.start_date_entry = DateEntry(salary_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        ttk.Label(salary_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.end_date_entry = DateEntry(salary_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.end_date_entry.grid(row=0, column=3, sticky=tk.W, pady=2, padx=(5, 0))
        ttk.Label(salary_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        self.start_date_entry.set_date(thirty_days_ago)
        self.end_date_entry.set_date(today)

        ttk.Button(salary_frame, text="Calculate Salary", command=self.salary_handler.calculate_salary).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(salary_frame, text="Export as Excel", command=lambda: self.salary_handler.export_salary_sheet('xlsx')).grid(row=1, column=2, pady=5)
        
        details_frame.columnconfigure(1, weight=1)

    def load_patients(self):
        """Load patients into comboboxes"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        
        self.patients = patients
        patient_names = [f"{p[0]}: {p[1]}" for p in patients]
        self.shift_patient_combo['values'] = patient_names
        self.intervention_patient_combo['values'] = patient_names
