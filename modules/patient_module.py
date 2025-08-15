import tkinter as tk
from tkinter import ttk
from .patient.crud import PatientCRUD
from .patient.stays import StaysHandler
from .patient.items import ItemsHandler
from .patient.costing import CostingHandler

class PatientModule:
    def __init__(self, parent):
        self.parent = parent
        self.doctor_module = None
        self.nurse_module = None

        self.crud_handler = PatientCRUD(self)
        self.stays_handler = StaysHandler(self)
        self.items_handler = ItemsHandler(self)
        self.costing_handler = CostingHandler(self)

        self.setup_ui()
        self.crud_handler.load_patients()

    def setup_ui(self):
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(main_frame, text="Patients", padding="10")
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.patient_vars = {}

        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(buttons_frame, text="Add Patient", command=self.crud_handler.add_patient).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(buttons_frame, text="Edit Patient", command=self.crud_handler.edit_patient).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(buttons_frame, text="Delete Patient", command=self.crud_handler.delete_patient).pack(fill=tk.X)

        details_frame = ttk.LabelFrame(main_frame, text="Patient Details", padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew")

        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)

        self.admission_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.admission_date_var, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(details_frame, text="Admission Date:").grid(row=1, column=0, sticky=tk.W, pady=2)

        self.discharge_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.discharge_date_var, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(details_frame, text="Discharge Date:").grid(row=2, column=0, sticky=tk.W, pady=2)

        notebook = ttk.Notebook(details_frame)
        notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.stays_tab_frame = ttk.Frame(notebook)
        notebook.add(self.stays_tab_frame, text="Stays")
        self.stays_handler.setup_stays_tab(self.stays_tab_frame)

        self.labs_tab_frame = ttk.Frame(notebook)
        notebook.add(self.labs_tab_frame, text="Labs")
        self.items_handler.setup_category_tab(self.labs_tab_frame, "labs")

        self.drugs_tab_frame = ttk.Frame(notebook)
        notebook.add(self.drugs_tab_frame, text="Drugs")
        self.items_handler.setup_category_tab(self.drugs_tab_frame, "drugs")

        self.radiology_tab_frame = ttk.Frame(notebook)
        notebook.add(self.radiology_tab_frame, text="Radiology")
        self.items_handler.setup_category_tab(self.radiology_tab_frame, "radiology")

        self.consultations_tab_frame = ttk.Frame(notebook)
        notebook.add(self.consultations_tab_frame, text="Consultations")
        self.items_handler.setup_category_tab(self.consultations_tab_frame, "consultations")

        cost_frame = ttk.LabelFrame(details_frame, text="Cost Calculation", padding="5")
        cost_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(cost_frame, text="Calculate Total Cost", command=self.costing_handler.calculate_cost).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cost_frame, text="Export Cost Sheet", command=self.costing_handler.export_cost_sheet).pack(side=tk.LEFT)

        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(3, weight=1)

    def clear_all_tabs(self):
        """Clear all data from the tabs"""
        for i in self.stays_handler.stays_tree.get_children():
            self.stays_handler.stays_tree.delete(i)
        for category in ["labs", "drugs", "radiology", "consultations"]:
            vars_attr = getattr(self, f"{category}_vars", None)
            if vars_attr and 'tree' in vars_attr:
                tree = vars_attr['tree']
                for item in tree.get_children():
                    tree.delete(item)

    def _refresh_other_modules(self):
        """Refresh patient lists in other modules."""
        if self.doctor_module:
            self.doctor_module.load_patients()
        if self.nurse_module:
            self.nurse_module.load_patients()
