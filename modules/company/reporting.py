import sqlite3
from datetime import datetime

class ReportingHandler:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode

    def calculate_doctor_costs(self, from_date, to_date):
        """Calculate total doctor costs"""
        if self.debug_mode:
            print("\n--- Calculating Doctor Costs ---")
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

            if self.debug_mode:
                print(f"  Doctor: {name}")
                print(f"    - Total Hours: {total_hours:.2f} * ${hourly_rate}/hr = ${total_hours * hourly_rate:.2f}")
                print(f"    - Total Bonus: ${total_bonus:.2f}")
                print(f"    - Total Cost for {name}: ${doctor_cost:.2f}")

            if doctor_cost > 0:
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
        if self.debug_mode:
            print("\n--- Calculating Nurse Costs ---")
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

            if self.debug_mode:
                print(f"  Nurse: {name} ({level})")
                print(f"    - Total Hours: {total_hours:.2f} * ${hourly_rate}/hr = ${total_hours * hourly_rate:.2f}")
                print(f"    - Total Bonus: ${total_bonus:.2f}")
                print(f"    - Total Cost for {name}: ${nurse_cost:.2f}")

            if nurse_cost > 0:
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
        if self.debug_mode:
            print("\n--- Calculating Patient Revenues ---")
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
            
            # For the company, all item charges are pass-through costs
            patient_operational_cost = item_revenue
            total_operational_cost += patient_operational_cost

            if self.debug_mode and patient_total_revenue > 0:
                print(f"  Patient: {name}")
                print(f"    - Stay Revenue: ${stay_revenue:.2f}")
                print(f"    - Item Revenue (Pass-through cost): ${item_revenue:.2f}")
                print(f"    - Equipment Revenue: ${equipment_revenue:.2f}")
                print(f"    - Total Revenue from {name}: ${patient_total_revenue:.2f}")

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
