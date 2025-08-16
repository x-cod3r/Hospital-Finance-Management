from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.auth import AuthModule

settings_bp = Blueprint('settings', __name__, template_folder='../templates/settings')

auth_module = AuthModule()

@settings_bp.route('/settings')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('settings.html', auth_module=auth_module, session=session)

@settings_bp.route('/settings/users')
def users():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # This is a placeholder for the actual UserManagementHandler object
    # In a real application, you would have a better way of managing this
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    user_management_handler = UserManagementHandler(MockSettingsModule(), auth_module)
    users = user_management_handler.load_users()
    
    return render_template('users.html', users=users)

@settings_bp.route('/settings/care_levels/add', methods=['GET', 'POST'])
def add_care_level():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        
        class MockSettingsModule:
            def __init__(self):
                self.parent = None

        care_level_management_handler = CareLevelManagementHandler(MockSettingsModule())
        if care_level_management_handler.add_care_level(name, rate):
            flash(f"Care level {name} added successfully")
        else:
            flash(f"Error adding care level {name}")
        return redirect(url_for('settings.care_levels'))
        
    return render_template('add_care_level.html')

@settings_bp.route('/settings/care_levels/edit/<int:care_level_id>', methods=['GET', 'POST'])
def edit_care_level(care_level_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    care_level_management_handler = CareLevelManagementHandler(MockSettingsModule())
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        if care_level_management_handler.edit_care_level(care_level_id, name, rate):
            flash(f"Care level {name} updated successfully")
        else:
            flash(f"Error updating care level {name}")
        return redirect(url_for('settings.care_levels'))
        
    care_level = care_level_management_handler.get_care_level(care_level_id)
    return render_template('edit_care_level.html', care_level=care_level)

@settings_bp.route('/settings/care_levels/delete/<int:care_level_id>')
def delete_care_level(care_level_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    care_level_management_handler = CareLevelManagementHandler(MockSettingsModule())
    if care_level_management_handler.delete_care_level(care_level_id):
        flash("Care level deleted successfully")
    else:
        flash("Error deleting care level")
    return redirect(url_for('settings.care_levels'))

@settings_bp.route('/settings/care_levels')
def care_levels():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    care_level_management_handler = CareLevelManagementHandler(MockSettingsModule())
    care_levels = care_level_management_handler.load_care_levels()
    
    return render_template('care_levels.html', care_levels=care_levels)

@settings_bp.route('/settings/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        
        class MockSettingsModule:
            def __init__(self):
                self.parent = None

        equipment_management_handler = EquipmentManagementHandler(MockSettingsModule())
        if equipment_management_handler.add_equipment(name, price):
            flash(f"Equipment {name} added successfully")
        else:
            flash(f"Error adding equipment {name}")
        return redirect(url_for('settings.equipment'))
        
    return render_template('add_equipment.html')

@settings_bp.route('/settings/equipment/edit/<int:equipment_id>', methods=['GET', 'POST'])
def edit_equipment(equipment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    equipment_management_handler = EquipmentManagementHandler(MockSettingsModule())
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        if equipment_management_handler.edit_equipment(equipment_id, name, price):
            flash(f"Equipment {name} updated successfully")
        else:
            flash(f"Error updating equipment {name}")
        return redirect(url_for('settings.equipment'))
        
    equipment = equipment_management_handler.get_equipment(equipment_id)
    return render_template('edit_equipment.html', equipment=equipment)

@settings_bp.route('/settings/equipment/delete/<int:equipment_id>')
def delete_equipment(equipment_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    equipment_management_handler = EquipmentManagementHandler(MockSettingsModule())
    if equipment_management_handler.delete_equipment(equipment_id):
        flash("Equipment deleted successfully")
    else:
        flash("Error deleting equipment")
    return redirect(url_for('settings.equipment'))

@settings_bp.route('/settings/equipment')
def equipment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    equipment_management_handler = EquipmentManagementHandler(MockSettingsModule())
    equipment = equipment_management_handler.load_equipment()
    
    return render_template('equipment.html', equipment=equipment)

@settings_bp.route('/settings/items')
def items():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    item_management_handler = ItemManagementHandler(MockSettingsModule())
    interventions = item_management_handler.load_interventions()
    
    items = {}
    for category in ["labs", "drugs", "radiology", "consultations"]:
        items[category] = item_management_handler.load_items(category)
    
    return render_template('items.html', interventions=interventions, items=items)

@settings_bp.route('/settings/users/add', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        privileges = request.form.getlist('privileges')
        
        class MockSettingsModule:
            def __init__(self):
                self.parent = None

        user_management_handler = UserManagementHandler(MockSettingsModule(), auth_module)
        if user_management_handler.create_user(username, password, privileges):
            flash(f"User {username} created successfully")
        else:
            flash(f"Error creating user {username}")
        return redirect(url_for('settings.users'))
        
    return render_template('add_user.html')

@settings_bp.route('/settings/users/delete/<username>')
def delete_user(username):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    class MockSettingsModule:
        def __init__(self):
            self.parent = None

    user_management_handler = UserManagementHandler(MockSettingsModule(), auth_module)
    if user_management_handler.delete_user(username):
        flash("User deleted successfully")
    else:
        flash("Error deleting user")
    return redirect(url_for('settings.users'))
