import tkinter as tk
from tkinter import ttk
from .settings.general import GeneralSettingsHandler
from .settings.user_management import UserManagementHandler
from .settings.audit_log import AuditLogHandler
from .settings.item_management import ItemManagementHandler
from .settings.care_level_management import CareLevelManagementHandler

class SettingsModule:
    def __init__(self, parent):
        self.parent = parent
        self.doctor_module = None
        self.nurse_module = None
        self.patient_module = None

        self.general_handler = GeneralSettingsHandler(self)
        self.user_management_handler = UserManagementHandler(self)
        self.audit_log_handler = AuditLogHandler(self)
        self.item_management_handler = ItemManagementHandler(self)
        self.care_level_management_handler = CareLevelManagementHandler(self)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General Settings")
        self.general_handler.setup_general_tab(general_tab)
        
        user_tab = ttk.Frame(notebook)
        notebook.add(user_tab, text="User Management")
        self.user_management_handler.setup_user_tab(user_tab)
        
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="Audit Log")
        self.audit_log_handler.setup_log_tab(log_tab)

        item_tab = ttk.Frame(notebook)
        notebook.add(item_tab, text="Item Management")
        self.item_management_handler.setup_item_tab(item_tab)

        care_level_tab = ttk.Frame(notebook)
        notebook.add(care_level_tab, text="Care Level Management")
        self.care_level_management_handler.setup_care_level_tab(care_level_tab)

    def _refresh_other_modules(self):
        """Refresh item lists in other modules."""
        if self.doctor_module:
            self.doctor_module.interventions_handler.load_interventions()
        if self.nurse_module:
            self.nurse_module.interventions_handler.load_interventions()
        if self.patient_module:
            self.patient_module.items_handler.setup_category_tab(self.patient_module.labs_tab_frame, "labs")
            self.patient_module.items_handler.setup_category_tab(self.patient_module.drugs_tab_frame, "drugs")
            self.patient_module.items_handler.setup_category_tab(self.patient_module.radiology_tab_frame, "radiology")
            self.patient_module.items_handler.setup_category_tab(self.patient_module.consultations_tab_frame, "consultations")
            self.patient_module.stays_handler.load_care_levels_for_combo()
