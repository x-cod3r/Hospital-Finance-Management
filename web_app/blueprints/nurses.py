from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os
from datetime import datetime

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.nurse.crud import NurseCRUD
from modules.nurse.shifts import ShiftsHandler
from modules.nurse.interventions import InterventionsHandler
from modules.nurse.salary import SalaryHandler
from modules.auth import AuthModule

nurses_bp = Blueprint('nurses', __name__, template_folder='../templates/nurses')

auth_module = AuthModule()

class WebNurseModule:
    def __init__(self):
        self.auth_module = auth_module
        self.parent = None

@nurses_bp.route('/nurses')
def list_nurses():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    nurse_crud = NurseCRUD(WebNurseModule(), auth_module)
    nurses = nurse_crud.load_nurses()
    
    return render_template('list_nurses.html', nurses=nurses)

@nurses_bp.route('/nurses/add', methods=['GET', 'POST'])
def add_nurse():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        rate = request.form['rate']
        
        nurse_crud = NurseCRUD(WebNurseModule(), auth_module)
        if nurse_crud.add_nurse(name, level, rate):
            flash(f"Nurse {name} added successfully")
        else:
            flash(f"Error adding nurse {name}")
        return redirect(url_for('nurses.list_nurses'))
        
    return render_template('add_nurse.html')

@nurses_bp.route('/nurses/edit/<int:nurse_id>', methods=['GET', 'POST'])
def edit_nurse(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    nurse_crud = NurseCRUD(WebNurseModule(), auth_module)
    
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        rate = request.form['rate']
        if nurse_crud.edit_nurse(nurse_id, name, level, rate):
            flash(f"Nurse {name} updated successfully")
        else:
            flash(f"Error updating nurse {name}")
        return redirect(url_for('nurses.list_nurses'))
        
    nurse = nurse_crud.get_nurse(nurse_id)
    return render_template('edit_nurse.html', nurse=nurse)

@nurses_bp.route('/nurses/<int:nurse_id>/shifts')
def view_shifts(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    shifts_handler = ShiftsHandler(WebNurseModule())
    shifts = shifts_handler.get_shifts_for_nurse(nurse_id)
    
    return render_template('shifts.html', shifts=shifts, nurse_id=nurse_id)

@nurses_bp.route('/nurses/<int:nurse_id>/shifts/add', methods=['POST'])
def add_shift(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    patient_id = request.form['patient_id']
    arrival_str = request.form['arrival_datetime']
    leave_str = request.form['leave_datetime']
    nurse_level_id = request.form['nurse_level_id']

    try:
        arrival_datetime = datetime.strptime(arrival_str, '%Y-%m-%dT%H:%M')
        leave_datetime = datetime.strptime(leave_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DDTHH:MM.")
        return redirect(url_for('nurses.view_shifts', nurse_id=nurse_id))

    shifts_handler = ShiftsHandler(WebNurseModule())
    if shifts_handler.add_shift(nurse_id, patient_id, arrival_datetime, leave_datetime, nurse_level_id):
        flash("Shift added successfully")
    else:
        flash("Error adding shift. Check for overlaps.")
    return redirect(url_for('nurses.view_shifts', nurse_id=nurse_id))

@nurses_bp.route('/nurses/shifts/delete/<int:shift_id>')
def delete_shift(shift_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    shifts_handler = ShiftsHandler(WebNurseModule())
    nurse_id = request.args.get('nurse_id') 
    if shifts_handler.remove_shift(shift_id):
        flash("Shift deleted successfully")
    else:
        flash("Error deleting shift")
    return redirect(url_for('nurses.view_shifts', nurse_id=nurse_id))

@nurses_bp.route('/nurses/<int:nurse_id>/interventions', methods=['GET', 'POST'])
def view_interventions(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    interventions_handler = InterventionsHandler(WebNurseModule())
    
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        date = request.form['date']
        intervention_id = request.form['intervention_id']
        
        if interventions_handler.add_intervention(nurse_id, patient_id, date, intervention_id):
            flash("Intervention added successfully")
        else:
            flash("Error adding intervention")
        return redirect(url_for('nurses.view_interventions', nurse_id=nurse_id))
        
    interventions = interventions_handler.load_interventions()
    # This is not ideal, but we need to get the patient list for the form
    from modules.patient.crud import PatientCRUD
    patients = PatientCRUD(None, auth_module).load_patients()
    
    return render_template('interventions.html', interventions=interventions, patients=patients, nurse_id=nurse_id)

@nurses_bp.route('/nurses/delete/<int:nurse_id>')
def delete_nurse(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    nurse_crud = NurseCRUD(WebNurseModule(), auth_module)
    if nurse_crud.delete_nurse(nurse_id):
        flash("Nurse deleted successfully")
    else:
        flash("Error deleting nurse")
    return redirect(url_for('nurses.list_nurses'))

@nurses_bp.route('/nurses/<int:nurse_id>/salary', methods=['GET', 'POST'])
def calculate_salary(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        salary_handler = SalaryHandler(WebNurseModule())
        salary_details = salary_handler.calculate_salary_details("nurse", nurse_id, start_date, end_date)
        
        return render_template('salary.html', salary_details=salary_details, nurse_id=nurse_id)
        
    return render_template('salary.html', nurse_id=nurse_id)
