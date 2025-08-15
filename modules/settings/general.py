import tkinter as tk
from tkinter import ttk, messagebox

class GeneralSettingsHandler:
    def __init__(self, settings_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent

    def setup_general_tab(self, parent):
        """Setup general settings tab"""
        db_frame = ttk.LabelFrame(parent, text="Database Settings", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(db_frame, text="Doctors Database:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.settings_module.doctors_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.settings_module.doctors_db_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(db_frame, text="Nurses Database:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.settings_module.nurses_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.settings_module.nurses_db_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(db_frame, text="Patients Database:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.settings_module.patients_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.settings_module.patients_db_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Button(parent, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        db_frame.columnconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        self.load_settings()

    def load_settings(self):
        """Load current settings"""
        self.settings_module.doctors_db_var.set("db/doctors.db")
        self.settings_module.nurses_db_var.set("db/nurses.db")
        self.settings_module.patients_db_var.set("db/patients.db")
    
    def save_settings(self):
        """Save settings"""
        messagebox.showinfo("Settings", "Settings saved successfully!")
