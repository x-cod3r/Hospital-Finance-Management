import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import traceback
import os
import configparser
from modules.auth import AuthModule
from modules.doctor_module import DoctorModule
from modules.nurse_module import NurseModule
from modules.patient_module import PatientModule
from modules.company_module import CompanyModule
from modules.settings_module import SettingsModule
from modules.utils import setup_database, show_error_message

class ICUManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICU Management System")
        self.root.geometry("350x420")
        
        # Read configuration
        self.config = configparser.ConfigParser()
        self.config.read('Config/config.ini')
        self.debug_mode = self.config.getboolean('DEBUG', 'debugmode', fallback=False)

        # Setup databases
        setup_database()
        
        # Initialize modules
        self.auth_module = AuthModule()
        
        # Create main menu
        self.create_main_menu()
        
        # Show login screen
        self.show_login()
    
    def create_main_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def show_login(self):
        """Show the login screen"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Center the frame
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        login_frame.columnconfigure(0, weight=1) # Left padding column
        login_frame.columnconfigure(1, weight=0) # Label column
        login_frame.columnconfigure(2, weight=0) # Entry column
        login_frame.columnconfigure(3, weight=1) # Right padding column
        login_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(login_frame, text="ICU Management System", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=1, column=1, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=20)
        self.username_entry.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=2, column=1, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*", width=20)
        self.password_entry.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=4, pady=20)
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda event: self.login())
        
        # Focus on username field
        self.username_entry.focus()
    
    def login(self):
        """Handle login process"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if self.auth_module.authenticate(username, password):
            self.show_main_interface()
        else:
            show_error_message("Login Failed", "Invalid username or password")
            print("Login Failed: Invalid username or password")
    
    def show_main_interface(self):
        """Show the main application interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1200x600")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create and add tabs based on user privileges
        current_user = self.auth_module.current_user
        
        if self.auth_module.has_privilege(current_user, 'view_doctors_tab'):
            doctor_tab = ttk.Frame(notebook)
            notebook.add(doctor_tab, text="Doctors")
            doctor_module = DoctorModule(doctor_tab, self.auth_module)
        
        if self.auth_module.has_privilege(current_user, 'view_nurses_tab'):
            nurse_tab = ttk.Frame(notebook)
            notebook.add(nurse_tab, text="Nurses")
            nurse_module = NurseModule(nurse_tab, self.auth_module)
            
        if self.auth_module.has_privilege(current_user, 'view_patients_tab'):
            patient_tab = ttk.Frame(notebook)
            notebook.add(patient_tab, text="Patients")
            patient_module = PatientModule(patient_tab, self.auth_module)

        if self.auth_module.has_privilege(current_user, 'view_reports_tab'):
            company_tab = ttk.Frame(notebook)
            notebook.add(company_tab, text="Company")
            company_module = CompanyModule(company_tab)

        if self.auth_module.has_privilege(current_user, 'view_settings_tab'):
            settings_tab = ttk.Frame(notebook)
            notebook.add(settings_tab, text="Settings")
            settings_module = SettingsModule(settings_tab, self.auth_module)

        # Add sign-out tab
        sign_out_tab = ttk.Frame(notebook)
        notebook.add(sign_out_tab, text="Sign Out")
        
        login_time = self.auth_module.log_action(current_user, "GET_LOGIN_TIME", "User is viewing login time")
        ttk.Label(sign_out_tab, text=f"Logged in as: {current_user}").pack(pady=10)
        ttk.Label(sign_out_tab, text=f"Login time: {login_time}").pack(pady=10)
        ttk.Button(sign_out_tab, text="Sign Out", command=self.show_login).pack(pady=10)

        # Set up module connections
        if 'patient_module' in locals() and 'doctor_module' in locals():
            patient_module.doctor_module = doctor_module
        if 'patient_module' in locals() and 'nurse_module' in locals():
            patient_module.nurse_module = nurse_module
        if 'settings_module' in locals() and 'doctor_module' in locals():
            settings_module.doctor_module = doctor_module
        if 'settings_module' in locals() and 'nurse_module' in locals():
            settings_module.nurse_module = nurse_module
        if 'settings_module' in locals() and 'patient_module' in locals():
            settings_module.patient_module = patient_module
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "ICU Management System v1.0\n\nDeveloped for healthcare management")

def handle_exception(exc_type, exc_value, exc_traceback, debug_mode):
    """Handle uncaught exceptions"""
    if debug_mode:
        show_error_message("Error", "An unexpected error occurred. Please check the terminal for details.")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    else:
        show_error_message("Error", "An unexpected error occurred.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ICUManagementApp(root)
    root.report_callback_exception = lambda exc_type, exc_value, exc_traceback: handle_exception(exc_type, exc_value, exc_traceback, app.debug_mode)
    root.mainloop()
