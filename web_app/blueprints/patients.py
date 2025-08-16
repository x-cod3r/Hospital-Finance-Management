from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.patient.crud import PatientCRUD
from modules.patient.stays import StaysHandler
from modules.patient.items import ItemsHandler
from modules.patient.equipment import EquipmentHandler
from modules.patient.costing import CostingHandler
from modules.auth import AuthModule

patients_bp = Blueprint('patients', __name__, template_folder='../templates/patients')

auth_module = AuthModule()

class WebPatientModule:
    def __init__(self):
        self.auth_module = auth_module
        self.parent = None
    def _refresh_other_modules(self):
        pass

@patients_bp.route('/patients')
def list_patients():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    patient_crud = PatientCRUD(WebPatientModule(), auth_module)
    patients = patient_crud.load_patients()
    
    return render_template('list_patients.html', patients=patients)

@patients_bp.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        admission_date = request.form['admission_date']
        
        patient_crud = PatientCRUD(WebPatientModule(), auth_module)
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
    
    patient_crud = PatientCRUD(WebPatientModule(), auth_module)
    
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

@patients_bp.route('/patients/<int:patient_id>/stays', methods=['GET', 'POST'])
def view_stays(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    stays_handler = StaysHandler(WebPatientModule())
    
    if request.method == 'POST':
        stay_date = request.form['stay_date']
        care_level_id = request.form['care_level_id']
        if stays_handler.add_stay(patient_id, stay_date, care_level_id):
            flash("Stay added successfully")
        else:
            flash("Error adding stay")
        return redirect(url_for('patients.view_stays', patient_id=patient_id))
        
    stays = stays_handler.load_stays(patient_id)
    care_levels = stays_handler.load_care_levels()
    
    return render_template('stays.html', stays=stays, care_levels=care_levels, patient_id=patient_id)

@patients_bp.route('/patients/stays/delete/<int:stay_id>')
def delete_stay(stay_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    stays_handler = StaysHandler(WebPatientModule())
    patient_id = request.args.get('patient_id') 
    if stays_handler.remove_stay(stay_id):
        flash("Stay deleted successfully")
    else:
        flash("Error deleting stay")
    return redirect(url_for('patients.view_stays', patient_id=patient_id))

@patients_bp.route('/patients/<int:patient_id>/items/<category>', methods=['GET', 'POST'])
def view_items(patient_id, category):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    items_handler = ItemsHandler(WebPatientModule())
    
    if request.method == 'POST':
        item_id = request.form['item_id']
        date = request.form['date']
        quantity = request.form['quantity']
        if items_handler.add_category_item(patient_id, category, item_id, date, quantity):
            flash("Item added successfully")
        else:
            flash("Error adding item")
        return redirect(url_for('patients.view_items', patient_id=patient_id, category=category))
        
    items = items_handler.load_category_items(patient_id, category)
    
    # This is not ideal, but we need to get the item list for the form
    from modules.settings.item_management import ItemManagementHandler
    all_items = ItemManagementHandler(None).get_items_by_category(category)
    
    return render_template('items.html', items=items, all_items=all_items, patient_id=patient_id, category=category)

@patients_bp.route('/patients/items/delete/<category>/<int:record_id>')
def delete_item(category, record_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    items_handler = ItemsHandler(WebPatientModule())
    patient_id = request.args.get('patient_id') 
    if items_handler.remove_category_item(category, record_id):
        flash("Item deleted successfully")
    else:
        flash("Error deleting item")
    return redirect(url_for('patients.view_items', patient_id=patient_id, category=category))

@patients_bp.route('/patients/<int:patient_id>/equipment', methods=['GET', 'POST'])
def view_equipment(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    equipment_handler = EquipmentHandler(WebPatientModule())
    
    if request.method == 'POST':
        equipment_id = request.form['equipment_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        daily_price = request.form['daily_price']
        if equipment_handler.add_equipment(patient_id, equipment_id, start_date, end_date, daily_price):
            flash("Equipment added successfully")
        else:
            flash("Error adding equipment")
        return redirect(url_for('patients.view_equipment', patient_id=patient_id))
        
    equipment = equipment_handler.load_patient_equipment(patient_id)
    all_equipment = equipment_handler.load_equipment()
    
    return render_template('equipment.html', equipment=equipment, all_equipment=all_equipment, patient_id=patient_id)

@patients_bp.route('/patients/equipment/delete/<int:record_id>')
def delete_equipment(record_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    equipment_handler = EquipmentHandler(WebPatientModule())
    patient_id = request.args.get('patient_id') 
    if equipment_handler.remove_equipment(record_id):
        flash("Equipment deleted successfully")
    else:
        flash("Error deleting equipment")
    return redirect(url_for('patients.view_equipment', patient_id=patient_id))

@patients_bp.route('/patients/delete/<int:patient_id>')
def delete_patient(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    patient_crud = PatientCRUD(WebPatientModule(), auth_module)
    if patient_crud.delete_patient(patient_id):
        flash("Patient deleted successfully")
    else:
        flash("Error deleting patient")
    return redirect(url_for('patients.list_patients'))

@patients_bp.route('/patients/<int:patient_id>/costing')
def view_costing(patient_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockPatientModule:
        def __init__(self):
            self.current_patient_id = patient_id
            self.crud_handler = PatientCRUD(self, auth_module)
        def get_selected_patients(self):
            return [self.current_patient_id]

    costing_handler = CostingHandler(MockPatientModule())
    cost_details = costing_handler.calculate_cost()
    
    return render_template('costing.html', cost_details=cost_details, patient_id=patient_id)
