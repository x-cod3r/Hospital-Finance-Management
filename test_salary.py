import unittest
import sqlite3
from datetime import datetime
import os

from modules.utils import calculate_salary_details
from modules.company_module import CompanyModule

class TestSalary(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for testing
        self.db_path = "test_db.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create necessary tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hourly_rate REAL DEFAULT 100.0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER,
                arrival_datetime TIMESTAMP,
                leave_datetime TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER,
                date DATE NOT NULL,
                intervention_id INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nurses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                hourly_rate REAL DEFAULT 80.0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nurse_shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nurse_id INTEGER,
                arrival_datetime TIMESTAMP,
                leave_datetime TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nurse_interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nurse_id INTEGER,
                date DATE NOT NULL,
                intervention_id INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                bonus_amount REAL NOT NULL
            )
        ''')

        # Insert test data
        self.cursor.execute("INSERT INTO doctors (id, name, hourly_rate) VALUES (1, 'Dr. Test', 120.0)")
        self.cursor.execute("INSERT INTO doctor_shifts (doctor_id, arrival_datetime, leave_datetime) VALUES (1, '2023-10-01 08:00:00', '2023-10-01 16:00:00')")
        self.cursor.execute("INSERT INTO doctor_interventions (doctor_id, date, intervention_id) VALUES (1, '2023-10-01', 1)")

        self.cursor.execute("INSERT INTO nurses (id, name, level, hourly_rate) VALUES (1, 'Nurse Test', 'ICU', 90.0)")
        self.cursor.execute("INSERT INTO nurse_shifts (nurse_id, arrival_datetime, leave_datetime) VALUES (1, '2023-10-01 08:00:00', '2023-10-01 16:00:00')")
        self.cursor.execute("INSERT INTO nurse_interventions (nurse_id, date, intervention_id) VALUES (1, '2023-10-01', 1)")

        self.cursor.execute("INSERT INTO interventions (id, name, bonus_amount) VALUES (1, 'Test Intervention', 150.0)")

        self.conn.commit()

        # Create dummy db files for company module
        os.makedirs("db", exist_ok=True)
        sqlite3.connect("db/doctors.db").close()
        sqlite3.connect("db/nurses.db").close()


    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists("db/doctors.db"):
            os.remove("db/doctors.db")
        if os.path.exists("db/nurses.db"):
            os.remove("db/nurses.db")
        if os.path.exists("db/interventions.db"):
            os.remove("db/interventions.db")
        if os.path.exists("db"):
            os.rmdir("db")


    def test_calculate_salary_details(self):
        # Temporarily replace the original db path with the test db path
        original_db_path = "db/doctors.db"
        os.rename(original_db_path, original_db_path + ".bak")
        os.rename(self.db_path, original_db_path)

        salary_details = calculate_salary_details("doctor", 1, 10, 2023)
        self.assertIsNotNone(salary_details)
        self.assertEqual(salary_details['name'], "Dr. Test")
        self.assertEqual(salary_details['total_hours'], 8.0)
        self.assertEqual(salary_details['base_salary'], 960.0)
        self.assertEqual(salary_details['total_bonus'], 150.0)
        self.assertEqual(salary_details['total_salary'], 1110.0)

        # Restore the original db path
        os.rename(original_db_path, self.db_path)
        os.rename(original_db_path + ".bak", original_db_path)

    def test_company_module(self):
        # Temporarily replace the original db paths with the test db path
        original_doctors_db_path = "db/doctors.db"
        original_nurses_db_path = "db/nurses.db"
        os.rename(original_doctors_db_path, original_doctors_db_path + ".bak")
        os.rename(original_nurses_db_path, original_nurses_db_path + ".bak")
        os.rename(self.db_path, original_doctors_db_path)
        sqlite3.connect(original_nurses_db_path).close() # create empty nurses db

        company_module = CompanyModule(None, setup_ui=False)
        doctor_costs = company_module.calculate_doctor_costs('2023-10-01', '2023-10-31')
        self.assertEqual(doctor_costs['total'], 1110.0)

        # Restore the original db paths
        os.rename(original_doctors_db_path, self.db_path)
        os.rename(original_doctors_db_path + ".bak", original_doctors_db_path)
        os.rename(original_nurses_db_path + ".bak", original_nurses_db_path)

    def test_calculate_nurse_salary_details(self):
        # Temporarily replace the original db path with the test db path
        original_db_path = "db/nurses.db"
        os.rename(original_db_path, original_db_path + ".bak")
        os.rename(self.db_path, original_db_path)

        salary_details = calculate_salary_details("nurse", 1, 10, 2023)
        self.assertIsNotNone(salary_details)
        self.assertEqual(salary_details['name'], "Nurse Test")
        self.assertEqual(salary_details['total_hours'], 8.0)
        self.assertEqual(salary_details['base_salary'], 720.0)
        self.assertEqual(salary_details['total_bonus'], 150.0)
        self.assertEqual(salary_details['total_salary'], 870.0)

        # Restore the original db path
        os.rename(original_db_path, self.db_path)
        os.rename(original_db_path + ".bak", original_db_path)


if __name__ == '__main__':
    unittest.main()
