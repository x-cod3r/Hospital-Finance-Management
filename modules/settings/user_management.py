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
        
        if self.auth_module.create_user(username, password, self.auth_module.current_user):
            messagebox.showinfo("Success", f"User '{username}' created successfully")
            self.load_users()
            
            self.new_username_var.set("")
            self.new_password_var.set("")
        else:
            show_error_message("Error", "Failed to create user (username may already exist)")
