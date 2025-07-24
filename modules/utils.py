import sqlite3
import os
from datetime import datetime

def setup_database():
    """Setup all required databases"""
    # Create db directory if not exists
    os.makedirs("db", exist_ok=True)
    
    # Setup doctors database
    setup_doctors_db()
    
    # Setup nurses database
    setup_nurses_db()
    
    # Setup patients database
    setup_patients_db()
    
    # Setup interventions database
    setup_interventions_db()
    
    # Setup items database
    setup_items_db()

def setup_doctors_db():
    """Setup doctors database"""
    conn = sqlite3.connect("db/doctors.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hourly_rate REAL DEFAULT 100.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            arrival_datetime TIMESTAMP,
            leave_datetime TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            date DATE NOT NULL,
            intervention_id INTEGER,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            FOREIGN KEY (intervention_id) REFERENCES interventions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            month TEXT NOT NULL,
            year TEXT NOT NULL,
            total_hours REAL,
            total_bonus REAL,
            total_salary REAL,
            paid BOOLEAN DEFAULT 0,
            paid_date TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def setup_nurses_db():
    """Setup nurses database"""
    conn = sqlite3.connect("db/nurses.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nurses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL, -- 'ICU' or 'Medium_ICU'
            hourly_rate REAL DEFAULT 80.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nurse_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id INTEGER,
            arrival_datetime TIMESTAMP,
            leave_datetime TIMESTAMP,
            FOREIGN KEY (nurse_id) REFERENCES nurses (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nurse_interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id INTEGER,
            date DATE NOT NULL,
            intervention_id INTEGER,
            FOREIGN KEY (nurse_id) REFERENCES nurses (id),
            FOREIGN KEY (intervention_id) REFERENCES interventions (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nurse_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nurse_id INTEGER,
            month TEXT NOT NULL,
            year TEXT NOT NULL,
            total_hours REAL,
            total_bonus REAL,
            total_salary REAL,
            paid BOOLEAN DEFAULT 0,
            paid_date TIMESTAMP,
            FOREIGN KEY (nurse_id) REFERENCES nurses (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def setup_patients_db():
    """Setup patients database"""
    conn = sqlite3.connect("db/patients.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icu_type TEXT NOT NULL, -- 'ICU' or 'Medium_ICU'
            admission_date DATE NOT NULL,
            discharge_date DATE,
            package_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            package_type TEXT NOT NULL, -- 'default' or 'custom'
            items TEXT, -- JSON string of items
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_labs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date DATE NOT NULL,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date DATE NOT NULL,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_radiology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date DATE NOT NULL,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date DATE NOT NULL,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def setup_interventions_db():
    """Setup interventions database"""
    conn = sqlite3.connect("db/interventions.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bonus_amount REAL NOT NULL
        )
    ''')
    
    # Insert some default interventions if table is empty
    cursor.execute("SELECT COUNT(*) FROM interventions")
    count = cursor.fetchone()[0]
    
    if count == 0:
        default_interventions = [
            ("Central Line Insertion", 150.0),
            ("Intubation", 200.0),
            ("CPR", 100.0),
            ("Ventilator Management", 75.0),
            ("Wound Dressing", 50.0)
        ]
        
        cursor.executemany(
            "INSERT INTO interventions (name, bonus_amount) VALUES (?, ?)",
            default_interventions
        )
    
    conn.commit()
    conn.close()

def setup_items_db():
    """Setup items database"""
    conn = sqlite3.connect("db/items.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL, -- 'labs', 'drugs', 'radiology', 'consultations'
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icu_type TEXT NOT NULL, -- 'ICU' or 'Medium_ICU'
            daily_rate REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS package_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_id INTEGER,
            item_id INTEGER,
            FOREIGN KEY (package_id) REFERENCES packages (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    # Insert some default items if table is empty
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Default items
        default_items = [
            ("labs", "Complete Blood Count", 25.0),
            ("labs", "Liver Function Test", 30.0),
            ("labs", "Kidney Function Test", 35.0),
            ("drugs", "Antibiotics", 50.0),
            ("drugs", "Pain Killers", 20.0),
            ("drugs", "IV Fluids", 40.0),
            ("radiology", "X-Ray Chest", 100.0),
            ("radiology", "CT Scan", 500.0),
            ("radiology", "MRI", 800.0),
            ("consultations", "General Physician", 150.0),
            ("consultations", "Specialist", 300.0),
            ("consultations", "Surgeon", 400.0)
        ]
        
        cursor.executemany(
            "INSERT INTO items (category, name, price) VALUES (?, ?, ?)",
            default_items
        )
    
    # Insert default packages if table is empty
    cursor.execute("SELECT COUNT(*) FROM packages")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Default packages
        cursor.execute(
            "INSERT INTO packages (name, icu_type, daily_rate) VALUES (?, ?, ?)",
            ("Basic ICU Package", "ICU", 1500.0)
        )
        
        cursor.execute(
            "INSERT INTO packages (name, icu_type, daily_rate) VALUES (?, ?, ?)",
            ("Basic Medium ICU Package", "Medium_ICU", 1000.0)
        )
        
        # Get package IDs
        cursor.execute("SELECT id FROM packages WHERE icu_type = 'ICU'")
        icu_package_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM packages WHERE icu_type = 'Medium_ICU'")
        medium_icu_package_id = cursor.fetchone()[0]
        
        # Link items to packages
        # For ICU package, link first 6 items
        for i in range(1, 7):
            cursor.execute(
                "INSERT INTO package_items (package_id, item_id) VALUES (?, ?)",
                (icu_package_id, i)
            )
        
        # For Medium ICU package, link first 3 items
        for i in range(1, 4):
            cursor.execute(
                "INSERT INTO package_items (package_id, item_id) VALUES (?, ?)",
                (medium_icu_package_id, i)
            )
    
    conn.commit()
    conn.close()

def calculate_hours(arrival_datetime, leave_datetime):
    """Calculate hours worked between two datetime objects"""
    if not arrival_datetime or not leave_datetime:
        return 0.0
    
    try:
        # Calculate difference in hours
        diff = leave_datetime - arrival_datetime
        hours = diff.total_seconds() / 3600
        
        return round(hours, 2)
    except:
        return 0.0

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def calculate_salary_details(employee_type, employee_id, month, year):
    """Calculate salary details for a given employee"""
    db_name = f"db/{employee_type}s.db"
    interventions_db_name = "db/interventions.db"

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get employee info
    cursor.execute(f"SELECT name, hourly_rate FROM {employee_type}s WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()
    if not employee:
        conn.close()
        return None

    name, hourly_rate = employee

    # Calculate total hours
    cursor.execute(f"""
        SELECT arrival_datetime, leave_datetime FROM {employee_type}_shifts
        WHERE {employee_type}_id = ? AND
              strftime('%m', arrival_datetime) = ? AND
              strftime('%Y', arrival_datetime) = ?
    """, (employee_id, f"{month:02d}", str(year)))

    shifts = cursor.fetchall()
    total_hours = sum(calculate_hours(datetime.strptime(shift[0], "%Y-%m-%d %H:%M:%S"),
                                      datetime.strptime(shift[1], "%Y-%m-%d %H:%M:%S")) for shift in shifts)

    # Get intervention IDs
    cursor.execute(f"""
        SELECT intervention_id FROM {employee_type}_interventions
        WHERE {employee_type}_id = ? AND
              strftime('%m', date) = ? AND
              strftime('%Y', date) = ?
    """, (employee_id, f"{month:02d}", str(year)))
    intervention_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Calculate total bonus from interventions
    total_bonus = 0.0
    if intervention_ids:
        conn_interventions = sqlite3.connect(interventions_db_name)
        cursor_interventions = conn_interventions.cursor()

        placeholders = ','.join('?' for _ in intervention_ids)
        cursor_interventions.execute(f"""
            SELECT SUM(bonus_amount)
            FROM interventions
            WHERE id IN ({placeholders})
        """, intervention_ids)

        total_bonus_result = cursor_interventions.fetchone()[0]
        total_bonus = total_bonus_result if total_bonus_result else 0.0

        conn_interventions.close()

    # Calculate total salary
    base_salary = total_hours * hourly_rate
    total_salary = base_salary + total_bonus

    return {
        "name": name,
        "hourly_rate": hourly_rate,
        "total_hours": total_hours,
        "base_salary": base_salary,
        "total_bonus": total_bonus,
        "total_salary": total_salary,
    }

def export_to_pdf(filename, data):
    """Export data to a PDF file"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    text = c.beginText(40, height - 40)
    for line in data:
        text.textLine(line)

    c.drawText(text)
    c.save()