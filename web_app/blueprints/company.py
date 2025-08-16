from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.company.reporting import ReportingHandler
from modules.auth import AuthModule

company_bp = Blueprint('company', __name__, template_folder='../templates/company')

auth_module = AuthModule()

@company_bp.route('/company', methods=['GET', 'POST'])
def report():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    report_data = None
    if request.method == 'POST':
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        
        reporting_handler = ReportingHandler(debug_mode=True)
        patient_revenues = reporting_handler.calculate_patient_revenues(from_date, to_date)
        doctor_costs = reporting_handler.calculate_doctor_costs(from_date, to_date)
        nurse_costs = reporting_handler.calculate_nurse_costs(from_date, to_date)
        
        total_patient_revenue = patient_revenues['total']
        pass_through_costs = patient_revenues['operational_cost']
        total_staff_cost = doctor_costs['total'] + nurse_costs['total']
        total_operational_cost = total_staff_cost + pass_through_costs
        net_profit = total_patient_revenue - total_operational_cost
        
        report_data = {
            "from_date": from_date,
            "to_date": to_date,
            "total_patient_revenue": total_patient_revenue,
            "total_staff_cost": total_staff_cost,
            "pass_through_costs": pass_through_costs,
            "total_operational_cost": total_operational_cost,
            "net_profit": net_profit,
            "doctor_details": doctor_costs['details'],
            "nurse_details": nurse_costs['details'],
            "patient_details": patient_revenues['details']
        }
        
    return render_template('report.html', report_data=report_data)
