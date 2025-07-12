import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry  # You'll need to install: pip install tkcalendar

def create_medicine_section(self, parent):
    medicine_frame = tk.LabelFrame(
        parent,
        text="Medicine Management",
        font=("Arial", 14, "bold"),
        bg=self.bg,
        fg="#2C3E50",
        relief="solid",
        bd=1,
    )
    medicine_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    medicine_frame.grid_columnconfigure(1, weight=1)
    
    # Medicine Name
    tk.Label(medicine_frame, text="Medicine Name:", bg=self.bg, fg="#2C3E50").grid(
        row=0, column=0, padx=10, pady=5, sticky="e"
    )
    self.medicine_name_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
    self.medicine_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    
    # Description
    tk.Label(medicine_frame, text="Description:", bg=self.bg, fg="#2C3E50").grid(
        row=1, column=0, padx=10, pady=5, sticky="ne"
    )
    self.description_entry = tk.Text(medicine_frame, height=4, width=30, font=("Arial", 10))
    self.description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
    # Price
    tk.Label(medicine_frame, text="Price:", bg=self.bg, fg="#2C3E50").grid(
        row=2, column=0, padx=10, pady=5, sticky="e"
    )
    self.price_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
    self.price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
    # Batch Number
    tk.Label(medicine_frame, text="Batch Number:", bg=self.bg, fg="#2C3E50").grid(
        row=3, column=0, padx=10, pady=5, sticky="e"
    )
    self.batch_number_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
    self.batch_number_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
    
    # Expiry Date
    tk.Label(medicine_frame, text="Expiry Date:", bg=self.bg, fg="#2C3E50").grid(
        row=4, column=0, padx=10, pady=5, sticky="e"
    )
    
    # Option 1: Using DateEntry (requires tkcalendar)
    self.expiry_date_entry = DateEntry(
        medicine_frame,
        width=27,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        font=("Arial", 10),
        date_pattern='yyyy-mm-dd'  # or 'dd/mm/yyyy' or 'mm/dd/yyyy'
    )
    self.expiry_date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
    # Option 2: Using Entry with validation (alternative to DateEntry)
    # self.expiry_date_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
    # self.expiry_date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    # self.expiry_date_entry.insert(0, "YYYY-MM-DD")  # Placeholder
    # self.expiry_date_entry.bind("<FocusIn>", self.clear_expiry_placeholder)
    # self.expiry_date_entry.bind("<FocusOut>", self.validate_expiry_date)
    
    # Supplier
    tk.Label(medicine_frame, text="Supplier:", bg=self.bg, fg="#2C3E50").grid(
        row=5, column=0, padx=10, pady=5, sticky="e"
    )
    self.supplier_var = tk.StringVar()
    self.supplier_menu = ttk.Combobox(
        medicine_frame, textvariable=self.supplier_var, width=27, font=("Arial", 10)
    )
    self.supplier_menu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    self.supplier_menu.bind("<<ComboboxSelected>>", self.on_supplier_selected)
    
    # Buttons
    button_frame = tk.Frame(medicine_frame, bg=self.bg)
    button_frame.grid(row=6, column=0, columnspan=2, pady=15)
    
    tk.Button(
        button_frame,
        text="Add Medicine",
        command=self.add_medicine,
        bg="#27AE60",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="Clear Form",
        command=self.clear_medicine_form,
        bg="#F39C12",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=5)

# Additional helper methods you'll need:

def clear_expiry_placeholder(self, event):
    """Clear placeholder text when entry is focused"""
    if self.expiry_date_entry.get() == "YYYY-MM-DD":
        self.expiry_date_entry.delete(0, tk.END)
        self.expiry_date_entry.config(fg='black')

def validate_expiry_date(self, event):
    """Validate expiry date format when entry loses focus"""
    from datetime import datetime
    
    date_str = self.expiry_date_entry.get()
    if not date_str:
        self.expiry_date_entry.insert(0, "YYYY-MM-DD")
        self.expiry_date_entry.config(fg='gray')
        return
    
    try:
        # Try to parse the date
        datetime.strptime(date_str, '%Y-%m-%d')
        self.expiry_date_entry.config(fg='black')
    except ValueError:
        # Invalid date format
        self.expiry_date_entry.config(fg='red')
        tk.messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")

def clear_medicine_form(self):
    """Clear all medicine form fields"""
    self.medicine_name_entry.delete(0, tk.END)
    self.description_entry.delete(1.0, tk.END)
    self.price_entry.delete(0, tk.END)
    self.batch_number_entry.delete(0, tk.END)
    
    # For DateEntry
    from datetime import date
    self.expiry_date_entry.set_date(date.today())
    
    # For regular Entry (if using Option 2)
    # self.expiry_date_entry.delete(0, tk.END)
    # self.expiry_date_entry.insert(0, "YYYY-MM-DD")
    # self.expiry_date_entry.config(fg='gray')
    
    self.supplier_var.set("")

def add_medicine(self):
    """Add medicine with all fields including batch number and expiry date"""
    medicine_name = self.medicine_name_entry.get()
    description = self.description_entry.get(1.0, tk.END).strip()
    price = self.price_entry.get()
    batch_number = self.batch_number_entry.get()
    expiry_date = self.expiry_date_entry.get_date()  # For DateEntry
    # expiry_date = self.expiry_date_entry.get()  # For regular Entry
    supplier = self.supplier_var.get()
    
    # Validation
    if not all([medicine_name, description, price, batch_number, expiry_date, supplier]):
        tk.messagebox.showerror("Error", "Please fill in all fields")
        return
    
    try:
        float(price)  # Validate price is numeric
    except ValueError:
        tk.messagebox.showerror("Error", "Price must be a valid number")
        return
    
    # Add your database insertion logic here
    medicine_data = {
        'name': medicine_name,
        'description': description,
        'price': float(price),
        'batch_number': batch_number,
        'expiry_date': expiry_date,
        'supplier': supplier
    }
    
    # Example: self.db.insert_medicine(medicine_data)
    print(f"Adding medicine: {medicine_data}")
    
    # Clear form after successful addition
    self.clear_medicine_form()
    tk.messagebox.showinfo("Success", "Medicine added successfully!")