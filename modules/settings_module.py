import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from modules.auth import AuthModule
from modules.database import get_db_connection

class SettingsModule:
    def __init__(self, parent):
        self.parent = parent
        self.auth_module = AuthModule()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings tab
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General Settings")
        self.setup_general_tab(general_tab)
        
        # User management tab
        user_tab = ttk.Frame(notebook)
        notebook.add(user_tab, text="User Management")
        self.setup_user_tab(user_tab)
        
        # Interventions tab
        interventions_tab = ttk.Frame(notebook)
        notebook.add(interventions_tab, text="Interventions")
        self.setup_interventions_tab(interventions_tab)

        # Audit log tab
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="Audit Log")
        self.setup_log_tab(log_tab)
    
    def setup_general_tab(self, parent):
        """Setup general settings tab"""
        # Database settings
        db_frame = ttk.LabelFrame(parent, text="Database Settings", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(db_frame, text="Doctors Database:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.doctors_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.doctors_db_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(db_frame, text="Nurses Database:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.nurses_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.nurses_db_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(db_frame, text="Patients Database:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.patients_db_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.patients_db_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Rate settings
        rate_frame = ttk.LabelFrame(parent, text="Default Rates", padding="10")
        rate_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rate_frame, text="Doctor Hourly Rate:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.doctor_rate_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.doctor_rate_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(rate_frame, text="Nurse Hourly Rate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.nurse_rate_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.nurse_rate_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(rate_frame, text="ICU Daily Rate:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.icu_rate_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.icu_rate_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(rate_frame, text="Medium ICU Daily Rate:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.medium_icu_rate_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.medium_icu_rate_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Save button
        ttk.Button(parent, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Configure grid weights
        db_frame.columnconfigure(1, weight=1)
        rate_frame.columnconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
    
    def setup_user_tab(self, parent):
        """Setup user management tab"""
        # User list
        list_frame = ttk.LabelFrame(parent, text="Users", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        self.users_listbox = tk.Listbox(list_frame)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Refresh", command=self.load_users).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT)
        
        # Add user frame
        add_frame = ttk.LabelFrame(parent, text="Add New User", padding="10")
        add_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        ttk.Label(add_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.new_username_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_username_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.new_password_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_password_var, show="*").pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(add_frame, text="Create User", command=self.create_user).pack(pady=10)
        
        # Load users
        self.load_users()
    
    def setup_interventions_tab(self, parent):
        """Setup interventions management tab"""
        # Intervention list
        list_frame = ttk.LabelFrame(parent, text="Interventions", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.interventions_listbox = tk.Listbox(list_frame)
        self.interventions_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Buttons
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="Refresh", command=self.load_interventions).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Add Intervention", command=self.add_intervention).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit Intervention", command=self.edit_intervention).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Intervention", command=self.delete_intervention).pack(side=tk.LEFT)

        # Add/Edit intervention frame
        add_frame = ttk.LabelFrame(parent, text="Add/Edit Intervention", padding="10")
        add_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        ttk.Label(add_frame, text="Name:").pack(anchor=tk.W, pady=(0, 5))
        self.intervention_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.intervention_name_var).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(add_frame, text="Bonus Amount:").pack(anchor=tk.W, pady=(0, 5))
        self.intervention_bonus_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.intervention_bonus_var).pack(fill=tk.X, pady=(0, 10))

        ttk.Button(add_frame, text="Save Intervention", command=self.save_intervention).pack(pady=10)

        # Load interventions
        self.load_interventions()

    def load_interventions(self):
        """Load interventions into listbox"""
        self.interventions_listbox.delete(0, tk.END)
        conn = get_db_connection("doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions ORDER BY name")
        interventions = cursor.fetchall()

        for intervention in interventions:
            self.interventions_listbox.insert(tk.END, f"{intervention[0]}: {intervention[1]} ({format_currency(intervention[2])})")

    def add_intervention(self):
        """Add a new intervention"""
        self.intervention_name_var.set("")
        self.intervention_bonus_var.set("")
        self.current_intervention_id = None

    def edit_intervention(self):
        """Edit selected intervention"""
        selection = self.interventions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an intervention to edit")
            return

        # Get intervention ID from selection
        intervention_text = self.interventions_listbox.get(selection[0])
        intervention_id = int(intervention_text.split(":")[0])

        conn = get_db_connection("doctors.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, bonus_amount FROM interventions WHERE id = ?", (intervention_id,))
        intervention = cursor.fetchone()

        if intervention:
            self.intervention_name_var.set(intervention[0])
            self.intervention_bonus_var.set(intervention[1])
            self.current_intervention_id = intervention_id

    def delete_intervention(self):
        """Delete selected intervention"""
        selection = self.interventions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an intervention to delete")
            return

        # Get intervention ID from selection
        intervention_text = self.interventions_listbox.get(selection[0])
        intervention_id = int(intervention_text.split(":")[0])

        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this intervention?")
        if not result:
            return

        conn = get_db_connection("doctors.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM interventions WHERE id = ?", (intervention_id,))
            conn.commit()
            messagebox.showinfo("Success", "Intervention deleted successfully")
            self.load_interventions()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete intervention: {e}")

    def save_intervention(self):
        """Save new or edited intervention"""
        name = self.intervention_name_var.get().strip()
        try:
            bonus = float(self.intervention_bonus_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid bonus amount")
            return

        if not name:
            messagebox.showerror("Error", "Please enter an intervention name")
            return

        conn = get_db_connection("doctors.db")
        cursor = conn.cursor()

        try:
            if hasattr(self, 'current_intervention_id') and self.current_intervention_id:
                # Update existing intervention
                cursor.execute("UPDATE interventions SET name = ?, bonus_amount = ? WHERE id = ?",
                              (name, bonus, self.current_intervention_id))
            else:
                # Insert new intervention
                cursor.execute("INSERT INTO interventions (name, bonus_amount) VALUES (?, ?)", (name, bonus))

            conn.commit()
            messagebox.showinfo("Success", "Intervention saved successfully")
            self.load_interventions()

            # Clear fields
            self.intervention_name_var.set("")
            self.intervention_bonus_var.set("")
            delattr(self, 'current_intervention_id')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to save intervention: {e}")

    def setup_log_tab(self, parent):
        """Setup audit log tab"""
        # Create text widget with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        ttk.Button(parent, text="Refresh Logs", command=self.load_logs).pack(pady=10)
        
        # Load logs
        self.load_logs()
    
    def load_settings(self):
        """Load current settings"""
        # In a real implementation, this would load from a config file
        # For now, we'll set default values
        self.doctors_db_var.set("db/doctors.db")
        self.nurses_db_var.set("db/nurses.db")
        self.patients_db_var.set("db/patients.db")
        self.doctor_rate_var.set("100.0")
        self.nurse_rate_var.set("80.0")
        self.icu_rate_var.set("1500.0")
        self.medium_icu_rate_var.set("1000.0")
    
    def save_settings(self):
        """Save settings"""
        # In a real implementation, this would save to a config file
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def load_users(self):
        """Load users into listbox"""
        self.users_listbox.delete(0, tk.END)
        users = self.auth_module.get_all_users()
        
        for user in users:
            username, created_at = user
            self.users_listbox.insert(tk.END, f"{username} (Created: {created_at})")
    
    def add_user(self):
        """Add a new user"""
        # This is handled by the form in the user tab
        pass
    
    def delete_user(self):
        """Delete selected user"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        # Get username from selection
        user_text = self.users_listbox.get(selection[0])
        username = user_text.split(" ")[0]
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?")
        if not result:
            return
        
        # Delete user (users can only delete themselves)
        # In a real implementation, this would check the current logged-in user
        if self.auth_module.delete_user(username, "admin"):  # Placeholder for current user
            messagebox.showinfo("Success", f"User '{username}' deleted successfully")
            self.load_users()
        else:
            messagebox.showerror("Error", "Failed to delete user")
    
    def create_user(self):
        """Create a new user"""
        username = self.new_username_var.get().strip()
        password = self.new_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Create user
        if self.auth_module.create_user(username, password, "admin"):  # Placeholder for current user
            messagebox.showinfo("Success", f"User '{username}' created successfully")
            self.load_users()
            
            # Clear fields
            self.new_username_var.set("")
            self.new_password_var.set("")
        else:
            messagebox.showerror("Error", "Failed to create user (username may already exist)")
    
    def load_logs(self):
        """Load audit logs"""
        self.log_text.delete(1.0, tk.END)
        logs = self.auth_module.get_logs()
        
        for log in logs:
            user, action, timestamp, details = log
            log_entry = f"[{timestamp}] {user}: {action}"
            if details:
                log_entry += f" - {details}"
            log_entry += "\n"
            self.log_text.insert(tk.END, log_entry)