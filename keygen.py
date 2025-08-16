import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import hashlib
import base64

class KeygenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keygen")
        self.root.geometry("400x250")

        ttk.Label(root, text="Enter Number of Days:").pack(pady=10)
        self.days_entry = ttk.Entry(root, width=20)
        self.days_entry.pack(pady=5)
        self.days_entry.insert(0, "30")

        ttk.Button(root, text="Generate Key", command=self.generate_key).pack(pady=10)

        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(root, textvariable=self.key_var, width=50, state="readonly")
        key_entry.pack(pady=10)
        
        ttk.Button(root, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(pady=5)

    def generate_key(self):
        try:
            days = int(self.days_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        expiration_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        secret_key = "my-secret-key"  # This should be a secret key that you don't share
        data = f"{expiration_date}:{secret_key}"
        hashed_data = hashlib.sha256(data.encode()).hexdigest()
        license_key = f"{expiration_date}::{hashed_data}"
        
        encoded_key = base64.b64encode(license_key.encode()).decode()
        self.key_var.set(encoded_key)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.key_var.get())
        messagebox.showinfo("Success", "Key copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeygenApp(root)
    root.mainloop()
