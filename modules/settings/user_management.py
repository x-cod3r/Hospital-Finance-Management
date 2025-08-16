import tkinter as tk
from tkinter import ttk, messagebox
from modules.auth import AuthModule
from modules.utils import show_error_message

class UserManagementHandler:
    def __init__(self, settings_module, auth_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent
        self.auth_module = auth_module

    def setup_user_tab(self, parent):
        """Setup user management tab"""
        list_frame = ttk.LabelFrame(parent, text="Users", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        self.users_listbox = tk.Listbox(list_frame)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Refresh", command=self.load_users).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT)
        
        add_frame = ttk.LabelFrame(parent, text="Add New User", padding="10")
        add_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        ttk.Label(add_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.new_username_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_username_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.new_password_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_password_var, show="*").pack(fill=tk.X, pady=(0, 10))
        
        privileges_frame = ttk.LabelFrame(add_frame, text="Privileges", padding="10")
        privileges_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        canvas = tk.Canvas(privileges_frame)
        scrollbar = ttk.Scrollbar(privileges_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.privileges_vars = {}
        privileges = {
            "Doctors": ['view_doctors_tab', 'add_doctor', 'edit_doctor', 'delete_doctor'],
            "Nurses": ['view_nurses_tab', 'add_nurse', 'edit_nurse', 'delete_nurse'],
            "Patients": ['view_patients_tab', 'add_patient', 'edit_patient', 'delete_patient', 'add_patient_stay', 'add_patient_item', 'add_patient_equipment'],
            "Reports": ['view_reports_tab', 'generate_report', 'export_report'],
            "Settings": ['view_settings_tab', 'manage_users', 'manage_items', 'manage_care_levels', 'manage_equipment']
        }
        
        for group, privs in privileges.items():
            group_frame = ttk.LabelFrame(scrollable_frame, text=group)
            group_frame.pack(fill=tk.X, pady=5, padx=5)
            for p in privs:
                var = tk.BooleanVar()
                ttk.Checkbutton(group_frame, text=p.replace('_', ' ').title(), variable=var).pack(anchor=tk.W)
                self.privileges_vars[p] = var
            
        ttk.Button(add_frame, text="Create User", command=self.create_user).pack(pady=10)
        
        self.load_users()

    def load_users(self):
        """Load users into listbox"""
        self.users_listbox.delete(0, tk.END)
        users = self.auth_module.get_all_users()
        
        for user in users:
            username, created_at = user
            self.users_listbox.insert(tk.END, f"{username} (Created: {created_at})")

    def delete_user(self):
        """Delete selected user"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        user_text = self.users_listbox.get(selection[0])
        username = user_text.split(" ")[0]
        
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?")
        if not result:
            return
        
        if self.auth_module.delete_user(username, self.auth_module.current_user):
            messagebox.showinfo("Success", f"User '{username}' deleted successfully")
            self.load_users()
        else:
            show_error_message("Error", "Failed to delete user")

    def create_user(self):
        """Create a new user"""
        username = self.new_username_var.get().strip()
        password = self.new_password_var.get().strip()
        
        if not username or not password:
            show_error_message("Error", "Please enter both username and password")
            return
            
        privileges = [p for p, var in self.privileges_vars.items() if var.get()]
        
        if self.auth_module.create_user(username, password, self.auth_module.current_user, privileges):
            messagebox.showinfo("Success", f"User '{username}' created successfully")
            self.load_users()
            
            self.new_username_var.set("")
            self.new_password_var.set("")
            for var in self.privileges_vars.values():
                var.set(False)
        else:
            show_error_message("Error", "Failed to create user (username may already exist)")
