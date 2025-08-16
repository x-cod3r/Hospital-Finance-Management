from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.patient.crud import PatientCRUD
from modules.auth import AuthModule

patients_bp = Blueprint('patients', __name__, template_folder='../templates/patients')

auth_module = AuthModule()

@patients_bp.route('/patients')
def list_patients():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.parent = None

    patient_crud = PatientCRUD(MockPatientModule(), auth_module)
    patients = patient_crud.load_patients()
    
    return render_template('list_patients.html', patients=patients)

@patients_bp.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        admission_date = request.form['admission_date']
        
        class MockPatientModule:
            def __init__(self):
                self.parent = None
            def _refresh_other_modules(self):
                pass

        patient_crud = PatientCRUD(MockPatientModule(), auth_module)
        if patient_crud.add_patient(name, admission_date):
            flash(f"Patient {name} added successfully")
        else:
            flash(f"Error adding patient {name}")
        return redirect(url_for('patients.list_patients'))
        
    return render_template('add_patient.html')

@patients_bp.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.parent = None
            self.name_var = None
            self.admission_date_var = None
            self.discharge_date_var = None
            def _refresh_other_modules(self):
                pass

    patient_crud = PatientCRUD(MockPatientModule(), auth_module)
    
    if request.method == 'POST':
        name = request.form['name']
        admission_date = request.form['admission_date']
        discharge_date = request.form['discharge_date']
        if patient_crud.edit_patient(patient_id, name, admission_date, discharge_date):
            flash(f"Patient {name} updated successfully")
        else:
            flash(f"Error updating patient {name}")
        return redirect(url_for('patients.list_patients'))
        
    patient = patient_crud.get_patient(patient_id)
    return render_template('edit_patient.html', patient=patient)

@patients_bp.route('/patients/<int:patient_id>/stays')
def view_stays(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.parent = None

    stays_handler = StaysHandler(MockPatientModule())
    stays = stays_handler.load_stays(patient_id)
    
    return render_template('stays.html', stays=stays, patient_id=patient_id)

@patients_bp.route('/patients/<int:patient_id>/items/<category>')
def view_items(patient_id, category):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.parent = None

    items_handler = ItemsHandler(MockPatientModule())
    items = items_handler.load_category_items(patient_id, category)
    
    return render_template('items.html', items=items, patient_id=patient_id, category=category)

@patients_bp.route('/patients/<int:patient_id>/equipment')
def view_equipment(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.parent = None

    equipment_handler = EquipmentHandler(MockPatientModule())
    equipment = equipment_handler.load_patient_equipment(patient_id)
    
    return render_template('equipment.html', equipment=equipment, patient_id=patient_id)

@patients_bp.route('/patients/delete/<int:patient_id>')
def delete_patient(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockPatientModule:
        def __init__(self):
            self.parent = None
            def _refresh_other_modules(self):
                pass
            def on_patient_select(self):
                pass

    patient_crud = PatientCRUD(MockPatientModule(), auth_module)
    if patient_crud.delete_patient(patient_id):
        flash("Patient deleted successfully")
    else:
        flash("Error deleting patient")
    return redirect(url_for('patients.list_patients'))
