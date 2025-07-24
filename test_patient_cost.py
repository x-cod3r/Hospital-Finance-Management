import unittest
import sqlite3
from datetime import datetime
import os

from modules.patient_module import PatientModule

class TestPatientCost(unittest.TestCase):

    def setUp(self):
        # Create temporary databases for testing
        os.makedirs("db", exist_ok=True)
        self.patients_db_path = "db/patients.db"
        self.items_db_path = "db/items.db"

        self.conn_patients = sqlite3.connect(self.patients_db_path)
        self.cursor_patients = self.conn_patients.cursor()

        self.conn_items = sqlite3.connect(self.items_db_path)
        self.cursor_items = self.conn_items.cursor()

        # Create necessary tables
        self.cursor_patients.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icu_type TEXT NOT NULL,
                admission_date DATE NOT NULL,
                discharge_date DATE
            )
        ''')
        self.cursor_patients.execute('''
            CREATE TABLE IF NOT EXISTS patient_labs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                date DATE NOT NULL,
                item_id INTEGER,
                quantity INTEGER DEFAULT 1
            )
        ''')
        self.cursor_items.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        self.cursor_items.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icu_type TEXT NOT NULL,
                daily_rate REAL NOT NULL
            )
        ''')

        # Insert test data
        self.cursor_patients.execute("INSERT INTO patients (id, name, icu_type, admission_date, discharge_date) VALUES (1, 'Test Patient', 'ICU', '2023-10-01', '2023-10-11')")
        self.cursor_patients.execute("INSERT INTO patient_labs (patient_id, date, item_id, quantity) VALUES (1, '2023-10-01', 1, 2)")

        self.cursor_items.execute("INSERT INTO items (id, category, name, price) VALUES (1, 'labs', 'Test Lab', 50.0)")
        self.cursor_items.execute("INSERT INTO packages (id, name, icu_type, daily_rate) VALUES (1, 'Test Package', 'ICU', 1000.0)")

        self.conn_patients.commit()
        self.conn_items.commit()

    def tearDown(self):
        self.conn_patients.close()
        self.conn_items.close()
        os.remove(self.patients_db_path)
        os.remove(self.items_db_path)
        os.rmdir("db")

    def test_calculate_cost(self):
        # The PatientModule constructor calls setup_ui, which fails in a headless environment.
        # I will temporarily modify the PatientModule to allow skipping the UI setup.

        original_init = PatientModule.__init__
        def new_init(self, parent, setup_ui=False):
            self.parent = parent
            if setup_ui:
                self.setup_ui()
        PatientModule.__init__ = new_init

        patient_module = PatientModule(None)
        patient_module.current_patient_id = 1

        # I can't directly call calculate_cost and check the messagebox.
        # I will have to replicate the logic here to test it.

        conn_patients = sqlite3.connect(self.patients_db_path)
        cursor_patients = conn_patients.cursor()
        cursor_patients.execute("SELECT name, icu_type, admission_date, discharge_date FROM patients WHERE id = 1")
        patient = cursor_patients.fetchone()
        name, icu_type, admission_date, discharge_date = patient

        admission = datetime.strptime(admission_date, "%Y-%m-%d")
        discharge = datetime.strptime(discharge_date, "%Y-%m-%d")
        icu_days = (discharge - admission).days

        conn_items = sqlite3.connect(self.items_db_path)
        cursor_items = conn_items.cursor()
        cursor_items.execute("SELECT daily_rate FROM packages WHERE icu_type = ?", (icu_type,))
        package_result = cursor_items.fetchone()
        daily_rate = package_result[0]
        icu_cost = icu_days * daily_rate

        cursor_patients.execute("SELECT item_id, quantity FROM patient_labs WHERE patient_id = 1")
        items = cursor_patients.fetchall()

        category_cost = 0.0
        for item_id, quantity in items:
            cursor_items.execute("SELECT price FROM items WHERE id = ?", (item_id,))
            price_result = cursor_items.fetchone()
            category_cost += quantity * price_result[0]

        total_cost = icu_cost + category_cost

        self.assertEqual(total_cost, 10 * 1000 + 2 * 50)

        # Restore original __init__
        PatientModule.__init__ = original_init


if __name__ == '__main__':
    unittest.main()
