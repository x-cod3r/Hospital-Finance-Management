from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys
import os
import configparser

# Add the parent directory to the path to allow imports from the 'modules' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.auth import AuthModule
from blueprints.doctors import doctors_bp
from blueprints.nurses import nurses_bp
from blueprints.patients import patients_bp
from blueprints.company import company_bp
from blueprints.settings import settings_bp

app = Flask(__name__)
app.register_blueprint(doctors_bp)
app.register_blueprint(nurses_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(company_bp)
app.register_blueprint(settings_bp)
app.secret_key = os.urandom(24)

auth_module = AuthModule()

# Read configuration
config = configparser.ConfigParser()
config.read('Config/config.ini')
debug_mode = config.getboolean('DEBUG', 'debugmode', fallback=False)

@app.before_request
def before_request():
    if debug_mode is True :
            session["username"] = "admin"
            session["password"] = "admin123"
    #if debug_mode and 'username' not in session:
        #if request.endpoint and 'static' not in request.endpoint and request.endpoint != 'login':
            #session['username'] = 'admin'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if auth_module.authenticate(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if debug_mode and 'username' not in session:
        session['username'] = 'admin'

    if 'username' not in session:
        return redirect(url_for('login'))
    
    privileges = {
        'view_doctors_tab': auth_module.has_privilege(session['username'], 'view_doctors_tab'),
        'view_nurses_tab': auth_module.has_privilege(session['username'], 'view_nurses_tab'),
        'view_patients_tab': auth_module.has_privilege(session['username'], 'view_patients_tab'),
        'view_reports_tab': auth_module.has_privilege(session['username'], 'view_reports_tab'),
        'view_settings_tab': auth_module.has_privilege(session['username'], 'view_settings_tab'),
    }
    
    return render_template('index.html', username=session['username'], privileges=privileges)

if __name__ == '__main__':
    app.run(debug=True)
