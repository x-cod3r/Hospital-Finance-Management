from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sys
import os

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.auth import AuthModule
from modules.settings.user_management import UserManagementHandler
from modules.settings.care_level_management import CareLevelManagementHandler
from modules.settings.equipment_management import EquipmentManagementHandler
from modules.settings.item_management import ItemManagementHandler

settings_bp = Blueprint('settings', __name__, template_folder='../templates/settings')

auth_module = AuthModule()

class WebSettingsModule:
    def __init__(self):
        self.auth_module = auth_module
        self.parent = None

@settings_bp.route('/settings')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('settings.html', auth_module=auth_module, session=session)

@settings_bp.route('/settings/users')
def users():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_management_handler = UserManagementHandler(WebSettingsModule(), auth_module)
    users = user_management_handler.load_users()
    
    return render_template('users.html', users=users)

@settings_bp.route('/settings/care_levels/add', methods=['GET', 'POST'])
def add_care_level():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        rate = request.form['rate']
        
        care_level_management_handler = CareLevelManagementHandler(WebSettingsModule())
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
    
    care_level_management_handler = CareLevelManagementHandler(WebSettingsModule())
    
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
        
    care_level_management_handler = CareLevelManagementHandler(WebSettingsModule())
    if care_level_management_handler.delete_care_level(care_level_id):
        flash("Care level deleted successfully")
    else:
        flash("Error deleting care level")
    return redirect(url_for('settings.care_levels'))

@settings_bp.route('/settings/care_levels')
def care_levels():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    care_level_management_handler = CareLevelManagementHandler(WebSettingsModule())
    care_levels = care_level_management_handler.load_care_levels()
    
    return render_template('care_levels.html', care_levels=care_levels)

@settings_bp.route('/settings/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        
        equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
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
    
    equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
    
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
        
    equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
    if equipment_management_handler.delete_equipment(equipment_id):
        flash("Equipment deleted successfully")
    else:
        flash("Error deleting equipment")
    return redirect(url_for('settings.equipment'))

@settings_bp.route('/settings/equipment')
def equipment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
    equipment = equipment_management_handler.load_equipment()
    
    return render_template('settings_equipment.html', equipment=equipment)

@settings_bp.route('/settings/care_level_equipment', methods=['GET'])
def manage_care_level_equipment():
    if 'username' not in session:
        return redirect(url_for('login'))

    care_level_management_handler = CareLevelManagementHandler(WebSettingsModule())
    equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())

    care_levels = care_level_management_handler.load_care_levels()
    all_equipment = equipment_management_handler.load_equipment()

    selected_care_level_id = request.args.get('care_level_id', type=int)
    assigned_equipment = []
    if selected_care_level_id:
        assigned_equipment = equipment_management_handler.load_assigned_equipment(selected_care_level_id)

    return render_template('settings/care_level_equipment.html', 
                           care_levels=care_levels, 
                           all_equipment=all_equipment, 
                           assigned_equipment=assigned_equipment, 
                           selected_care_level_id=selected_care_level_id)

@settings_bp.route('/settings/care_level_equipment/assign/<int:care_level_id>', methods=['POST'])
def assign_equipment_to_care_level(care_level_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    equipment_id = request.form.get('equipment_id', type=int)
    if equipment_id:
        equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
        if equipment_management_handler.assign_equipment(care_level_id, equipment_id):
            flash('Equipment assigned successfully.')
        else:
            flash('Equipment already assigned.')
    return redirect(url_for('settings.manage_care_level_equipment', care_level_id=care_level_id))

@settings_bp.route('/settings/care_level_equipment/unassign/<int:care_level_id>/<int:equipment_id>')
def unassign_equipment_from_care_level(care_level_id, equipment_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    equipment_management_handler = EquipmentManagementHandler(WebSettingsModule())
    if equipment_management_handler.unassign_equipment(care_level_id, equipment_id):
        flash('Equipment unassigned successfully.')
    else:
        flash('Error unassigning equipment.')
    return redirect(url_for('settings.manage_care_level_equipment', care_level_id=care_level_id))

@settings_bp.route('/settings/items')
def items():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    item_management_handler = ItemManagementHandler(WebSettingsModule())
    interventions = item_management_handler.load_interventions()
    
    items = {}
    for category in ["labs", "drugs", "radiology", "consultations"]:
        items[category] = item_management_handler.load_items(category)
    
    return render_template('settings/items.html', interventions=interventions, items=items)

@settings_bp.route('/settings/interventions/add', methods=['GET', 'POST'])
def add_intervention():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        bonus = request.form['bonus']
        
        item_management_handler = ItemManagementHandler(WebSettingsModule())
        if item_management_handler.add_intervention(name, bonus):
            flash(f"Intervention {name} added successfully")
        else:
            flash(f"Error adding intervention {name}")
        return redirect(url_for('settings.items'))
        
    return render_template('add_intervention.html')

@settings_bp.route('/settings/interventions/edit/<int:intervention_id>', methods=['GET', 'POST'])
def edit_intervention(intervention_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    item_management_handler = ItemManagementHandler(WebSettingsModule())
    
    if request.method == 'POST':
        name = request.form['name']
        bonus = request.form['bonus']
        if item_management_handler.edit_intervention(intervention_id, name, bonus):
            flash(f"Intervention {name} updated successfully")
        else:
            flash(f"Error updating intervention {name}")
        return redirect(url_for('settings.items'))
        
    intervention = item_management_handler.get_intervention(intervention_id)
    return render_template('edit_intervention.html', intervention=intervention)

@settings_bp.route('/settings/interventions/delete/<int:intervention_id>')
def delete_intervention(intervention_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    item_management_handler = ItemManagementHandler(WebSettingsModule())
    if item_management_handler.delete_intervention(intervention_id):
        flash("Intervention deleted successfully")
    else:
        flash("Error deleting intervention")
    return redirect(url_for('settings.items'))

@settings_bp.route('/settings/items/add', methods=['GET', 'POST'])
def add_item():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        price = request.form['price']
        
        item_management_handler = ItemManagementHandler(WebSettingsModule())
        if item_management_handler.add_item(category, name, price):
            flash(f"Item {name} added successfully")
        else:
            flash(f"Error adding item {name}")
        return redirect(url_for('settings.items'))
        
    return render_template('add_item.html')

@settings_bp.route('/settings/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    item_management_handler = ItemManagementHandler(WebSettingsModule())
    
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        price = request.form['price']
        if item_management_handler.edit_item(item_id, category, name, price):
            flash(f"Item {name} updated successfully")
        else:
            flash(f"Error updating item {name}")
        return redirect(url_for('settings.items'))
        
    item = item_management_handler.get_item(item_id)
    return render_template('edit_item.html', item=item)

@settings_bp.route('/settings/items/delete/<int:item_id>')
def delete_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    item_management_handler = ItemManagementHandler(WebSettingsModule())
    if item_management_handler.delete_item(item_id):
        flash("Item deleted successfully")
    else:
        flash("Error deleting item")
    return redirect(url_for('settings.items'))

@settings_bp.route('/settings/users/add', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        privileges = request.form.getlist('privileges')
        
        user_management_handler = UserManagementHandler(WebSettingsModule(), auth_module)
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
        
    user_management_handler = UserManagementHandler(WebSettingsModule(), auth_module)
    if user_management_handler.delete_user(username):
        flash("User deleted successfully")
    else:
        flash("Error deleting user")
    return redirect(url_for('settings.users'))
