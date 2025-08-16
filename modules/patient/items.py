import tkinter as tk
from tkinter import ttk, messagebox
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

    def load_category_items(self, patient_id, category):
        """Load existing items for a category for a specific patient"""
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
        """, (patient_id,))
        
        items = cursor.fetchall()
        conn.close()
        return items

    def add_category_item(self, patient_id, category, item_id, date, quantity):
        """Add an item to a category for a specific patient"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        
        table_name = f"patient_{category}"
        try:
            cursor.execute(f"""
                INSERT INTO {table_name} (patient_id, date, item_id, quantity)
                VALUES (?, ?, ?, ?)
            """, (patient_id, date, item_id, quantity))
            conn.commit()
            
            cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
            cursor.execute("SELECT name FROM items_db.items WHERE id = ?", (item_id,))
            item_name = cursor.fetchone()[0]
            self.patient_module.auth_module.log_action(self.patient_module.auth_module.current_user, f"ADD_{category.upper()}", f"Added {item_name} (x{quantity}) for patient ID {patient_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return False
        finally:
            conn.close()

    def remove_category_item(self, category, record_id):
        """Remove an item from a category"""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        table_name = f"patient_{category}"
        try:
            cursor.execute(f"SELECT patient_id, item_id, quantity FROM {table_name} WHERE id = ?", (record_id,))
            patient_id, item_id, quantity = cursor.fetchone()
            
            cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")
            cursor.execute("SELECT name FROM items_db.items WHERE id = ?", (item_id,))
            item_name = cursor.fetchone()[0]
            
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
            conn.commit()
            self.patient_module.auth_module.log_action(self.patient_module.auth_module.current_user, f"REMOVE_{category.upper()}", f"Removed {item_name} (x{quantity}) for patient ID {patient_id}")
            return True
        except sqlite3.Error as e:
            print(f"Error removing item: {e}")
            return False
        finally:
            conn.close()
