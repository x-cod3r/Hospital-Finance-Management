import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from modules.auth import AuthModule

class SettingsModule:
    def __init__(self, parent):
        self.parent = parent
        self.auth_module = AuthModule()
        self.doctor_module = None
        self.nurse_module = None
        self.patient_module = None
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
        
        # Audit log tab
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="Audit Log")
        self.setup_log_tab(log_tab)

        # Item management tab
        item_tab = ttk.Frame(notebook)
        notebook.add(item_tab, text="Item Management")
        self.setup_item_tab(item_tab)

        # Care Level Management tab
        care_level_tab = ttk.Frame(notebook)
        notebook.add(care_level_tab, text="Care Level Management")
        self.setup_care_level_tab(care_level_tab)
    
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
        
        # Save button
        ttk.Button(parent, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Configure grid weights
        db_frame.columnconfigure(1, weight=1)
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
            print("Error: Failed to delete user")
    
    def create_user(self):
        """Create a new user"""
        username = self.new_username_var.get().strip()
        password = self.new_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            print("Error: Please enter both username and password")
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
            print("Error: Failed to create user (username may already exist)")
    
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

    def setup_item_tab(self, parent):
        """Setup item management tab"""
        # Main frame
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for item types
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Interventions tab
        interventions_tab = ttk.Frame(notebook)
        notebook.add(interventions_tab, text="Interventions")
        self.setup_interventions_manager(interventions_tab)

        # Other items tab
        items_tab = ttk.Frame(notebook)
        notebook.add(items_tab, text="Labs, Drugs, etc.")
        self.setup_items_manager(items_tab)

    def setup_interventions_manager(self, parent):
        """Setup interventions management UI"""
        # Interventions list
        list_frame = ttk.LabelFrame(parent, text="Interventions", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.interventions_tree = ttk.Treeview(list_frame, columns=("Name", "Bonus"), show="headings")
        self.interventions_tree.heading("Name", text="Name")
        self.interventions_tree.heading("Bonus", text="Bonus")
        self.interventions_tree.pack(fill=tk.BOTH, expand=True)
        self.load_interventions()

        # Buttons
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_intervention).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_intervention).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_intervention).pack(side=tk.LEFT)

    def setup_items_manager(self, parent):
        """Setup items management UI"""
        # Items list
        list_frame = ttk.LabelFrame(parent, text="Billable Items", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.items_tree = ttk.Treeview(list_frame, columns=("Category", "Name", "Price"), show="headings")
        self.items_tree.heading("Category", text="Category")
        self.items_tree.heading("Name", text="Name")
        self.items_tree.heading("Price", text="Price")
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        self.load_items()

        # Buttons
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_item).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT)

    def load_interventions(self):
        """Load interventions into the treeview"""
        for i in self.interventions_tree.get_children():
            self.interventions_tree.delete(i)
        
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions ORDER BY name")
        for row in cursor.fetchall():
            self.interventions_tree.insert("", "end", values=(row[1], f"{row[2]:.2f}"), iid=row[0])
        conn.close()

    def add_intervention(self):
        """Show dialog to add a new intervention"""
        self.intervention_dialog("Add Intervention")

    def edit_intervention(self):
        """Show dialog to edit the selected intervention"""
        selected_item = self.interventions_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an intervention to edit.")
            return
        
        item = self.interventions_tree.item(selected_item)
        name, bonus = item['values']
        self.intervention_dialog("Edit Intervention", item_id=selected_item, name=name, bonus=bonus)

    def delete_intervention(self):
        """Delete the selected intervention"""
        selected_item = self.interventions_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an intervention to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this intervention?"):
            conn = sqlite3.connect("db/interventions.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interventions WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.load_interventions()

    def intervention_dialog(self, title, item_id=None, name="", bonus=""):
        """Dialog for adding/editing interventions"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Bonus Amount:").pack(pady=(10, 0))
        bonus_var = tk.StringVar(value=bonus)
        ttk.Entry(dialog, textvariable=bonus_var).pack(fill=tk.X, padx=10)

        def save():
            new_name = name_var.get().strip()
            new_bonus = bonus_var.get().strip()

            if not new_name or not new_bonus:
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                new_bonus = float(new_bonus)
            except ValueError:
                messagebox.showerror("Error", "Bonus must be a number.")
                return

            conn = sqlite3.connect("db/interventions.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE interventions SET name = ?, bonus_amount = ? WHERE id = ?", (new_name, new_bonus, item_id))
            else:
                cursor.execute("INSERT INTO interventions (name, bonus_amount) VALUES (?, ?)", (new_name, new_bonus))
            conn.commit()
            conn.close()
            self.load_interventions()
            self._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def load_items(self):
        """Load items into the treeview"""
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, name, price FROM items ORDER BY category, name")
        for row in cursor.fetchall():
            self.items_tree.insert("", "end", values=(row[1], row[2], f"{row[3]:.2f}"), iid=row[0])
        conn.close()

    def add_item(self):
        """Show dialog to add a new item"""
        self.item_dialog("Add Item")

    def edit_item(self):
        """Show dialog to edit the selected item"""
        selected_item = self.items_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        item = self.items_tree.item(selected_item)
        category, name, price = item['values']
        self.item_dialog("Edit Item", item_id=selected_item, category=category, name=name, price=price)

    def delete_item(self):
        """Delete the selected item"""
        selected_item = self.items_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.load_items()
            self._refresh_other_modules()

    def item_dialog(self, title, item_id=None, category="", name="", price=""):
        """Dialog for adding/editing items"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Category:").pack(pady=(10, 0))
        category_var = tk.StringVar(value=category)
        category_combo = ttk.Combobox(dialog, textvariable=category_var, values=["labs", "drugs", "radiology", "consultations"])
        category_combo.pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Price:").pack(pady=(10, 0))
        price_var = tk.StringVar(value=price)
        ttk.Entry(dialog, textvariable=price_var).pack(fill=tk.X, padx=10)

        def save():
            new_category = category_var.get().strip()
            new_name = name_var.get().strip()
            new_price = price_var.get().strip()

            if not all([new_category, new_name, new_price]):
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                new_price = float(new_price)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number.")
                return

            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE items SET category = ?, name = ?, price = ? WHERE id = ?", (new_category, new_name, new_price, item_id))
            else:
                cursor.execute("INSERT INTO items (category, name, price) VALUES (?, ?, ?)", (new_category, new_name, new_price))
            conn.commit()
            conn.close()
            self.load_items()
            self._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def _refresh_other_modules(self):
        """Refresh item lists in other modules."""
        if self.doctor_module:
            self.doctor_module.load_interventions()
        if self.nurse_module:
            self.nurse_module.load_interventions()
        if self.patient_module:
            # This is a bit of a hack, but it's the easiest way to refresh all the item lists
            self.patient_module.setup_labs_tab(self.patient_module.labs_tab_frame)
            self.patient_module.setup_drugs_tab(self.patient_module.drugs_tab_frame)
            self.patient_module.setup_radiology_tab(self.patient_module.radiology_tab_frame)
            self.patient_module.setup_consultations_tab(self.patient_module.consultations_tab_frame)
            self.patient_module.setup_stays_tab(self.patient_module.stays_tab_frame)

    def setup_care_level_tab(self, parent):
        """Setup care level management UI"""
        list_frame = ttk.LabelFrame(parent, text="Care Levels", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.care_levels_tree = ttk.Treeview(list_frame, columns=("Name", "Daily Rate"), show="headings")
        self.care_levels_tree.heading("Name", text="Name")
        self.care_levels_tree.heading("Daily Rate", text="Daily Rate")
        self.care_levels_tree.pack(fill=tk.BOTH, expand=True)
        self.load_care_levels()

        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_care_level).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_care_level).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_care_level).pack(side=tk.LEFT)

    def load_care_levels(self):
        """Load care levels into the treeview"""
        for i in self.care_levels_tree.get_children():
            self.care_levels_tree.delete(i)
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        for row in cursor.fetchall():
            self.care_levels_tree.insert("", "end", values=(row[1], f"{row[2]:.2f}"), iid=row[0])
        conn.close()

    def add_care_level(self):
        """Show dialog to add a new care level"""
        self.care_level_dialog("Add Care Level")

    def edit_care_level(self):
        """Show dialog to edit the selected care level"""
        selected_item = self.care_levels_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a care level to edit.")
            return
        
        item = self.care_levels_tree.item(selected_item)
        name, rate = item['values']
        self.care_level_dialog("Edit Care Level", item_id=selected_item, name=name, rate=rate)

    def delete_care_level(self):
        """Delete the selected care level"""
        selected_item = self.care_levels_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a care level to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this care level?"):
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM care_levels WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.load_care_levels()
            self._refresh_other_modules()

    def care_level_dialog(self, title, item_id=None, name="", rate=""):
        """Dialog for adding/editing care levels"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(dialog, text="Daily Rate:").pack(pady=(10, 0))
        rate_var = tk.StringVar(value=rate)
        ttk.Entry(dialog, textvariable=rate_var).pack(fill=tk.X, padx=10)

        def save():
            new_name = name_var.get().strip()
            new_rate = rate_var.get().strip()

            if not new_name or not new_rate:
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                new_rate = float(new_rate)
            except ValueError:
                messagebox.showerror("Error", "Rate must be a number.")
                return

            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE care_levels SET name = ?, daily_rate = ? WHERE id = ?", (new_name, new_rate, item_id))
            else:
                cursor.execute("INSERT INTO care_levels (name, daily_rate) VALUES (?, ?)", (new_name, new_rate))
            conn.commit()
            conn.close()
            self.load_care_levels()
            self._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
