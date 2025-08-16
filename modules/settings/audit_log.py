import tkinter as tk
from tkinter import ttk
from modules.auth import AuthModule

class AuditLogHandler:
    def __init__(self, settings_module):
        self.settings_module = settings_module
        self.parent = settings_module.parent
        self.auth_module = self.settings_module.auth_module

    def setup_log_tab(self, parent):
        """Setup audit log tab"""
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(parent, text="Refresh Logs", command=self.load_logs).pack(pady=10)
        
        self.load_logs()

    def load_logs(self):
        """Load audit logs for the current user"""
        self.log_text.delete(1.0, tk.END)
        
        current_user = self.auth_module.current_user
        if not current_user:
            return
            
        logs = self.auth_module.get_logs(current_user)
        
        for log in logs:
            user, action, timestamp, details = log
            log_entry = f"[{timestamp}] {user}: {action}"
            if details:
                log_entry += f" - {details}"
            log_entry += "\n"
            self.log_text.insert(tk.END, log_entry)
