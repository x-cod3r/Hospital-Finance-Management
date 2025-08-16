from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.doctor.crud import DoctorCRUD
from modules.auth import AuthModule

doctors_bp = Blueprint('doctors', __name__, template_folder='../templates/doctors')

auth_module = AuthModule()

@doctors_bp.route('/doctors')
def list_doctors():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # This is a placeholder for the actual DoctorCRUD object
    # In a real application, you would have a better way of managing this
    class MockDoctorModule:
        def __init__(self):
            self.doctor_vars = {}
            self.scrollable_frame = None
            self.name_var = None
            self.rate_var = None
            self.current_doctor_id = None
            self.parent = None

    doctor_crud = DoctorCRUD(MockDoctorModule(), auth_module)
    doctors = doctor_crud.load_doctors()
    
    return render_template('list_doctors.html', doctors=doctors)

@doctors_bp.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        
        class MockDoctorModule:
            def __init__(self):
                self.parent = None

        doctor_crud = DoctorCRUD(MockDoctorModule(), auth_module)
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
    
    class MockDoctorModule:
        def __init__(self):
            self.parent = None

    doctor_crud = DoctorCRUD(MockDoctorModule(), auth_module)
    
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
    
    # This is a placeholder for the actual ShiftsHandler object
    # In a real application, you would have a better way of managing this
    class MockDoctorModule:
        def __init__(self):
            self.parent = None

    shifts_handler = ShiftsHandler(MockDoctorModule())
    shifts = shifts_handler.load_shifts(doctor_id)
    
    return render_template('shifts.html', shifts=shifts, doctor_id=doctor_id)

@doctors_bp.route('/doctors/<int:doctor_id>/interventions')
def view_interventions(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockDoctorModule:
        def __init__(self):
            self.parent = None

    interventions_handler = InterventionsHandler(MockDoctorModule())
    interventions = interventions_handler.load_interventions()
    
    return render_template('interventions.html', interventions=interventions, doctor_id=doctor_id)

@doctors_bp.route('/doctors/delete/<int:doctor_id>')
def delete_doctor(doctor_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockDoctorModule:
        def __init__(self):
            self.parent = None

    doctor_crud = DoctorCRUD(MockDoctorModule(), auth_module)
    if doctor_crud.delete_doctor(doctor_id):
        flash("Doctor deleted successfully")
    else:
        flash("Error deleting doctor")
    return redirect(url_for('doctors.list_doctors'))
