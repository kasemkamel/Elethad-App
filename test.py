import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import calendar

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

    tk.Label(medicine_frame, text="Medicine Name:", bg=self.bg, fg="#2C3E50").grid(
        row=0, column=0, padx=10, pady=5, sticky="e"
    )
    self.medicine_name_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
    self.medicine_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(medicine_frame, text="Description:", bg=self.bg, fg="#2C3E50").grid(
        row=1, column=0, padx=10, pady=5, sticky="ne"
    )
    self.description_entry = tk.Text(medicine_frame, height=4, width=30, font=("Arial", 10))
    self.description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

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
    
    # Expiry Date with Spinboxes
    tk.Label(medicine_frame, text="Expiry Date:", bg=self.bg, fg="#2C3E50").grid(
        row=4, column=0, padx=10, pady=5, sticky="e"
    )

    # Create frame for date spinboxes
    date_frame = tk.Frame(medicine_frame, bg=self.bg)
    date_frame.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    # Get current date for default values
    current_date = date.today()
    
    # Day Spinbox
    tk.Label(date_frame, text="Day:", bg=self.bg, fg="#2C3E50", font=("Arial", 9)).grid(
        row=0, column=0, padx=(0, 5), sticky="w"
    )
    self.day_spinbox = tk.Spinbox(
        date_frame,
        from_=1,
        to=31,
        width=5,
        font=("Arial", 10),
        value=current_date.day,
        command=self.validate_date,
        wrap=True
    )
    self.day_spinbox.grid(row=0, column=1, padx=(0, 10))

    # Month Spinbox
    tk.Label(date_frame, text="Month:", bg=self.bg, fg="#2C3E50", font=("Arial", 9)).grid(
        row=0, column=2, padx=(0, 5), sticky="w"
    )
    self.month_spinbox = tk.Spinbox(
        date_frame,
        from_=1,
        to=12,
        width=5,
        font=("Arial", 10),
        value=current_date.month,
        command=self.validate_date,
        wrap=True
    )
    self.month_spinbox.grid(row=0, column=3, padx=(0, 10))

    # Year Spinbox
    tk.Label(date_frame, text="Year:", bg=self.bg, fg="#2C3E50", font=("Arial", 9)).grid(
        row=0, column=4, padx=(0, 5), sticky="w"
    )
    self.year_spinbox = tk.Spinbox(
        date_frame,
        from_=current_date.year,
        to=current_date.year + 10,
        width=8,
        font=("Arial", 10),
        value=current_date.year,
        command=self.validate_date,
        wrap=False
    )
    self.year_spinbox.grid(row=0, column=5, padx=(0, 10))

    # Date display label (shows formatted date)
    self.date_display = tk.Label(
        date_frame,
        text=current_date.strftime("%d/%m/%Y"),
        bg=self.bg,
        fg="#27AE60",
        font=("Arial", 10, "bold")
    )
    self.date_display.grid(row=0, column=6, padx=(10, 0))

    # Bind events to validate date when values change
    self.day_spinbox.bind('<KeyRelease>', self.on_date_change)
    self.month_spinbox.bind('<KeyRelease>', self.on_date_change)
    self.year_spinbox.bind('<KeyRelease>', self.on_date_change)

    tk.Label(medicine_frame, text="Supplier:", bg=self.bg, fg="#2C3E50").grid(
        row=5, column=0, padx=10, pady=5, sticky="e"
    )
    self.supplier_var = tk.StringVar()
    self.supplier_menu = ttk.Combobox(
        medicine_frame, textvariable=self.supplier_var, width=27, font=("Arial", 10)
    )
    self.supplier_menu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
    self.supplier_menu.bind("<<ComboboxSelected>>", self.on_supplier_selected)

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

# Helper methods for date validation and handling
def validate_date(self):
    """Validate the date and update display"""
    try:
        day = int(self.day_spinbox.get())
        month = int(self.month_spinbox.get())
        year = int(self.year_spinbox.get())
        
        # Check if date is valid
        selected_date = datetime(year, month, day).date()
        
        # Update display
        self.date_display.config(
            text=selected_date.strftime("%d/%m/%Y"),
            fg="#27AE60"
        )
        
        # Adjust day if invalid for selected month
        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            self.day_spinbox.config(to=max_day)
            if int(self.day_spinbox.get()) > max_day:
                self.day_spinbox.delete(0, tk.END)
                self.day_spinbox.insert(0, str(max_day))
        else:
            self.day_spinbox.config(to=31)
            
    except ValueError:
        # Invalid date
        self.date_display.config(text="Invalid Date", fg="#E74C3C")

def on_date_change(self, event=None):
    """Handle date change events"""
    self.validate_date()

def get_expiry_date(self):
    """Get the selected expiry date"""
    try:
        day = int(self.day_spinbox.get())
        month = int(self.month_spinbox.get())
        year = int(self.year_spinbox.get())
        return datetime(year, month, day).date()
    except ValueError:
        return None

def set_expiry_date(self, date_obj):
    """Set the expiry date from a date object"""
    if date_obj:
        self.day_spinbox.delete(0, tk.END)
        self.day_spinbox.insert(0, str(date_obj.day))
        
        self.month_spinbox.delete(0, tk.END)
        self.month_spinbox.insert(0, str(date_obj.month))
        
        self.year_spinbox.delete(0, tk.END)
        self.year_spinbox.insert(0, str(date_obj.year))
        
        self.validate_date()

def clear_medicine_form(self):
    """Clear all form fields including date spinboxes"""
    self.medicine_name_entry.delete(0, tk.END)
    self.description_entry.delete(1.0, tk.END)
    self.price_entry.delete(0, tk.END)
    self.batch_number_entry.delete(0, tk.END)
    
    # Reset date to current date
    current_date = date.today()
    self.set_expiry_date(current_date)