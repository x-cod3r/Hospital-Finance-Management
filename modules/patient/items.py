import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from ..utils import format_currency, show_error_message

class ItemsHandler:
    def __init__(self, patient_module):
        self.patient_module = patient_module
        self.parent = patient_module.parent

    def setup_category_tab(self, parent, category):
        """Setup a generic category tab"""
        for widget in parent.winfo_children():
            widget.destroy()

        ttk.Label(parent, text=f"Add {category.capitalize()}:").pack(anchor=tk.W, pady=(10, 5))
        
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM items WHERE category = ? ORDER BY name", (category,))
        items = cursor.fetchall()
        conn.close()
        
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill=tk.X, pady=5)
        
        category_vars = getattr(self.patient_module, f"{category}_vars", {})
        category_vars['item'] = tk.StringVar()
        category_vars['date'] = tk.StringVar()
        category_vars['quantity'] = tk.StringVar()
        category_vars['items_list'] = items
        
        setattr(self.patient_module, f"{category}_vars", category_vars)
        
        item_combo = ttk.Combobox(item_frame, textvariable=category_vars['item'], state="readonly", width=30)
        category_vars['item_combo'] = item_combo
        item_combo.pack(side=tk.LEFT)
        
        item_names = [f"{item[1]} ({format_currency(item[2])})" for item in items]
        item_combo['values'] = item_names
        if item_names:
            item_combo.current(0)
        
        ttk.Label(item_frame, text="Date:").pack(side=tk.LEFT, padx=(10, 0))
        date_entry = ttk.Entry(item_frame, textvariable=category_vars['date'], width=12)
        date_entry.pack(side=tk.LEFT, padx=(5, 0))
        category_vars['date'].set(datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(item_frame, text="Qty:").pack(side=tk.LEFT, padx=(10, 0))
        qty_entry = ttk.Entry(item_frame, textvariable=category_vars['quantity'], width=5)
        qty_entry.pack(side=tk.LEFT, padx=(5, 0))
        category_vars['quantity'].set("1")
        
        def add_item():
            self.add_category_item(category)
        
        ttk.Button(item_frame, text="Add", command=add_item).pack(side=tk.LEFT, padx=(10, 0))

        def remove_item():
            self.remove_category_item(category)

        ttk.Button(item_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(parent, text=f"{category.capitalize()} Records:").pack(anchor=tk.W, pady=(10, 5))
        
        columns = ("ID", "Date", "Item", "Quantity", "Price", "Total")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        
        tree.heading("ID", text="ID")
        tree.column("ID", width=0, stretch=tk.NO)
        for col in columns[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        category_vars['tree'] = tree
        
        self.load_category_items(category)

    def load_category_items(self, category):
        """Load existing items for a category"""
        category_vars = getattr(self.patient_module, f"{category}_vars")
        if not hasattr(self.patient_module, 'current_patient_id'):
            return
        
        tree = category_vars['tree']
        for item in tree.get_children():
            tree.delete(item)
        
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")

        table_name = f"patient_{category}"
        cursor.execute(f"""
            SELECT p.id, p.date, i.name, p.quantity, i.price
            FROM {table_name} p
            JOIN items_db.items i ON p.item_id = i.id
            WHERE p.patient_id = ?
            ORDER BY p.date
        """, (self.patient_module.current_patient_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        for item in items:
            record_id, date, name, quantity, price = item
            total = quantity * price
            tree.insert("", "end", values=(record_id, date, name, quantity, format_currency(price), format_currency(total)))

    def add_category_item(self, category):
        """Add an item to a category for selected patients"""
        category_vars = getattr(self.patient_module, f"{category}_vars")
        selected_patients = self.patient_module.crud_handler.get_selected_patients()
        if not selected_patients:
            messagebox.showwarning("Warning", "Please select at least one patient")
            return
        
        item_text = category_vars['item'].get()
        if not item_text:
            show_error_message("Error", "Please select an item")
            return
        
        item_name = item_text.split(" (")[0]
        items_list = category_vars['items_list']
        item_id = None
        
        for item in items_list:
            if item[1] == item_name:
                item_id = item[0]
                break
        
        if not item_id:
            show_error_message("Error", "Invalid item selected")
            return
        
        date = category_vars['date'].get().strip()
        try:
            quantity = int(category_vars['quantity'].get())
        except ValueError:
            show_error_message("Error", "Please enter a valid quantity")
            return
        
        if not date:
            show_error_message("Error", "Please enter a date")
            return
        
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
            
            if len(selected_patients) == 1:
                self.load_category_items(category)
            
            if category_vars.get('items_list'):
                category_vars['item_combo'].current(0)
            else:
                category_vars['item'].set("")
            category_vars['quantity'].set("1")
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to add item: {e}")
        finally:
            conn.close()

    def remove_category_item(self, category):
        """Remove the selected item from a category"""
        category_vars = getattr(self.patient_module, f"{category}_vars")
        tree = category_vars.get('tree')
        if not tree:
            return

        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this item?")
        if not result:
            return

        item_values = tree.item(selected_item, 'values')
        record_id = item_values[0]

        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        table_name = f"patient_{category}"
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
            conn.commit()
            messagebox.showinfo("Success", "Item removed successfully")
            
            self.load_category_items(category)
        except sqlite3.Error as e:
            show_error_message("Error", f"Failed to remove item: {e}")
        finally:
            conn.close()
