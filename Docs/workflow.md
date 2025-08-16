## Application Workflow

### First-Time Setup
1.  **Generate License Key:** Run `python keygen.py` to generate a license key.
2.  **Initial Run:** Run `python main.py`. You will be prompted to enter the license key.
3.  **Login:** Log in with the default admin credentials (`admin`/`admin123`).

### Main Application
The application is organized into a series of tabs, with access controlled by user privileges.

*   **Doctors Tab:**
    *   Add, edit, and delete doctors.
    *   Track doctor shifts and interventions.
    *   Calculate and export doctor salaries.

*   **Nurses Tab:**
    *   Add, edit, and delete nurses.
    *   Track nurse shifts and interventions.
    *   Calculate and export nurse salaries.

*   **Patients Tab:**
    *   Add, edit, and delete patients.
    *   Manage patient stays and assign care levels.
    *   Record and bill for items (labs, drugs, etc.) and equipment.
    *   Calculate and export total patient costs.

*   **Company Tab:**
    *   Generate company-wide financial reports for custom date ranges.
    *   Export reports to Excel.

*   **Settings Tab:**
    *   **User Management:** Create new users and assign granular privileges.
    *   **Item Management:** Manage billable items and interventions.
    *   **Care Level Management:** Manage patient care levels and their associated costs.
    *   **Equipment Management:** Manage medical equipment and assign it to care levels.
    *   **Audit Log:** View a real-time log of all user actions.

*   **Sign Out Tab:**
    *   View your login time and sign out of the application.
