import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
from .utils import format_currency, calculate_hours

class PatientModule:
    def __init__(self, parent):
        self.parent = parent
        self.doctor_module = None
        self.nurse_module = None
        self.setup_ui()
        self.load_patients()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Patients list frame
        list_frame = ttk.LabelFrame(main_frame, text="Patients", padding="10")
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        # Patients list with checkboxes
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.patient_vars = {}
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(buttons_frame, text="Add Patient", command=self.add_patient).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(buttons_frame, text="Edit Patient", command=self.edit_patient).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(buttons_frame, text="Delete Patient", command=self.delete_patient).pack(fill=tk.X)
        
        # Patient details frame
        details_frame = ttk.LabelFrame(main_frame, text="Patient Details", padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        # Patient info
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Admission Date:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.admission_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.admission_date_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(details_frame, text="Discharge Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.discharge_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.discharge_date_var, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Notebook for tabs
        notebook = ttk.Notebook(details_frame)
        notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Stays tab
        self.stays_tab_frame = ttk.Frame(notebook)
        notebook.add(self.stays_tab_frame, text="Stays")
        self.setup_stays_tab(self.stays_tab_frame)
        
        # Labs tab
        self.labs_tab_frame = ttk.Frame(notebook)
        notebook.add(self.labs_tab_frame, text="Labs")
        self.setup_labs_tab(self.labs_tab_frame)
        
        # Drugs tab
        self.drugs_tab_frame = ttk.Frame(notebook)
        notebook.add(self.drugs_tab_frame, text="Drugs")
        self.setup_drugs_tab(self.drugs_tab_frame)
        
        # Radiology tab
        self.radiology_tab_frame = ttk.Frame(notebook)
        notebook.add(self.radiology_tab_frame, text="Radiology")
        self.setup_radiology_tab(self.radiology_tab_frame)
        
        # Consultations tab
        self.consultations_tab_frame = ttk.Frame(notebook)
        notebook.add(self.consultations_tab_frame, text="Consultations")
        self.setup_consultations_tab(self.consultations_tab_frame)
        
        # Cost calculation
        cost_frame = ttk.LabelFrame(details_frame, text="Cost Calculation", padding="5")
        cost_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(cost_frame, text="Calculate Total Cost", command=self.calculate_cost).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cost_frame, text="Export Cost Sheet", command=self.export_cost_sheet).pack(side=tk.LEFT)
        
        # Configure grid weights
        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(3, weight=1)

    def get_selected_patients(self):
        """Get a list of selected patient IDs"""
        return [patient_id for patient_id, var in self.patient_vars.items() if var.get()]

    def setup_stays_tab(self, parent):
        """Setup the patient stays tab"""
        # Add stay frame
        add_frame = ttk.Frame(parent, padding="5")
        add_frame.pack(fill=tk.X)

        ttk.Label(add_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.stay_date_entry = DateEntry(add_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.stay_date_entry.pack(side=tk.LEFT)

        ttk.Label(add_frame, text="Care Level:").pack(side=tk.LEFT, padx=(10, 5))
        self.stay_care_level_var = tk.StringVar()
        self.stay_care_level_combo = ttk.Combobox(add_frame, textvariable=self.stay_care_level_var, state="readonly")
        self.stay_care_level_combo.pack(side=tk.LEFT)
        self.load_care_levels_for_combo()

        ttk.Button(add_frame, text="Add Stay", command=self.add_stay).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_frame, text="Remove Selected Stay", command=self.remove_stay).pack(side=tk.LEFT, padx=(5, 0))

        # Stays list
        list_frame = ttk.LabelFrame(parent, text="Recorded Stays", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.stays_tree = ttk.Treeview(list_frame, columns=("Date", "Care Level", "Cost"), show="headings")
        self.stays_tree.heading("Date", text="Date")
        self.stays_tree.heading("Care Level", text="Care Level")
        self.stays_tree.heading("Cost", text="Cost")
        self.stays_tree.pack(fill=tk.BOTH, expand=True)

    def load_care_levels_for_combo(self):
        """Load care levels into the combobox"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, daily_rate FROM care_levels ORDER BY name")
        self.care_levels = cursor.fetchall()
        conn.close()
        
        level_names = [f"{name} ({format_currency(rate)})" for id, name, rate in self.care_levels]
        self.stay_care_level_combo['values'] = level_names
        if level_names:
            self.stay_care_level_combo.current(0)

    def add_stay(self):
        """Add a new stay record for the selected patient"""
        selected_patients = self.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient.")
            return

        stay_date = self.stay_date_entry.get_date().strftime('%Y-%m-%d')
        selected_level_text = self.stay_care_level_var.get()
        
        if not stay_date or not selected_level_text:
            messagebox.showerror("Error", "Please select a date and care level.")
            return

        # Find the ID of the selected care level
        care_level_id = None
        for id, name, rate in self.care_levels:
            if f"{name} ({format_currency(rate)})" == selected_level_text:
                care_level_id = id
                break
        
        if not care_level_id:
            messagebox.showerror("Error", "Invalid care level selected.")
            return

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            for patient_id in selected_patients:
                # Check for existing stay on the same date
                cursor.execute("SELECT id FROM patient_stays WHERE patient_id = ? AND stay_date = ?", (patient_id, stay_date))
                if cursor.fetchone():
                    messagebox.showwarning("Warning", f"A stay for this date already exists for one or more selected patients. It will be updated.")
                    cursor.execute("UPDATE patient_stays SET care_level_id = ? WHERE patient_id = ? AND stay_date = ?", (care_level_id, patient_id, stay_date))
                else:
                    cursor.execute("INSERT INTO patient_stays (patient_id, stay_date, care_level_id) VALUES (?, ?, ?)", (patient_id, stay_date, care_level_id))
            conn.commit()
            messagebox.showinfo("Success", "Stay record(s) added/updated successfully.")
            if len(selected_patients) == 1:
                self.load_stays()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add stay record: {e}")
        finally:
            conn.close()

    def remove_stay(self):
        """Remove the selected stay record"""
        selected_item = self.stays_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stay to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this stay record?"):
            item_data = self.stays_tree.item(selected_item)
            stay_date = item_data['values'][0]

            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM patient_stays WHERE patient_id = ? AND stay_date = ?", (self.current_patient_id, stay_date))
                conn.commit()
                messagebox.showinfo("Success", "Stay record removed successfully.")
                self.load_stays()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to remove stay: {e}")
            finally:
                conn.close()

    def load_stays(self):
        """Load stay records for the selected patient"""
        for i in self.stays_tree.get_children():
            self.stays_tree.delete(i)

        if not hasattr(self, 'current_patient_id'):
            return

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor.execute("""
            SELECT ps.stay_date, cl.name, cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
            ORDER BY ps.stay_date
        """, (self.current_patient_id,))
        
        for row in cursor.fetchall():
            self.stays_tree.insert("", "end", values=(row[0], row[1], format_currency(row[2])))
        conn.close()

    def clear_all_tabs(self):
        """Clear all data from the tabs"""
        for i in self.stays_tree.get_children():
            self.stays_tree.delete(i)
        for category in ["labs", "drugs", "radiology", "consultations"]:
            vars_attr = getattr(self, f"{category}_vars", None)
            if vars_attr and 'tree' in vars_attr:
                tree = vars_attr['tree']
                for item in tree.get_children():
                    tree.delete(item)
    
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
        # Clear previous widgets
        for widget in parent.winfo_children():
            widget.destroy()

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
        
        category_vars = getattr(self, f"{category}_vars", {})
        category_vars['item'] = tk.StringVar()
        category_vars['date'] = tk.StringVar()
        category_vars['quantity'] = tk.StringVar()
        category_vars['items_list'] = items
        
        setattr(self, f"{category}_vars", category_vars)
        
        # Item combobox
        item_combo = ttk.Combobox(item_frame, textvariable=category_vars['item'], state="readonly", width=30)
        category_vars['item_combo'] = item_combo
        item_combo.pack(side=tk.LEFT)
        
        # Format item names
        item_names = [f"{item[1]} ({format_currency(item[2])})" for item in items]
        item_combo['values'] = item_names
        if item_names:
            item_combo.current(0)
        
        # Date
        ttk.Label(item_frame, text="Date:").pack(side=tk.LEFT, padx=(10, 0))
        date_entry = ttk.Entry(item_frame, textvariable=category_vars['date'], width=12)
        date_entry.pack(side=tk.LEFT, padx=(5, 0))
        category_vars['date'].set(datetime.now().strftime("%Y-%m-%d"))
        
        # Quantity
        ttk.Label(item_frame, text="Qty:").pack(side=tk.LEFT, padx=(10, 0))
        qty_entry = ttk.Entry(item_frame, textvariable=category_vars['quantity'], width=5)
        qty_entry.pack(side=tk.LEFT, padx=(5, 0))
        category_vars['quantity'].set("1")
        
        # Add button
        def add_item():
            self.add_category_item(category)
        
        ttk.Button(item_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=(10, 0))

        # Remove button
        def remove_item():
            self.remove_category_item(category)

        ttk.Button(item_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=(5, 0))
        
        # Items list
        ttk.Label(parent, text=f"{category.capitalize()} Records:").pack(anchor=tk.W, pady=(10, 5))
        
        # Create treeview for items
        columns = ("ID", "Date", "Item", "Quantity", "Price", "Total")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        
        tree.heading("ID", text="ID")
        tree.column("ID", width=0, stretch=tk.NO) # Hidden column
        for col in columns[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Store tree reference
        category_vars['tree'] = tree
        
        # Load existing items
        self.load_category_items(category)
    
    def load_category_items(self, category):
        """Load existing items for a category"""
        category_vars = getattr(self, f"{category}_vars")
        if not hasattr(self, 'current_patient_id'):
            return
        
        # Clear existing items
        tree = category_vars['tree']
        for item in tree.get_children():
            tree.delete(item)
        
        # Get items from database
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        # Attach items database
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")

        table_name = f"patient_{category}"
        cursor.execute(f"""
            SELECT p.id, p.date, i.name, p.quantity, i.price
            FROM {table_name} p
            JOIN items_db.items i ON p.item_id = i.id
            WHERE p.patient_id = ?
            ORDER BY p.date
        """, (self.current_patient_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Add items to tree
        for item in items:
            record_id, date, name, quantity, price = item
            total = quantity * price
            tree.insert("", "end", values=(record_id, date, name, quantity, format_currency(price), format_currency(total)))
    
    def add_category_item(self, category):
        """Add an item to a category for selected patients"""
        category_vars = getattr(self, f"{category}_vars")
        selected_patients = self.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient")
            return
        
        # Get selected item
        item_text = category_vars['item'].get()
        if not item_text:
            messagebox.showerror("Error", "Please select an item")
            print("Error: Please select an item")
            return
        
        # Extract item name and find ID
        item_name = item_text.split(" (")[0]
        items_list = category_vars['items_list']
        item_id = None
        
        for item in items_list:
            if item[1] == item_name:
                item_id = item[0]
                break
        
        if not item_id:
            messagebox.showerror("Error", "Invalid item selected")
            print("Error: Invalid item selected")
            return
        
        # Get date and quantity
        date = category_vars['date'].get().strip()
        try:
            quantity = int(category_vars['quantity'].get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            print("Error: Please enter a valid quantity")
            return
        
        if not date:
            messagebox.showerror("Error", "Please enter a date")
            print("Error: Please enter a date")
            return
        
        # Add to database
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        table_name = f"patient_{category}"
        try:
            for patient_id in selected_patients:
                cursor.execute(f"""
                    INSERT INTO {table_name} (patient_id, date, item_id, quantity)
                    VALUES (?, ?, ?, ?)
                """, (patient_id, date, item_id, quantity))
            conn.commit()
            messagebox.showinfo("Success", f"{category.capitalize()} item added to {len(selected_patients)} patient(s) successfully")
            
            # Update UI if a single patient is selected
            if len(selected_patients) == 1:
                self.load_category_items(category)
            
            # Reset fields
            if category_vars.get('items_list'):
                category_vars['item_combo'].current(0)
            else:
                category_vars['item'].set("")
            category_vars['quantity'].set("1")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
            print(f"Error: Failed to add item: {e}")
        finally:
            conn.close()

    def remove_category_item(self, category):
        """Remove the selected item from a category"""
        category_vars = getattr(self, f"{category}_vars")
        tree = category_vars.get('tree')
        if not tree:
            return

        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this item?")
        if not result:
            return

        item_values = tree.item(selected_item, 'values')
        record_id = item_values[0]

        # Delete from database
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        table_name = f"patient_{category}"
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
            conn.commit()
            messagebox.showinfo("Success", "Item removed successfully")
            
            # Update UI
            self.load_category_items(category)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to remove item: {e}")
            print(f"Error: Failed to remove item: {e}")
        finally:
            conn.close()
    
    def load_patients(self):
        """Load patients into a list of checkboxes"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.patient_vars = {}
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        
        for patient in patients:
            patient_id, patient_name = patient
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.scrollable_frame, text=f"{patient_id}: {patient_name}", variable=var,
                                 command=self.on_patient_select)
            cb.pack(fill='x', padx=5, pady=2)
            self.patient_vars[patient_id] = var
    
    def on_patient_select(self):
        """Handle patient selection from checkbox"""
        selected_patients = self.get_selected_patients()
        
        if len(selected_patients) == 1:
            patient_id = selected_patients[0]
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            if patient:
                self.name_var.set(patient[0])
                self.admission_date_var.set(patient[1])
                self.discharge_date_var.set(patient[2] or "")
                self.current_patient_id = patient_id
                
                # Load items for all categories
                self.load_stays()
                self.load_category_items("labs")
                self.load_category_items("drugs")
                self.load_category_items("radiology")
                self.load_category_items("consultations")
        else:
            # Clear details if none or multiple are selected
            self.name_var.set("")
            self.admission_date_var.set("")
            self.discharge_date_var.set("")
            if hasattr(self, 'current_patient_id'):
                delattr(self, 'current_patient_id')
            
            # Clear category lists
            self.clear_all_tabs()
    
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
        
        ttk.Label(add_window, text="Admission Date:").pack()
        admission_entry = DateEntry(add_window, width=38, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        admission_entry.pack(pady=5)
        
        def save_patient():
            name = name_entry.get().strip()
            admission_date = admission_entry.get_date().strftime('%Y-%m-%d')
            
            if not name:
                messagebox.showerror("Error", "Please enter a patient name")
                return
            
            if not admission_date:
                messagebox.showerror("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO patients (name, admission_date) VALUES (?, ?)", (name, admission_date))
                conn.commit()
                messagebox.showinfo("Success", "Patient added successfully")
                add_window.destroy()
                self.load_patients()
                self._refresh_other_modules()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add patient: {e}")
                print(f"Error: Failed to add patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(add_window, text="Save", command=save_patient).pack(pady=10)
        
        # Bind Enter key to save
        admission_entry.bind("<Return>", lambda event: save_patient())
    
    def edit_patient(self):
        """Edit selected patient"""
        selected_patients = self.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to edit")
            return
        self.current_patient_id = selected_patients[0]
        
        # Get current patient info
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (self.current_patient_id,))
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
        
        ttk.Label(edit_window, text="Admission Date:").pack()
        admission_entry = DateEntry(edit_window, width=38, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        admission_entry.pack(pady=5)
        admission_entry.set_date(patient[1])
        
        ttk.Label(edit_window, text="Discharge Date:").pack()
        discharge_entry = DateEntry(edit_window, width=38, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        discharge_entry.pack(pady=5)
        if patient[2]:
            discharge_entry.set_date(patient[2])
        else:
            discharge_entry.set_date(None)
        
        def save_patient():
            name = name_entry.get().strip()
            admission_date = admission_entry.get_date().strftime('%Y-%m-%d')
            discharge_date = discharge_entry.get_date().strftime('%Y-%m-%d') if discharge_entry.get() else None
            
            if not name:
                messagebox.showerror("Error", "Please enter a patient name")
                return
            
            if not admission_date:
                messagebox.showerror("Error", "Please enter an admission date")
                return
            
            conn = sqlite3.connect("db/patients.db")
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE patients SET name = ?, admission_date = ?, discharge_date = ? WHERE id = ?", 
                               (name, admission_date, discharge_date, self.current_patient_id))
                conn.commit()
                messagebox.showinfo("Success", "Patient updated successfully")
                edit_window.destroy()
                self.load_patients()
                self._refresh_other_modules()
                self.name_var.set(name)
                self.admission_date_var.set(admission_date)
                self.discharge_date_var.set(discharge_date or "")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update patient: {e}")
                print(f"Error: Failed to update patient: {e}")
            finally:
                conn.close()
        
        ttk.Button(edit_window, text="Save", command=save_patient).pack(pady=10)
        
        # Bind Enter key to save
        discharge_entry.bind("<Return>", lambda event: save_patient())
    
    def delete_patient(self):
        """Delete selected patient(s)"""
        selected_patients = self.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_patients)} patient(s)?")
        if not result:
            return
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        try:
            for patient_id in selected_patients:
                # Delete related records first
                cursor.execute("DELETE FROM patient_stays WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_labs WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_drugs WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_radiology WHERE patient_id = ?", (patient_id,))
                cursor.execute("DELETE FROM patient_consultations WHERE patient_id = ?", (patient_id,))
                
                # Delete the patient
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
            
            messagebox.showinfo("Success", f"{len(selected_patients)} patient(s) deleted successfully")
            self.load_patients()
            self._refresh_other_modules()
            
            # Clear details
            self.on_patient_select()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to delete patient: {e}")
            print(f"Error: Failed to delete patient: {e}")
        finally:
            conn.close()
    
    def calculate_cost(self):
        """Calculate total cost for selected patient"""
        selected_patients = self.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to calculate cost")
            return
        self.current_patient_id = selected_patients[0]

        # Get patient info
        conn_patients = sqlite3.connect("db/patients.db")
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (self.current_patient_id,))
        patient = cursor_patients.fetchone()

        if not patient:
            conn_patients.close()
            return

        name, admission_date, discharge_date = patient

        # Calculate stay costs
        cursor_patients.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor_patients.execute("""
            SELECT cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
        """, (self.current_patient_id,))
        stay_costs = [row[0] for row in cursor_patients.fetchall()]
        total_stay_cost = sum(stay_costs)

        # Calculate category costs
        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0

        for category in categories:
            cursor_patients.execute(f"SELECT item_id, quantity FROM patient_{category} WHERE patient_id = ?", (self.current_patient_id,))
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

        # Calculate doctor costs
        total_doctor_cost = 0.0
        try:
            conn_docs = sqlite3.connect("db/doctors.db")
            cursor_docs = conn_docs.cursor()
            cursor_docs.execute("SELECT doctor_id, arrival_datetime, leave_datetime FROM doctor_shifts WHERE patient_id = ?", (self.current_patient_id,))
            doctor_shifts = cursor_docs.fetchall()
            total_doctor_shift_cost = 0.0
            for doc_id, arrival, leave in doctor_shifts:
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                leave_dt = datetime.strptime(leave, "%Y-%m-%d %H:%M:%S")
                hours = calculate_hours(arrival_dt, leave_dt)
                cursor_docs.execute("SELECT hourly_rate FROM doctors WHERE id = ?", (doc_id,))
                rate_res = cursor_docs.fetchone()
                if rate_res:
                    total_doctor_shift_cost += hours * rate_res[0]
            cursor_docs.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor_docs.execute("SELECT i.bonus_amount FROM doctor_interventions di JOIN interventions_db.interventions i ON di.intervention_id = i.id WHERE di.patient_id = ?", (self.current_patient_id,))
            doc_interventions = cursor_docs.fetchall()
            total_doctor_intervention_cost = sum(i[0] for i in doc_interventions)
            total_doctor_cost = total_doctor_shift_cost + total_doctor_intervention_cost
            conn_docs.close()
        except sqlite3.Error as e:
            print(f"Error calculating doctor costs: {e}")

        # Calculate nurse costs
        total_nurse_cost = 0.0
        try:
            conn_nurses = sqlite3.connect("db/nurses.db")
            cursor_nurses = conn_nurses.cursor()
            cursor_nurses.execute("SELECT nurse_id, arrival_datetime, leave_datetime FROM nurse_shifts WHERE patient_id = ?", (self.current_patient_id,))
            nurse_shifts = cursor_nurses.fetchall()
            total_nurse_shift_cost = 0.0
            for nurse_id, arrival, leave in nurse_shifts:
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                leave_dt = datetime.strptime(leave, "%Y-%m-%d %H:%M:%S")
                hours = calculate_hours(arrival_dt, leave_dt)
                cursor_nurses.execute("SELECT hourly_rate FROM nurses WHERE id = ?", (nurse_id,))
                rate_res = cursor_nurses.fetchone()
                if rate_res:
                    total_nurse_shift_cost += hours * rate_res[0]
            cursor_nurses.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor_nurses.execute("SELECT i.bonus_amount FROM nurse_interventions ni JOIN interventions_db.interventions i ON ni.intervention_id = i.id WHERE ni.patient_id = ?", (self.current_patient_id,))
            nurse_interventions = cursor_nurses.fetchall()
            total_nurse_intervention_cost = sum(i[0] for i in nurse_interventions)
            total_nurse_cost = total_nurse_shift_cost + total_nurse_intervention_cost
            conn_nurses.close()
        except sqlite3.Error as e:
            print(f"Error calculating nurse costs: {e}")

        # Calculate total cost
        total_cost = total_stay_cost + total_category_cost + total_doctor_cost + total_nurse_cost

        # Show results
        result_text = f"""
Patient: {name}
Admission: {admission_date}
Discharge: {discharge_date or 'N/A'}

Cost Breakdown:
Stays ({len(stay_costs)} days): {format_currency(total_stay_cost)}
Labs: {format_currency(category_costs['labs'])}
Drugs: {format_currency(category_costs['drugs'])}
Radiology: {format_currency(category_costs['radiology'])}
Consultations: {format_currency(category_costs['consultations'])}
Doctor Costs: {format_currency(total_doctor_cost)}
Nurse Costs: {format_currency(total_nurse_cost)}

Total Cost: {format_currency(total_cost)}
        """
        messagebox.showinfo("Cost Calculation", result_text)
    
    def export_cost_sheet(self):
        """Export cost sheet for selected patient"""
        selected_patients = self.get_selected_patients()
        if len(selected_patients) != 1:
            messagebox.showwarning("Warning", "Please select exactly one patient to export a cost sheet")
            return
        self.current_patient_id = selected_patients[0]

        # Get patient info
        conn_patients = sqlite3.connect("db/patients.db")
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("SELECT name, admission_date, discharge_date FROM patients WHERE id = ?", (self.current_patient_id,))
        patient = cursor_patients.fetchone()
        if not patient:
            conn_patients.close()
            return
        name, admission_date, discharge_date = patient

        # Calculate stay costs
        conn_items = sqlite3.connect("db/items.db")
        cursor_items = conn_items.cursor()
        cursor_patients.execute("ATTACH DATABASE 'db/items.db' AS items_db")
        cursor_patients.execute("""
            SELECT ps.stay_date, cl.name, cl.daily_rate
            FROM patient_stays ps
            JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
            WHERE ps.patient_id = ?
            ORDER BY ps.stay_date
        """, (self.current_patient_id,))
        stays = cursor_patients.fetchall()
        total_stay_cost = sum(row[2] for row in stays)

        # Calculate category costs
        categories = ["labs", "drugs", "radiology", "consultations"]
        category_costs = {}
        total_category_cost = 0.0
        category_details = {}
        for category in categories:
            cursor_patients.execute(f"SELECT item_id, quantity, date FROM patient_{category} WHERE patient_id = ? ORDER BY date", (self.current_patient_id,))
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

        # Calculate doctor costs
        total_doctor_cost = 0.0
        doctor_shift_details = []
        doctor_intervention_details = []
        try:
            conn_docs = sqlite3.connect("db/doctors.db")
            cursor_docs = conn_docs.cursor()
            cursor_docs.execute("SELECT doctor_id, arrival_datetime, leave_datetime FROM doctor_shifts WHERE patient_id = ?", (self.current_patient_id,))
            doctor_shifts = cursor_docs.fetchall()
            total_doctor_shift_cost = 0.0
            for doc_id, arrival, leave in doctor_shifts:
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                leave_dt = datetime.strptime(leave, "%Y-%m-%d %H:%M:%S")
                hours = calculate_hours(arrival_dt, leave_dt)
                cursor_docs.execute("SELECT name, hourly_rate FROM doctors WHERE id = ?", (doc_id,))
                rate_res = cursor_docs.fetchone()
                if rate_res:
                    doc_name, rate = rate_res
                    cost = hours * rate
                    total_doctor_shift_cost += cost
                    doctor_shift_details.append((arrival, leave, doc_name, hours, rate, cost))
            cursor_docs.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor_docs.execute("SELECT i.name, i.bonus_amount, di.date, d.name FROM doctor_interventions di JOIN interventions_db.interventions i ON di.intervention_id = i.id JOIN doctors d ON di.doctor_id = d.id WHERE di.patient_id = ?", (self.current_patient_id,))
            doc_interventions = cursor_docs.fetchall()
            total_doctor_intervention_cost = sum(i[1] for i in doc_interventions)
            doctor_intervention_details = [(date, name, doc_name, bonus) for name, bonus, date, doc_name in doc_interventions]
            total_doctor_cost = total_doctor_shift_cost + total_doctor_intervention_cost
            conn_docs.close()
        except sqlite3.Error as e:
            print(f"Error calculating doctor costs: {e}")

        # Calculate nurse costs
        total_nurse_cost = 0.0
        nurse_shift_details = []
        nurse_intervention_details = []
        try:
            conn_nurses = sqlite3.connect("db/nurses.db")
            cursor_nurses = conn_nurses.cursor()
            cursor_nurses.execute("SELECT nurse_id, arrival_datetime, leave_datetime FROM nurse_shifts WHERE patient_id = ?", (self.current_patient_id,))
            nurse_shifts = cursor_nurses.fetchall()
            total_nurse_shift_cost = 0.0
            for nurse_id, arrival, leave in nurse_shifts:
                arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M:%S")
                leave_dt = datetime.strptime(leave, "%Y-%m-%d %H:%M:%S")
                hours = calculate_hours(arrival_dt, leave_dt)
                cursor_nurses.execute("SELECT name, hourly_rate FROM nurses WHERE id = ?", (nurse_id,))
                rate_res = cursor_nurses.fetchone()
                if rate_res:
                    nurse_name, rate = rate_res
                    cost = hours * rate
                    total_nurse_shift_cost += cost
                    nurse_shift_details.append((arrival, leave, nurse_name, hours, rate, cost))
            cursor_nurses.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")
            cursor_nurses.execute("SELECT i.name, i.bonus_amount, ni.date, n.name FROM nurse_interventions ni JOIN interventions_db.interventions i ON ni.intervention_id = i.id JOIN nurses n ON ni.nurse_id = n.id WHERE ni.patient_id = ?", (self.current_patient_id,))
            nurse_interventions = cursor_nurses.fetchall()
            total_nurse_intervention_cost = sum(i[1] for i in nurse_interventions)
            nurse_intervention_details = [(date, name, nurse_name, bonus) for name, bonus, date, nurse_name in nurse_interventions]
            total_nurse_cost = total_nurse_shift_cost + total_nurse_intervention_cost
            conn_nurses.close()
        except sqlite3.Error as e:
            print(f"Error calculating nurse costs: {e}")

        # Calculate total cost
        total_cost = total_stay_cost + total_category_cost + total_doctor_cost + total_nurse_cost

        # Export to Excel
        import openpyxl
        filename = f"{name}_cost_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Cost Sheet"
            sheet.append(["Patient Cost Sheet"])
            sheet.append([])
            sheet.append(["Patient Name:", name])
            sheet.append(["Admission Date:", admission_date])
            sheet.append(["Discharge Date:", discharge_date or 'N/A'])
            sheet.append([])
            sheet.append(["Cost Breakdown:"])
            sheet.append([f"Stays ({len(stays)} days):", format_currency(total_stay_cost)])
            if stays:
                sheet.append(["  Date", "Care Level", "Cost"])
                for date, level, cost in stays:
                    sheet.append([f"  {date}", level, format_currency(cost)])
            sheet.append([])
            for category in categories:
                sheet.append([f"{category.capitalize()}:", format_currency(category_costs[category])])
                if category_details[category]:
                    sheet.append(["  Date", "Item", "Quantity", "Price", "Total"])
                    for item in category_details[category]:
                        date, item_name, qty, price, total = item
                        sheet.append([f"  {date}", item_name, qty, format_currency(price), format_currency(total)])
                sheet.append([])
            
            sheet.append(["Doctor Costs:", format_currency(total_doctor_cost)])
            if doctor_shift_details:
                sheet.append(["  Doctor Shifts"])
                sheet.append(["    Arrival", "Leave", "Doctor", "Hours", "Rate", "Cost"])
                for arrival, leave, doc_name, hours, rate, cost in doctor_shift_details:
                    sheet.append([f"    {arrival}", leave, doc_name, f"{hours:.2f}", format_currency(rate), format_currency(cost)])
            if doctor_intervention_details:
                sheet.append(["  Doctor Interventions"])
                sheet.append(["    Date", "Intervention", "Doctor", "Bonus"])
                for date, int_name, doc_name, bonus in doctor_intervention_details:
                    sheet.append([f"    {date}", int_name, doc_name, format_currency(bonus)])
            sheet.append([])

            sheet.append(["Nurse Costs:", format_currency(total_nurse_cost)])
            if nurse_shift_details:
                sheet.append(["  Nurse Shifts"])
                sheet.append(["    Arrival", "Leave", "Nurse", "Hours", "Rate", "Cost"])
                for arrival, leave, nurse_name, hours, rate, cost in nurse_shift_details:
                    sheet.append([f"    {arrival}", leave, nurse_name, f"{hours:.2f}", format_currency(rate), format_currency(cost)])
            if nurse_intervention_details:
                sheet.append(["  Nurse Interventions"])
                sheet.append(["    Date", "Intervention", "Nurse", "Bonus"])
                for date, int_name, nurse_name, bonus in nurse_intervention_details:
                    sheet.append([f"    {date}", int_name, nurse_name, format_currency(bonus)])
            sheet.append([])

            sheet.append(["Total Cost:", format_currency(total_cost)])

            workbook.save(filename)
            messagebox.showinfo("Export Success", f"Cost sheet exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export cost sheet: {e}")
            print(f"Export Error: Failed to export cost sheet: {e}")

    def _refresh_other_modules(self):
        """Refresh patient lists in other modules."""
        if self.doctor_module:
            self.doctor_module.load_patients()
        if self.nurse_module:
            self.nurse_module.load_patients()
