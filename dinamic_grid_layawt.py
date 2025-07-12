""" 
I Think I will need it later => -------#
Dynamic Grid Layout for Tkinter
This module provides a dynamic grid layout system for Tkinter applications, allowing sections to be added and
arranged in a grid format. It supports flexible column configurations and automatic resizing based on the number of sections.
It can be used in both class-based and function-based approaches, making it versatile for different use
"""

import tkinter as tk
import math

class DynamicGridLayout:
    def __init__(self, parent, bg_color):
        self.parent = parent
        self.bg = bg_color
        self.sections = []
        self.columns = 2
        self.main_container = None
        
    def setup_container(self):
        self.main_container = tk.Frame(self.parent, bg=self.bg)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
    def add_section(self, section_creator_func, section_name):
        self.sections.append({
            'creator': section_creator_func,
            'name': section_name
        })
        
    def set_columns(self, columns):
        self.columns = columns
        
    def calculate_grid_size(self):
        total_sections = len(self.sections)
        rows = math.ceil(total_sections / self.columns)
        return rows, self.columns

    def configure_grid(self):
        rows, cols = self.calculate_grid_size()
        
        for col in range(cols):
            self.main_container.grid_columnconfigure(col, weight=1)
            
        for row in range(rows):
            self.main_container.grid_rowconfigure(row, weight=1)
            
    def render_sections(self):
        self.configure_grid()
        
        for i, section in enumerate(self.sections):
            row = i // self.columns
            col = i % self.columns
            
            section['creator'](self.main_container, row=row, column=col)
            
    def build_layout(self):
        self.setup_container()
        self.render_sections()

class YourMainClass:
    def __init__(self):
        self.bg = "white"  
        self.scrollable_frame = None
        self.layout = DynamicGridLayout(self.scrollable_frame, self.bg)
        
    def setup_dashboard(self):
        self.layout.add_section(self.create_medicine_section, "Medicine")
        self.layout.add_section(self.create_user_section, "Users")
        self.layout.add_section(self.create_supplier_section, "Suppliers")
        self.layout.add_section(self.create_stock_section, "Stock")
        
        self.layout.add_section(self.create_orders_section, "Orders")
        self.layout.add_section(self.create_reports_section, "Reports")
        
        self.layout.set_columns(3)
        
        self.layout.build_layout()
        
    def create_medicine_section(self, parent, row=0, column=0):
        pass
        
    def create_user_section(self, parent, row=0, column=1):
        pass
        

def create_flexible_grid(parent, bg_color, sections, columns=2):
    """
    Create a flexible grid layout
    
    Args:
        parent: Parent widget
        bg_color: Background color
        sections: List of tuples (section_creator_function, section_name)
        columns: Number of columns (default: 2)
    """
    main_container = tk.Frame(parent, bg=bg_color)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    total_sections = len(sections)
    rows = math.ceil(total_sections / columns)
    
    for col in range(columns):
        main_container.grid_columnconfigure(col, weight=1)
    for row in range(rows):
        main_container.grid_rowconfigure(row, weight=1)
    
    for i, (section_func, section_name) in enumerate(sections):
        row = i // columns
        col = i % columns
        section_func(main_container, row=row, column=col)
    
    return main_container

def setup_dashboard_simple(self):
    sections = [
        (self.create_medicine_section, "Medicine"),
        (self.create_user_section, "Users"),
        (self.create_supplier_section, "Suppliers"),
        (self.create_stock_section, "Stock"),
        (self.create_orders_section, "Orders"),
        (self.create_reports_section, "Reports"),
    ]
    
    create_flexible_grid(self.scrollable_frame, self.bg, sections, columns=3)