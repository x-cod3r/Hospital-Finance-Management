import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from modules.auth import AuthModule
from modules.doctor_module import DoctorModule
from modules.nurse_module import NurseModule
from modules.patient_module import PatientModule
from modules.company_module import CompanyModule
from modules.settings_module import SettingsModule
from modules.utils import setup_database

class ICUManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICU Management System")
        self.root.geometry("1200x800")
        
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
        login_frame.columnconfigure(1, weight=1)
        login_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(login_frame, text="ICU Management System", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
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
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def show_main_interface(self):
        """Show the main application interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        doctor_tab = ttk.Frame(notebook)
        nurse_tab = ttk.Frame(notebook)
        patient_tab = ttk.Frame(notebook)
        company_tab = ttk.Frame(notebook)
        settings_tab = ttk.Frame(notebook)
        
        notebook.add(doctor_tab, text="Doctors")
        notebook.add(nurse_tab, text="Nurses")
        notebook.add(patient_tab, text="Patients")
        notebook.add(company_tab, text="Company")
        notebook.add(settings_tab, text="Settings")
        
        # Initialize modules in their respective tabs
        DoctorModule(doctor_tab)
        NurseModule(nurse_tab)
        PatientModule(patient_tab)
        CompanyModule(company_tab)
        SettingsModule(settings_tab)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "ICU Management System v1.0\n\nDeveloped for healthcare management")

if __name__ == "__main__":
    root = tk.Tk()
    app = ICUManagementApp(root)
    root.mainloop()