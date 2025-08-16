from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os
from datetime import datetime

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.doctor.crud import DoctorCRUD
from modules.doctor.shifts import ShiftsHandler
from modules.doctor.interventions import InterventionsHandler
from modules.doctor.salary import SalaryHandler
from modules.auth import AuthModule

doctors_bp = Blueprint('doctors', __name__, template_folder='../templates/doctors')

auth_module = AuthModule()

class WebDoctorModule:
    def __init__(self):
        self.auth_module = auth_module
        self.parent = None

@doctors_bp.route('/doctors')
def list_doctors():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    doctor_crud = DoctorCRUD(WebDoctorModule(), auth_module)
    doctors = doctor_crud.load_doctors()
    
    return render_template('list_doctors.html', doctors=doctors)

@doctors_bp.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        
        doctor_crud = DoctorCRUD(WebDoctorModule(), auth_module)
        if doctor_crud.add_doctor(name, rate):
            flash(f"Doctor {name} added successfully")
        else:
            flash(f"Error adding doctor {name}")
        return redirect(url_for('doctors.list_doctors'))
        
    return render_template('add_doctor.html')

@doctors_bp.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    doctor_crud = DoctorCRUD(WebDoctorModule(), auth_module)
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        if doctor_crud.edit_doctor(doctor_id, name, rate):
            flash(f"Doctor {name} updated successfully")
        else:
            flash(f"Error updating doctor {name}")
        return redirect(url_for('doctors.list_doctors'))
        
    doctor = doctor_crud.get_doctor(doctor_id)
    return render_template('edit_doctor.html', doctor=doctor)

@doctors_bp.route('/doctors/<int:doctor_id>/shifts')
def view_shifts(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    shifts_handler = ShiftsHandler(WebDoctorModule())
    shifts = shifts_handler.get_shifts_for_doctor(doctor_id)
    
    return render_template('shifts.html', shifts=shifts, doctor_id=doctor_id)

@doctors_bp.route('/doctors/<int:doctor_id>/shifts/add', methods=['POST'])
def add_shift(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    patient_id = request.form['patient_id']
    arrival_str = request.form['arrival_datetime']
    leave_str = request.form['leave_datetime']

    try:
        arrival_datetime = datetime.strptime(arrival_str, '%Y-%m-%dT%H:%M')
        leave_datetime = datetime.strptime(leave_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DDTHH:MM.")
        return redirect(url_for('doctors.view_shifts', doctor_id=doctor_id))

    shifts_handler = ShiftsHandler(WebDoctorModule())
    if shifts_handler.add_shift(doctor_id, patient_id, arrival_datetime, leave_datetime):
        flash("Shift added successfully")
    else:
        flash("Error adding shift. Check for overlaps.")
    return redirect(url_for('doctors.view_shifts', doctor_id=doctor_id))

@doctors_bp.route('/doctors/shifts/delete/<int:shift_id>')
def delete_shift(shift_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    shifts_handler = ShiftsHandler(WebDoctorModule())
    # We need the doctor_id to redirect back, this is a limitation of the current design
    # A better approach would be to store the doctor_id in the session or pass it as a query param
    doctor_id = request.args.get('doctor_id') 
    if shifts_handler.remove_shift(shift_id):
        flash("Shift deleted successfully")
    else:
        flash("Error deleting shift")
    return redirect(url_for('doctors.view_shifts', doctor_id=doctor_id))

@doctors_bp.route('/doctors/<int:doctor_id>/interventions', methods=['GET', 'POST'])
def view_interventions(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    interventions_handler = InterventionsHandler(WebDoctorModule())
    
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        date = request.form['date']
        intervention_id = request.form['intervention_id']
        
        if interventions_handler.add_intervention(doctor_id, patient_id, date, intervention_id):
            flash("Intervention added successfully")
        else:
            flash("Error adding intervention")
        return redirect(url_for('doctors.view_interventions', doctor_id=doctor_id))
        
    interventions = interventions_handler.load_interventions()
    # This is not ideal, but we need to get the patient list for the form
    from modules.patient.crud import PatientCRUD
    
    class WebPatientModule:
        def __init__(self):
            self.auth_module = auth_module
            self.parent = None

    patients = PatientCRUD(WebPatientModule(), auth_module).load_patients()
    
    return render_template('interventions.html', interventions=interventions, patients=patients, doctor_id=doctor_id)

@doctors_bp.route('/doctors/delete/<int:doctor_id>')
def delete_doctor(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    doctor_crud = DoctorCRUD(WebDoctorModule(), auth_module)
    if doctor_crud.delete_doctor(doctor_id):
        flash("Doctor deleted successfully")
    else:
        flash("Error deleting doctor")
    return redirect(url_for('doctors.list_doctors'))

@doctors_bp.route('/doctors/<int:doctor_id>/salary', methods=['GET', 'POST'])
def calculate_salary(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        salary_handler = SalaryHandler(WebDoctorModule())
        salary_details = salary_handler.calculate_salary_details("doctor", doctor_id, start_date, end_date)
        
        return render_template('salary.html', salary_details=salary_details, doctor_id=doctor_id)
        
    return render_template('salary.html', doctor_id=doctor_id)
