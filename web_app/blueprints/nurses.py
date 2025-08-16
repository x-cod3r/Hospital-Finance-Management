from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.nurse.crud import NurseCRUD
from modules.auth import AuthModule

nurses_bp = Blueprint('nurses', __name__, template_folder='../templates/nurses')

auth_module = AuthModule()

@nurses_bp.route('/nurses')
def list_nurses():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockNurseModule:
        def __init__(self):
            self.parent = None

    nurse_crud = NurseCRUD(MockNurseModule(), auth_module)
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
        
        class MockNurseModule:
            def __init__(self):
                self.parent = None

        nurse_crud = NurseCRUD(MockNurseModule(), auth_module)
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
    
    class MockNurseModule:
        def __init__(self):
            self.parent = None

    nurse_crud = NurseCRUD(MockNurseModule(), auth_module)
    
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
    
    class MockNurseModule:
        def __init__(self):
            self.parent = None

    shifts_handler = ShiftsHandler(MockNurseModule())
    shifts = shifts_handler.load_shifts(nurse_id)
    
    return render_template('shifts.html', shifts=shifts, nurse_id=nurse_id)

@nurses_bp.route('/nurses/<int:nurse_id>/interventions')
def view_interventions(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockNurseModule:
        def __init__(self):
            self.parent = None

    interventions_handler = InterventionsHandler(MockNurseModule())
    interventions = interventions_handler.load_interventions()
    
    return render_template('interventions.html', interventions=interventions, nurse_id=nurse_id)

@nurses_bp.route('/nurses/delete/<int:nurse_id>')
def delete_nurse(nurse_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockNurseModule:
        def __init__(self):
            self.parent = None

    nurse_crud = NurseCRUD(MockNurseModule(), auth_module)
    if nurse_crud.delete_nurse(nurse_id):
        flash("Nurse deleted successfully")
    else:
        flash("Error deleting nurse")
    return redirect(url_for('nurses.list_nurses'))
