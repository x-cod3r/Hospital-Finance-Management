icu-management-app/
│
├── main.py                  # Entry point of the app
├── config/                  # Configuration files (database paths, default settings)
│   └── config.ini
│
├── db/                      # Local databases (SQLite or JSON)
│   ├── doctors.db
│   ├── nurses.db
│   ├── patients.db
│   ├── interventions.db
│   ├── items.db             # Default packages and item prices
│   └── logs.db              # Settings change logs
│
├── modules/                 # Modular components
│   ├── auth.py              # Login / User management
│   ├── doctor_module.py
│   ├── nurse_module.py
│   ├── patient_module.py
│   ├── company_module.py
│   ├── settings_module.py
│   ├── reports_module.py
│   └── utils.py             # Helper functions
│
├── ui/                      # GUI files (Tkinter, PyQt5, etc.)
│   ├── main_window.ui
│   ├── login_window.ui
│   └── ...
│
├── export_templates/        # Templates for salary sheets, cost sheets, reports
│   ├── salary_template.xlsx
│   └── cost_template.xlsx
│
├── docs/
│   ├── README.md
│   ├── workflow.md
│   └── roadmap.md
│
└── requirements.txt         # Dependencies listn