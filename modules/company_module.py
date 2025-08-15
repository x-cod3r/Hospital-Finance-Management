import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from .utils import format_currency

class CompanyModule:
    def __init__(self, parent, setup_ui=True):
        self.parent = parent
        if setup_ui:
            self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Report parameters
        params_frame = ttk.LabelFrame(main_frame, text="Report Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date range
        ttk.Label(params_frame, text="From Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.from_date_var = tk.StringVar()
        self.from_date_var.set((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(params_frame, textvariable=self.from_date_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 10))
        
        ttk.Label(params_frame, text="To Date:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.to_date_var = tk.StringVar()
        self.to_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(params_frame, textvariable=self.to_date_var).grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2, padx=(5, 10))
        
        # Report type
        ttk.Label(params_frame, text="Report Type:").grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
        self.report_type_var = tk.StringVar()
        report_type_combo = ttk.Combobox(params_frame, textvariable=self.report_type_var, state="readonly")
        report_type_combo['values'] = ["Daily", "Weekly", "Monthly", "Custom Range"]
        report_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 2), padx=(5, 10))
        report_type_combo.set("Monthly")
        
        # Generate button
        ttk.Button(params_frame, text="Generate Report", command=self.generate_report).grid(row=1, column=3, sticky=tk.E, pady=(10, 2))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Report Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Export button
        ttk.Button(results_frame, text="Export Report", command=self.export_report).pack(pady=(10, 0))
        
        # Configure grid weights
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def generate_report(self):
        """Generate company report"""
        print("Generating report...")
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            report_type = self.report_type_var.get()
            
            print(f"Report parameters: from={from_date}, to={to_date}, type={report_type}")

            # Validate dates
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates (YYYY-MM-DD)")
            print("Error: Please enter valid dates (YYYY-MM-DD)")
            return
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Generate report header
        report_header = f"""
ICU MANAGEMENT SYSTEM - COMPANY REPORT
Report Period: {from_date} to {to_date}
Report Type: {report_type}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

""" + "="*80 + "\n\n"
        
        self.results_text.insert(tk.END, report_header)
        
        # Get patient revenues and pass-through costs
        patient_revenues = self.calculate_patient_revenues(from_date, to_date)
        total_patient_revenue = patient_revenues['total']
        pass_through_costs = patient_revenues['operational_cost']

        # Get staff costs
        doctor_costs = self.calculate_doctor_costs(from_date, to_date)
        nurse_costs = self.calculate_nurse_costs(from_date, to_date)
        total_staff_cost = doctor_costs['total'] + nurse_costs['total']

        # Calculate total operational costs
        total_operational_cost = total_staff_cost + pass_through_costs
        
        # Calculate net profit
        net_profit = total_patient_revenue - total_operational_cost

        # Display summary
        summary_text = f"""
FINANCIAL SUMMARY
=================
Total Patient Revenue: {format_currency(total_patient_revenue)}

Operational Costs:
  - Staff Costs: {format_currency(total_staff_cost)}
  - Pass-Through Costs (Labs, Drugs, etc.): {format_currency(pass_through_costs)}
-----------------
Total Operational Costs: {format_currency(total_operational_cost)}

Net Profit/Loss: {format_currency(net_profit)}

"""
        
        self.results_text.insert(tk.END, summary_text)
        
        # Display doctor details
        self.results_text.insert(tk.END, "\nDOCTORS\n" + "-"*40 + "\n")
        for doctor in doctor_costs['details']:
            self.results_text.insert(tk.END, f"{doctor['name']}: {format_currency(doctor['cost'])}\n")
        
        # Display nurse details
        self.results_text.insert(tk.END, "\nNURSES\n" + "-"*40 + "\n")
        for nurse in nurse_costs['details']:
            self.results_text.insert(tk.END, f"{nurse['name']} ({nurse['level']}): {format_currency(nurse['cost'])}\n")
        
        # Display patient details
        self.results_text.insert(tk.END, "\nPATIENTS\n" + "-"*40 + "\n")
        for patient in patient_revenues['details']:
            self.results_text.insert(tk.END, f"{patient['name']}: {format_currency(patient['revenue'])}\n")
    
    def calculate_doctor_costs(self, from_date, to_date):
        """Calculate total doctor costs"""
        conn = sqlite3.connect("db/doctors.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")

        # Get all doctors
        cursor.execute("SELECT id, name, hourly_rate FROM doctors")
        doctors = cursor.fetchall()

        total_cost = 0.0
        doctor_details = []

        for doctor in doctors:
            doctor_id, name, hourly_rate = doctor

            # Calculate total hours
            cursor.execute("""
                SELECT arrival_datetime, leave_datetime FROM doctor_shifts
                WHERE doctor_id = ? AND
                      date(arrival_datetime) BETWEEN ? AND ?
            """, (doctor_id, from_date, to_date))

            shifts = cursor.fetchall()
            total_hours = 0.0
            for shift in shifts:
                arrival_datetime = datetime.strptime(shift[0], "%Y-%m-%d %H:%M:%S")
                leave_datetime = datetime.strptime(shift[1], "%Y-%m-%d %H:%M:%S")
                total_hours += (leave_datetime - arrival_datetime).total_seconds() / 3600

            # Calculate total bonus
            cursor.execute("""
                SELECT SUM(i.bonus_amount)
                FROM doctor_interventions di
                JOIN interventions_db.interventions i ON di.intervention_id = i.id
                WHERE di.doctor_id = ? AND di.date BETWEEN ? AND ?
            """, (doctor_id, from_date, to_date))

            bonus_result = cursor.fetchone()[0]
            total_bonus = bonus_result if bonus_result else 0.0

            # Calculate total cost
            doctor_cost = (total_hours * hourly_rate) + total_bonus
            total_cost += doctor_cost

            doctor_details.append({
                'name': name,
                'cost': doctor_cost
            })

        conn.close()

        return {
            'total': total_cost,
            'details': doctor_details
        }
    
    def calculate_nurse_costs(self, from_date, to_date):
        """Calculate total nurse costs"""
        conn = sqlite3.connect("db/nurses.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/interventions.db' AS interventions_db")

        # Get all nurses
        cursor.execute("SELECT id, name, level, hourly_rate FROM nurses")
        nurses = cursor.fetchall()

        total_cost = 0.0
        nurse_details = []

        for nurse in nurses:
            nurse_id, name, level, hourly_rate = nurse

            # Calculate total hours
            cursor.execute("""
                SELECT arrival_datetime, leave_datetime FROM nurse_shifts
                WHERE nurse_id = ? AND
                      date(arrival_datetime) BETWEEN ? AND ?
            """, (nurse_id, from_date, to_date))

            shifts = cursor.fetchall()
            total_hours = 0.0
            for shift in shifts:
                arrival_datetime = datetime.strptime(shift[0], "%Y-%m-%d %H:%M:%S")
                leave_datetime = datetime.strptime(shift[1], "%Y-%m-%d %H:%M:%S")
                total_hours += (leave_datetime - arrival_datetime).total_seconds() / 3600

            # Calculate total bonus
            cursor.execute("""
                SELECT SUM(i.bonus_amount)
                FROM nurse_interventions ni
                JOIN interventions_db.interventions i ON ni.intervention_id = i.id
                WHERE ni.nurse_id = ? AND ni.date BETWEEN ? AND ?
            """, (nurse_id, from_date, to_date))

            bonus_result = cursor.fetchone()[0]
            total_bonus = bonus_result if bonus_result else 0.0

            # Calculate total cost
            nurse_cost = (total_hours * hourly_rate) + total_bonus
            total_cost += nurse_cost

            nurse_details.append({
                'name': name,
                'level': level,
                'cost': nurse_cost
            })

        conn.close()

        return {
            'total': total_cost,
            'details': nurse_details
        }
    
    def calculate_patient_revenues(self, from_date, to_date):
        """Calculate total patient revenues and operational costs from patient services."""
        conn = sqlite3.connect("db/patients.db")
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'db/items.db' AS items_db")

        cursor.execute("SELECT id, name FROM patients")
        patients = cursor.fetchall()

        total_revenue = 0.0
        total_operational_cost = 0.0
        patient_details = []

        for patient_id, name in patients:
            # Stay costs
            cursor.execute("""
                SELECT SUM(cl.daily_rate) FROM patient_stays ps
                JOIN items_db.care_levels cl ON ps.care_level_id = cl.id
                WHERE ps.patient_id = ? AND ps.stay_date BETWEEN ? AND ?
            """, (patient_id, from_date, to_date))
            stay_revenue = cursor.fetchone()[0] or 0.0

            # Item costs (labs, drugs, etc.)
            item_revenue = 0.0
            for category in ["labs", "drugs", "radiology", "consultations"]:
                cursor.execute(f"""
                    SELECT SUM(i.price * p.quantity) FROM patient_{category} p
                    JOIN items_db.items i ON p.item_id = i.id
                    WHERE p.patient_id = ? AND p.date BETWEEN ? AND ?
                """, (patient_id, from_date, to_date))
                item_revenue += cursor.fetchone()[0] or 0.0

            # Equipment costs
            equipment_revenue = 0.0
            cursor.execute("""
                SELECT start_date, end_date, daily_rental_price FROM patient_equipment
                WHERE patient_id = ?
            """, (patient_id,))
            for start_date, end_date, daily_price in cursor.fetchall():
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.strptime(to_date, "%Y-%m-%d")
                
                period_start = datetime.strptime(from_date, "%Y-%m-%d")
                period_end = datetime.strptime(to_date, "%Y-%m-%d")

                overlap_start = max(start, period_start)
                overlap_end = min(end, period_end)

                if overlap_start <= overlap_end:
                    days = (overlap_end - overlap_start).days + 1
                    equipment_revenue += days * daily_price

            patient_total_revenue = stay_revenue + item_revenue + equipment_revenue
            total_revenue += patient_total_revenue
            
            # For the company, all item and equipment charges are pass-through costs
            patient_operational_cost = item_revenue + equipment_revenue
            total_operational_cost += patient_operational_cost

            if patient_total_revenue > 0:
                patient_details.append({
                    'name': name,
                    'revenue': patient_total_revenue
                })

        conn.close()

        return {
            'total': total_revenue,
            'details': patient_details,
            'operational_cost': total_operational_cost
        }
    
    def export_report(self):
        """Export report to file"""
        report_content = self.results_text.get(1.0, tk.END)
        if not report_content.strip():
            messagebox.showwarning("Warning", "Please generate a report first")
            return

        import openpyxl
        from datetime import datetime as dt
        filename = f"company_report_{dt.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Company Report"

            for line in report_content.split('\n'):
                sheet.append([line])

            workbook.save(filename)
            messagebox.showinfo("Export Success", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
            print(f"Export Error: Failed to export report: {e}")
