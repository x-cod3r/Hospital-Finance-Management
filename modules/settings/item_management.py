import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ItemManagementHandler:
    def __init__(self, settings_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent

    def setup_item_tab(self, parent):
        """Setup item management tab"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        interventions_tab = ttk.Frame(notebook)
        notebook.add(interventions_tab, text="Interventions")
        self.setup_interventions_manager(interventions_tab)

        items_tab = ttk.Frame(notebook)
        notebook.add(items_tab, text="Labs, Drugs, etc.")
        self.setup_items_manager(items_tab)

    def setup_interventions_manager(self, parent):
        """Setup interventions management UI"""
        list_frame = ttk.LabelFrame(parent, text="Interventions", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.interventions_tree = ttk.Treeview(list_frame, columns=("Name", "Bonus"), show="headings")
        self.interventions_tree.heading("Name", text="Name")
        self.interventions_tree.heading("Bonus", text="Bonus")
        self.interventions_tree.pack(fill=tk.BOTH, expand=True)
        self.load_interventions()

        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=self.add_intervention).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=self.edit_intervention).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_intervention).pack(side=tk.LEFT)

    def setup_items_manager(self, parent):
        """Setup items management UI"""
        list_frame = ttk.LabelFrame(parent, text="Billable Items", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.items_tree = ttk.Treeview(list_frame, columns=("Category", "Name", "Price"), show="headings")
        self.items_tree.heading("Category", text="Category")
        self.items_tree.heading("Name", text="Name")
        self.items_tree.heading("Price", text="Price")
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        self.load_items()

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
            self.settings_module._refresh_other_modules()
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
            self.settings_module._refresh_other_modules()

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
            self.settings_module._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
