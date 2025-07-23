import tkinter as tk
from tkinter import ttk

def configure_styles():
    """Configure application styles"""
    style = ttk.Style()
    
    # Configure frame styles
    style.configure("TFrame", background="#f0f0f0")
    
    # Configure label styles
    style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
    
    # Configure button styles
    style.configure("TButton", font=("Arial", 10))
    
    # Configure entry styles
    style.configure("TEntry", font=("Arial", 10))
    
    # Configure combobox styles
    style.configure("TCombobox", font=("Arial", 10))
    
    # Configure notebook styles
    style.configure("TNotebook", background="#f0f0f0")
    style.configure("TNotebook.Tab", font=("Arial", 10, "bold"))
    
    # Configure label frame styles
    style.configure("TLabelframe", background="#f0f0f0")
    style.configure("TLabelframe.Label", font=("Arial", 10, "bold"))