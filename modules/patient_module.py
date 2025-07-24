import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from .utils import format_currency

class PatientModule:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_patients()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Patients list frame
        list_frame = ttk.LabelFrame(main_frame, text="Patients", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        # Patients listbox
        self.patients_listbox = tk.Listbox(list_frame, height=15)
        self.patients_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.patients_listbox.bind('<<ListboxSelect>>', self.on_patient_select)
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Add Patient", command=self.add_patient).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit Patient", command=self.edit_patient).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Patient", command=self.delete_patient).pack(side=tk.LEFT)
        
        # Patient details frame
        details_frame = ttk.LabelFrame(main_frame, text="Patient Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # Patient info
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="ICU Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.icu_type_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.icu_type_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Admission Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.admission_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.admission_date_var, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Discharge Date:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.discharge_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.discharge_date_var, state="readonly").grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Notebook for tabs
        notebook = ttk.Notebook(details_frame)
        notebook.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Package tab
        package_tab = ttk.Frame(notebook)
        notebook.add(package_tab, text="Package")
        self.setup_package_tab(package_tab)
        
        # Labs tab
        labs_tab = ttk.Frame(notebook)
        notebook.add(labs_tab, text="Labs")
        self.setup_labs_tab(labs_tab)
        
        # Drugs tab
        drugs_tab = ttk.Frame(notebook)
        notebook.add(drugs_tab, text="Drugs")
        self.setup_drugs_tab(drugs_tab)
        
        # Radiology tab
        radiology_tab = ttk.Frame(notebook)
        notebook.add(radiology_tab, text="Radiology")
        self.setup_radiology_tab(radiology_tab)
        
        # Consultations tab
        consultations_tab = ttk.Frame(notebook)
        notebook.add(consultations_tab, text="Consultations")
        self.setup_consultations_tab(consultations_tab)
        
        # Cost calculation
        cost_frame = ttk.LabelFrame(details_frame, text="Cost Calculation", padding="5")
        cost_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(cost_frame, text="Calculate Total Cost", command=self.calculate_cost).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cost_frame, text="Export Cost Sheet", command=self.export_cost_sheet).pack(side=tk.LEFT)
        
        # Configure grid weights
        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def setup_package_tab(self, parent):
        """Setup package tab"""
        # Package selection
        ttk.Label(parent, text="Package Type:").pack(anchor=tk.W, pady=(10, 5))
        self.package_type_var = tk.StringVar()
        package_type_frame = ttk.Frame(parent)
        package_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(package_type_frame, text="Default Package", variable=self.package_type_var, 
                       value="default", command=self.update_package_ui).pack(side=tk.LEFT)
        ttk.Radiobutton(package_type_frame, text="Custom Package", variable=self.package_type_var, 
                       value="custom", command=self.update_package_ui).pack(side=tk.LEFT, padx=(20, 0))
        
        # Package details
        self.package_details_frame = ttk.Frame(parent)
        self.package_details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Initialize with default package
        self.package_type_var.set("default")
        self.update_package_ui()
    
    def update_package_ui(self):
        """Update package UI based on selection"""
        # Clear previous widgets
        for widget in self.package_details_frame.winfo_children():
            widget.destroy()
        
        package_type = self.package_type_var.get()
        
        if package_type == "default":
            # Show default package selection
            ttk.Label(self.package_details_frame, text="Select Default Package:").pack(anchor=tk.W)
            
            # Get available packages
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, icu_type, daily_rate FROM packages ORDER BY name")
            packages = cursor.fetchall()
            conn.close()
            
            self.default_package_var = tk.StringVar()
            package_combo = ttk.Combobox(self.package_details_frame, textvariable=self.default_package_var, 
                                        state="readonly", width=40)
            package_combo.pack(fill=tk.X, pady=5)
            
            # Format package names
            package_names = [f"{p[1]} ({p[2]}) - {format_currency(p[3])}/day" for p in packages]
            package_combo['values'] = package_names
            
            if packages:
                package_combo.current(0)
                self.selected_package_id = packages[0][0]
            
            # Bind selection event
            def on_package_select(event):
                selected_index = package_combo.current()
                if selected_index >= 0:
                    self.selected_package_id = packages[selected_index][0]
            
            package_combo.bind('<<ComboboxSelected>>', on_package_select)
            
        else:
            # Show custom package selection
            ttk.Label(self.package_details_frame, text="Select Custom Items:").pack(anchor=tk.W)
            
            # Create a frame with scrollbar
            canvas_frame = ttk.Frame(self.package_details_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            canvas = tk.Canvas(canvas_frame)
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Get all items
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, name, price FROM items ORDER BY category, name")
            items = cursor.fetchall()
            conn.close()
            
            # Group items by category
            categories = {}
            for item in items:
                category = item[1]
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            # Create checkboxes for each item
            self.custom_items_vars = {}
            for category, category_items in categories.items():
                ttk.Label(scrollable_frame, text=category.capitalize(), font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
                for item in category_items:
                    var = tk.BooleanVar()
                    cb = ttk.Checkbutton(scrollable_frame, text=f"{item[2]} ({format_currency(item[3])})", 
                                        variable=var)
                    cb.pack(anchor=tk.W)
                    self.custom_items_vars[item[0]] = var
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
    
    def setup_labs_tab(self, parent):
        """Setup labs tab"""
        self.setup_category_tab(parent, "labs")
    
    def setup_drugs_tab(self, parent):
        """Setup drugs tab"""
        self.setup_category_tab(parent, "drugs")
    
    def setup_radiology_tab(self, parent):
        """Setup radiology tab"""
        self.setup_category_tab(parent, "radiology")
    
    def setup_consultations_tab(self, parent):
        """Setup consultations tab"""
        self.setup_category_tab(parent, "consultations")
    
    def setup_category_tab(self, parent, category):
        """Setup a generic category tab"""
        # Item selection
        ttk.Label(parent, text=f"Add {category.capitalize()}:").pack(anchor=tk.W, pady=(10, 5))
        
        # Get items for this category
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM items WHERE category = ? ORDER BY name", (category,))
        items = cursor.fetchall()
        conn.close()
        
        # Item selection frame
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill=tk.X, pady=5)
        
        self.category_vars = getattr(self, f"{category}_vars", {})
        self.category_vars['item'] = tk.StringVar()
        self.category_vars['date'] = tk.StringVar()
        self.category_vars['quantity'] = tk.StringVar()
        self.category_vars['items_list'] = items
        
        setattr(self, f"{category}_vars", self.category_vars)
        
        # Item combobox
        item_combo = ttk.Combobox(item_frame, textvariable=self.category_vars['item'], state="readonly", width=30)
        item_combo.pack(side=tk.LEFT)
        
        # Format item names
        item_names = [f"{item[1]} ({format_currency(item[2])})" for item in items]
        item_combo['values'] = item_names
        
        # Date
        ttk.Label(item_frame, text="Date:").pack(side=tk.LEFT, padx=(10, 0))
        date_entry = ttk.Entry(item_frame, textvariable=self.category_vars['date'], width=12)
        date_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.category_vars['date'].set(datetime.now().strftime("%Y-%m-%d"))
        
        # Quantity
        ttk.Label(item_frame, text="Qty:").pack(side=tk.LEFT, padx=(10, 0))
        qty_entry = ttk.Entry(item_frame, textvariable=self.category_vars['quantity'], width=5)
        qty_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.category_vars['quantity'].set("1")
        
        # Add button
        def add_item():
            self.add_category_item(category)
        
        ttk.Button(item_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=(10, 0))
        
        # Items list
        ttk.Label(parent, text=f"{category.capitalize()} Records:").pack(anchor=tk.W, pady=(10, 5))
        
        # Create treeview for items
        columns = ("Date", "Item", "Quantity", "Price", "Total")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Store tree reference
        self.category_vars['tree'] = tree
        
        # Load existing items
        self.load_category_items(category)
    
    def load_category_items(self, category):
        """Load existing items for a category"""
        if not hasattr(self, 'current_patient_id'):
            return
        
        # Clear existing items
        tree = self.category_vars['tree']
        for item in tree.get_children():
            tree.delete(item)
        
        # Get items from database
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        table_name = f"patient_{category}"
        cursor.execute(f"""
            SELECT p.date, i.name, p.quantity, i.price
            FROM {table_name} p
            JOIN items i ON p.item_id = i.id
            WHERE p.patient_id = ?
            ORDER BY p.date
        """, (self.current_patient_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Add items to tree
        for item in items:
            date, name, quantity, price = item
            total = quantity * price
            tree.insert("", "end", values=(date, name, quantity, format_currency(price), format_currency(total)))
    
    def add_category_item(self, category):
        """Add an item to a category"""
        if not hasattr(self, 'current_patient_id'):
            messagebox.showwarning("Warning", "Please select a patient first")
            return
        
        # Get selected item
        item_text = self.category_vars['item'].get()
        if not item_text:
            messagebox.showerror("Error", "Please select an item")
            return
        
        # Extract item name and find ID
        item_name = item_text.split(" (")[0]
        items_list = self.category_vars['items_list']
        item_id = None
        item_price = 0
        
        for item in items_list:
            if item[1] == item_name:
                item_id = item[0]
                item_price = item[2]
                break
        
        if not item_id:
            messagebox.showerror("Error", "Invalid item selected")
            return
        
        # Get date and quantity
        date = self.category_vars['date'].get().strip()
        try:
            quantity = int(self.category_vars['quantity'].get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return
        
        if not date:
            messagebox.showerror("Error", "Please enter a date")
            return
        
        # Add to database
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        table_name = f"patient_{category}"
        try:
            cursor.execute(f"""
                INSERT INTO {table_name} (patient_id, date, item_id, quantity)
                VALUES (?, ?, ?, ?)
            """, (self.current_patient_id, date, item_id, quantity))
            conn.commit()
            messagebox.showinfo("Success", f"{category.capitalize()} item added successfully")
            
            # Update UI
            self.load_category_items(category)
            
            # Clear fields
            self.category_vars['item'].set("")
            self.category_vars['quantity'].set("1")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
        finally:
            conn.close()
    
    def load_patients(self):
        """Load patients into listbox"""
        self.patients_listbox.delete(0, tk.END)
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, icu_type FROM patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        
        for patient in patients:
            self.patients_listbox.insert(tk.END, f"{patient[0]}: {patient[1]} ({patient[2]})")
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selection = self.patients_listbox.curselection()
        if selection:
            index = selection[0]
            patient_text = self.patients_listbox.get(index)
            patient_id = int(patient_text.split(":")[0])
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, icu_type, admission_date, discharge_date FROM patients WHERE id = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            if patient:
                self.name_var.set(patient[0])
                self.icu_type_var.set(patient[1])
                self.admission_date_var.set(patient[2])
                self.discharge_date_var.set(patient[3] or "")
                self.current_patient_id = patient_id
                
                # Load items for all categories
                self.load_category_items("labs")
                self.load_category_items("drugs")
                self.load_category_items("radiology")
                self.load_category_items("consultations")
    
    def add_patient(self):
        """Add a new patient"""
        # Create a new window for adding patient
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add Patient")
        add_window.geometry("400x250")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        # Center the window
        add_window.geometry("+%d+%d" % (add_window.winfo_screenwidth()/2 - 200,
                                        add_window.winfo_screenheight()/2 - 125))
        
        ttk.Label(add_window, text="Patient Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(add_window, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(add_window, text="ICU Type:").pack()
        icu_type_var = tk.StringVar()
        icu_type_combo = ttk.Combobox(add_window, textvariable=icu_type_var, state="readonly", width=38)
        icu_type_combo['values'] = ["ICU", "Medium_ICU"]
        icu_type_combo.pack(pady=5)
        icu_type_combo.set("ICU")
        
        ttk.Label(add_window, text="Admission Date (YYYY-MM-DD):").pack()
        admission_entry = ttk.Entry(add_window, width=40)
        admission_entry.pack(pady=5)
        admission_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        def save_patient():
            name = name_entry.get().strip()
            icu_type = icu_type_var.get()
            admission_date = admission_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a patient name")
                return
            
            if not icu_type:
                messagebox.showerror("Error", "Please select an ICU type")
                return
            
            if not admission_date:
                messagebox.showerror("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO patients (name, icu_type, admission_date)
                    VALUES (?, ?, ?)
                """, (name, icu_type, admission_date))
                conn.commit()
                messagebox.showinfo("Success", "Patient added successfully")
                add_window.destroy()
                self.load_patients()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_patient).pack(pady=10)
        
        # Bind Enter key to save
        admission_entry.bind("<Return>", lambda event: save_patient())
    
    def edit_patient(self):
        """Edit selected patient"""
        if not hasattr(self, 'current_patient_id'):
            messagebox.showwarning("Warning", "Please select a patient to edit")
            return
        
        # Get current patient info
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, icu_type, admission_date, discharge_date FROM patients WHERE id = ?", (self.current_patient_id,))
        patient = cursor.fetchone()
        conn.close()
        
        if not patient:
            return
        
        # Create a new window for editing patient
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Patient")
        edit_window.geometry("400x300")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (edit_window.winfo_screenwidth()/2 - 200,
                                         edit_window.winfo_screenheight()/2 - 150))
        
        ttk.Label(edit_window, text="Patient Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(edit_window, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, patient[0])
        name_entry.focus()
        
        ttk.Label(edit_window, text="ICU Type:").pack()
        icu_type_var = tk.StringVar()
        icu_type_combo = ttk.Combobox(edit_window, textvariable=icu_type_var, state="readonly", width=38)
        icu_type_combo['values'] = ["ICU", "Medium_ICU"]
        icu_type_combo.pack(pady=5)
        icu_type_combo.set(patient[1])
        
        ttk.Label(edit_window, text="Admission Date (YYYY-MM-DD):").pack()
        admission_entry = ttk.Entry(edit_window, width=40)
        admission_entry.pack(pady=5)
        admission_entry.insert(0, patient[2])
        
        ttk.Label(edit_window, text="Discharge Date (YYYY-MM-DD):").pack()
        discharge_entry = ttk.Entry(edit_window, width=40)
        discharge_entry.pack(pady=5)
        if patient[3]:
            discharge_entry.insert(0, patient[3])
        
        def save_patient():
            name = name_entry.get().strip()
            icu_type = icu_type_var.get()
            admission_date = admission_entry.get().strip()
            discharge_date = discharge_entry.get().strip() or None
            
            if not name:
                messagebox.showerror("Error", "Please enter a patient name")
                return
            
            if not icu_type:
                messagebox.showerror("Error", "Please select an ICU type")
                return
            
            if not admission_date:
                messagebox.showerror("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE patients 
                    SET name = ?, icu_type = ?, admission_date = ?, discharge_date = ?
                    WHERE id = ?
                """, (name, icu_type, admission_date, discharge_date, self.current_patient_id))
                conn.commit()
                messagebox.showinfo("Success", "Patient updated successfully")
                edit_window.destroy()
                self.load_patients()
                self.name_var.set(name)
                self.icu_type_var.set(icu_type)
                self.admission_date_var.set(admission_date)
                self.discharge_date_var.set(discharge_date or "")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_patient).pack(pady=10)
        
        # Bind Enter key to save
        discharge_entry.bind("<Return>", lambda event: save_patient())
    
    def delete_patient(self):
        """Delete selected patient"""
        if not hasattr(self, 'current_patient_id'):
            messagebox.showwarning("Warning", "Please select a patient to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?")
        if not result:
            return
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            # Delete related records first
            cursor.execute("DELETE FROM patient_packages WHERE patient_id = ?", (self.current_patient_id,))
            cursor.execute("DELETE FROM patient_labs WHERE patient_id = ?", (self.current_patient_id,))
            cursor.execute("DELETE FROM patient_drugs WHERE patient_id = ?", (self.current_patient_id,))
            cursor.execute("DELETE FROM patient_radiology WHERE patient_id = ?", (self.current_patient_id,))
            cursor.execute("DELETE FROM patient_consultations WHERE patient_id = ?", (self.current_patient_id,))
            
            # Delete the patient
            cursor.execute("DELETE FROM patients WHERE id = ?", (self.current_patient_id,))
            conn.commit()
            
            messagebox.showinfo("Success", "Patient deleted successfully")
            self.load_patients()
            
            # Clear details
            self.name_var.set("")
            self.icu_type_var.set("")
            self.admission_date_var.set("")
            self.discharge_date_var.set("")
            delattr(self, 'current_patient_id')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete patient: {e}")
        finally:
            conn.close()
    
    def calculate_cost(self):
        """Calculate total cost for selected patient"""
        if not hasattr(self, 'current_patient_id'):
            messagebox.showwarning("Warning", "Please select a patient first")
            return

        # Get patient info
        conn_patients = sqlite3.connect("db/patients.db")
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("""
            SELECT name, icu_type, admission_date, discharge_date
            FROM patients WHERE id = ?
        """, (self.current_patient_id,))
        patient = cursor_patients.fetchone()

        if not patient:
            conn_patients.close()
            return

        name, icu_type, admission_date, discharge_date = patient

        # Calculate ICU days
        from datetime import datetime
        admission = datetime.strptime(admission_date, "%Y-%m-%d")
        if discharge_date:
            discharge = datetime.strptime(discharge_date, "%Y-%m-%d")
        else:
            discharge = datetime.now()

        icu_days = (discharge - admission).days
        if icu_days < 0:
            icu_days = 0

        # Get package rate from items.db
        conn_items = sqlite3.connect("db/items.db")
        cursor_items = conn_items.cursor()
        cursor_items.execute("""
            SELECT daily_rate FROM packages WHERE icu_type = ?
        """, (icu_type,))
        package_result = cursor_items.fetchone()
        daily_rate = package_result[0] if package_result else 0.0
        conn_items.close()
        
        icu_cost = icu_days * daily_rate

        # Calculate category costs
        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0

        for category in categories:
            cursor_patients.execute(f"""
                SELECT item_id, quantity FROM patient_{category}
                WHERE patient_id = ?
            """, (self.current_patient_id,))
            items = cursor_patients.fetchall()

            category_cost = 0.0
            if items:
                conn_items = sqlite3.connect("db/items.db")
                cursor_items = conn_items.cursor()
                for item_id, quantity in items:
                    cursor_items.execute("SELECT price FROM items WHERE id = ?", (item_id,))
                    price_result = cursor_items.fetchone()
                    if price_result:
                        category_cost += quantity * price_result[0]
                conn_items.close()

            category_costs[category] = category_cost
            total_category_cost += category_cost

        conn_patients.close()

        # Calculate total cost
        total_cost = icu_cost + total_category_cost

        # Show results
        result_text = f"""
Patient: {name}
ICU Type: {icu_type}
ICU Days: {icu_days} days
Admission: {admission_date}
Discharge: {discharge_date or 'N/A'}

Cost Breakdown:
ICU Cost: {icu_days} days × {format_currency(daily_rate)} = {format_currency(icu_cost)}
Labs: {format_currency(category_costs['labs'])}
Drugs: {format_currency(category_costs['drugs'])}
Radiology: {format_currency(category_costs['radiology'])}
Consultations: {format_currency(category_costs['consultations'])}

Total Cost: {format_currency(total_cost)}
        """

        messagebox.showinfo("Cost Calculation", result_text)
    
    def export_cost_sheet(self):
        """Export cost sheet for selected patient"""
        if not hasattr(self, 'current_patient_id'):
            messagebox.showwarning("Warning", "Please select a patient first")
            return

        # Get patient info
        conn_patients = sqlite3.connect("db/patients.db")
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("""
        SELECT name, icu_type, admission_date, discharge_date 
        FROM patients WHERE id = ?
        """, (self.current_patient_id,))
        patient = cursor_patients.fetchone()
        if not patient:
            conn_patients.close()
            return
        name, icu_type, admission_date, discharge_date = patient

        # Calculate ICU days
        from datetime import datetime
        admission = datetime.strptime(admission_date, "%Y-%m-%d")
        if discharge_date:
            discharge = datetime.strptime(discharge_date, "%Y-%m-%d")
        else:
            discharge = datetime.now()
        icu_days = (discharge - admission).days
        if icu_days < 0:
            icu_days = 0

        # Get package rate from items.db
        conn_items = sqlite3.connect("db/items.db")
        cursor_items = conn_items.cursor()
        cursor_items.execute("""
        SELECT daily_rate FROM packages WHERE icu_type = ?
        """, (icu_type,))
        package_result = cursor_items.fetchone()
        daily_rate = package_result[0] if package_result else 0.0
        icu_cost = icu_days * daily_rate

        # Calculate category costs
        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0
        category_details = {}
        for category in categories:
            cursor_patients.execute(f"""
                SELECT item_id, quantity, date FROM patient_{category}
                WHERE patient_id = ?
                ORDER BY date
            """, (self.current_patient_id,))
            items = cursor_patients.fetchall()

            category_cost = 0.0
            details = []
            if items:
                for item_id, quantity, date in items:
                    cursor_items.execute("SELECT name, price FROM items WHERE id = ?", (item_id,))
                    item_result = cursor_items.fetchone()
                    if item_result:
                        item_name, price = item_result
                        total = quantity * price
                        category_cost += total
                        details.append((date, item_name, quantity, price, total))

            category_costs[category] = category_cost
            category_details[category] = details
            total_category_cost += category_cost

        conn_items.close()
        conn_patients.close()

        # Calculate total cost
        total_cost = icu_cost + total_category_cost

        # Export to CSV
        import csv
        from datetime import datetime as dt
        filename = f"patient_{self.current_patient_id}_cost_sheet_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Patient Cost Sheet"])
                writer.writerow([])
                writer.writerow(["Patient Name:", name])
                writer.writerow(["ICU Type:", icu_type])
                writer.writerow(["Admission Date:", admission_date])
                writer.writerow(["Discharge Date:", discharge_date or 'N/A'])
                writer.writerow([])
                writer.writerow(["Cost Breakdown:"])
                writer.writerow(["ICU Days:", icu_days])
                writer.writerow(["Daily Rate:", format_currency(daily_rate)])
                writer.writerow(["ICU Cost:", format_currency(icu_cost)])
                writer.writerow([])
                for category in categories:
                    writer.writerow([f"{category.capitalize()}:", format_currency(category_costs[category])])
                    # Add itemized details
                    if category_details[category]:
                        writer.writerow([f"  Date", "Item", "Quantity", "Price", "Total"])
                        for item in category_details[category]:
                            date, item_name, qty, price, total = item
                            writer.writerow([f"  {date}", item_name, qty, format_currency(price), format_currency(total)])
                    writer.writerow([]) # Empty row after category
                writer.writerow(["Total Cost:", format_currency(total_cost)])

            messagebox.showinfo("Export Success", f"Cost sheet exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export cost sheet: {e}")
