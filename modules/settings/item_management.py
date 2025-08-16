import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ..utils import show_error_message

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

        items_notebook = ttk.Notebook(notebook)
        notebook.add(items_notebook, text="Billable Items")

        self.categories = ["labs", "drugs", "radiology", "consultations"]
        self.item_trees = {}

        for category in self.categories:
            tab = ttk.Frame(items_notebook)
            items_notebook.add(tab, text=category.capitalize())
            self.setup_category_manager(tab, category)

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

    def setup_category_manager(self, parent, category):
        """Setup UI for a specific item category"""
        list_frame = ttk.LabelFrame(parent, text=f"{category.capitalize()} Items", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(list_frame, columns=("Name", "Price"), show="headings")
        tree.heading("Name", text="Name")
        tree.heading("Price", text="Price")
        tree.pack(fill=tk.BOTH, expand=True)
        self.item_trees[category] = tree
        self.load_items(category)

        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons_frame, text="Add", command=lambda c=category: self.add_item(c)).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Edit", command=lambda c=category: self.edit_item(c)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=lambda c=category: self.delete_item(c)).pack(side=tk.LEFT)

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
            item = self.interventions_tree.item(selected_item)
            name, _ = item['values']
            conn = sqlite3.connect("db/interventions.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interventions WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "DELETE_INTERVENTION", f"Deleted intervention: {name}")
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
                show_error_message("Error", "All fields are required.")
                return

            try:
                new_bonus = float(new_bonus)
            except ValueError:
                show_error_message("Error", "Bonus must be a number.")
                return

            conn = sqlite3.connect("db/interventions.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE interventions SET name = ?, bonus_amount = ? WHERE id = ?", (new_name, new_bonus, item_id))
                self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "UPDATE_INTERVENTION", f"Updated intervention: {new_name}")
            else:
                cursor.execute("INSERT INTO interventions (name, bonus_amount) VALUES (?, ?)", (new_name, new_bonus))
                self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "CREATE_INTERVENTION", f"Created intervention: {new_name}")
            conn.commit()
            conn.close()
            self.load_interventions()
            self.settings_module._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def load_items(self, category=None):
        """Load items for a specific category or all categories"""
        if category:
            categories_to_load = [category]
        else:
            categories_to_load = self.categories

        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()

        for cat in categories_to_load:
            tree = self.item_trees.get(cat)
            if not tree:
                continue
            
            for i in tree.get_children():
                tree.delete(i)
            
            cursor.execute("SELECT id, name, price FROM items WHERE category = ? ORDER BY name", (cat,))
            for row in cursor.fetchall():
                tree.insert("", "end", values=(row[1], f"{row[2]:.2f}"), iid=row[0])
        
        conn.close()

    def add_item(self, category):
        """Show dialog to add a new item"""
        self.item_dialog("Add Item", category=category)

    def edit_item(self, category):
        """Show dialog to edit the selected item"""
        tree = self.item_trees[category]
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        item = tree.item(selected_item)
        name, price = item['values']
        self.item_dialog("Edit Item", item_id=selected_item, category=category, name=name, price=price)

    def delete_item(self, category):
        """Delete the selected item"""
        tree = self.item_trees[category]
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            item = tree.item(selected_item)
            name, _ = item['values']
            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (selected_item,))
            conn.commit()
            conn.close()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"DELETE_ITEM", f"Deleted item: {name} from {category}")
            self.load_items(category)
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
        category_entry = ttk.Entry(dialog, textvariable=category_var, state="readonly")
        category_entry.pack(fill=tk.X, padx=10)

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
                show_error_message("Error", "All fields are required.")
                return

            try:
                new_price = float(new_price)
            except ValueError:
                show_error_message("Error", "Price must be a number.")
                return

            conn = sqlite3.connect("db/items.db")
            cursor = conn.cursor()
            if item_id:
                cursor.execute("UPDATE items SET category = ?, name = ?, price = ? WHERE id = ?", (new_category, new_name, new_price, item_id))
                self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"UPDATE_ITEM", f"Updated item: {new_name} in {new_category}")
            else:
                cursor.execute("INSERT INTO items (category, name, price) VALUES (?, ?, ?)", (new_category, new_name, new_price))
                self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"CREATE_ITEM", f"Created item: {new_name} in {new_category}")
            conn.commit()
            conn.close()
            self.load_items(new_category)
            self.settings_module._refresh_other_modules()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
