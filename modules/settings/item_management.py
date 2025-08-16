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
        """Load interventions from the database"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions ORDER BY name")
        interventions = cursor.fetchall()
        conn.close()
        return interventions

    def add_intervention(self, name, bonus):
        """Add a new intervention"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO interventions (name, bonus_amount) VALUES (?, ?)", (name, bonus))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "CREATE_INTERVENTION", f"Created intervention: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding intervention: {e}")
            return False
        finally:
            conn.close()

    def get_intervention(self, intervention_id):
        """Get a single intervention by ID"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, bonus_amount FROM interventions WHERE id = ?", (intervention_id,))
        intervention = cursor.fetchone()
        conn.close()
        return intervention

    def edit_intervention(self, intervention_id, name, bonus):
        """Edit an intervention"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE interventions SET name = ?, bonus_amount = ? WHERE id = ?", (name, bonus, intervention_id))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "UPDATE_INTERVENTION", f"Updated intervention: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating intervention: {e}")
            return False
        finally:
            conn.close()

    def delete_intervention(self, intervention_id):
        """Delete an intervention"""
        conn = sqlite3.connect("db/interventions.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM interventions WHERE id = ?", (intervention_id,))
            name = cursor.fetchone()[0]
            cursor.execute("DELETE FROM interventions WHERE id = ?", (intervention_id,))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, "DELETE_INTERVENTION", f"Deleted intervention: {name}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting intervention: {e}")
            return False
        finally:
            conn.close()

    def load_items(self, category):
        """Load items for a specific category from the database"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM items WHERE category = ? ORDER BY name", (category,))
        items = cursor.fetchall()
        conn.close()
        return items

    def add_item(self, category, name, price):
        """Add a new item"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO items (category, name, price) VALUES (?, ?, ?)", (category, name, price))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"CREATE_ITEM", f"Created item: {name} in {category}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return False
        finally:
            conn.close()

    def get_item(self, item_id):
        """Get a single item by ID"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        conn.close()
        return item

    def edit_item(self, item_id, category, name, price):
        """Edit an item"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE items SET category = ?, name = ?, price = ? WHERE id = ?", (category, name, price, item_id))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"UPDATE_ITEM", f"Updated item: {name} in {category}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating item: {e}")
            return False
        finally:
            conn.close()

    def delete_item(self, item_id):
        """Delete an item"""
        conn = sqlite3.connect("db/items.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name, category FROM items WHERE id = ?", (item_id,))
            name, category = cursor.fetchone()
            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            conn.commit()
            self.settings_module.auth_module.log_action(self.settings_module.auth_module.current_user, f"DELETE_ITEM", f"Deleted item: {name} from {category}")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            return False
        finally:
            conn.close()
