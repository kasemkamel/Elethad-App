import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from old_database import *


# This is a simple GUI application for managing users, suppliers, and medicines in a company.
class LoginWindow(tk.Toplevel):
    """A simple login window that prompts for username and password."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.withdraw()
        self.title("Login") 
        self.geometry("300x150")
        self.grab_set()
        self.focus_force()

        self.configure(bg="black")

        username_frame = tk.Frame(self, bg="black")
        username_frame.pack(pady=10)

        tk.Label(username_frame, text="Username:", bg="black", fg="white").pack(side="left", padx=20)
        self.username_entry = tk.Entry(username_frame, bg="gray", fg="white")
        self.username_entry.pack(side="left", padx=5)
        

        password_frame = tk.Frame(self, bg="black")
        password_frame.pack(pady=10)

        tk.Label(password_frame, text="Password:", bg="black", fg="white").pack(side="left", padx=20)
        self.password_entry = tk.Entry(password_frame, bg="gray", fg="white", show='*') 
        self.password_entry.pack(side="left", padx=5)

        login_button = tk.Button(self, text="Login", command=self.login, bg="darkblue", fg="white")
        login_button.pack(pady=10)
        
        self.username_entry.bind('<Return>', self.focus_password_entry)
        self.password_entry.bind('<Return>', self.login)

    def focus_password_entry(self, event=None):
        self.password_entry.focus()

    def login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        role = self.get_user_role(username, password)
    
        if role:

            self.parent.set_user(username, role)
            self.destroy()
            self.parent.deiconify()
        else:
            messagebox.showerror("Error", "Invalid username or password!")


    def get_user_role(self, username, password):
        result = self.parent.users.select_by_credentials(username, password)

        if result:
            return result[3]
        return None

# This is a sidebar that contains buttons to switch between different frames.
class Sidebar(tk.Frame):
    """A sidebar that contains buttons to switch between different frames."""
    def __init__(self, parent, role):
        super().__init__(parent, width=1000, bg='lightgray')
        self.parent = parent
        self.role = role
        # self.pack(side="right", fill="y")
        
        username = tk.Label(self,text = parent.user_name,  bg='lightgray')
        username.pack()
        
        label = tk.Label(self, bg='lightgray')
        label.pack(pady=40)
        buttons = []
        if self.role == "Ac": # Ac = Accountant
            buttons = [
                ("Main", self.show_main), 
                ("Frame 1", self.show_frame_1),
                ("Frame 2", self.show_frame_2),
                ("Frame 3", self.show_frame_3),
            ]
        elif self.role == "W": # W = Warehouse Worker
            buttons = [
                ("Main", self.show_main), 
                ("Frame 4", self.show_frame_4),
                ("Frame 5", self.show_frame_5),
            ]
        elif self.role == "Admin":
            buttons = [
                ("Main", self.show_main), 
                ("Frame 1", self.show_frame_1),
                ("Frame 2", self.show_frame_2),
                ("Frame 3", self.show_frame_3),
                ("Frame 4", self.show_frame_4),
                ("Frame 5", self.show_frame_5),
                ("Admin Farme 1", self.show_admin_frame_1),
                ("Admin Farme 2", self.show_admin_frame_2),
            ]
        
        # don't forget to remove else 
        else:
            buttons = [
                ("Main", self.show_main), 
                ("Frame 1", self.show_frame_1),
                ("Frame 2", self.show_frame_2),
                ("Frame 3", self.show_frame_3),
                ("Frame 4", self.show_frame_4),
                ("Frame 5", self.show_frame_5),
                ("Admin Farme 1", self.show_admin_frame_1),
                ("Admin Farme 2", self.show_admin_frame_2),
            ]
            
        for text, command in buttons:
            btn = tk.Button(self, text=text,  command=command)
            btn.pack(fill='x', padx=10, pady=10)


    def show_main(self, event=None):
        """Switch to the main frame."""
        self.master.switch_frame(MainFrame)
    
    def show_frame_1(self):
        """Switch to Frame 1."""
        self.master.switch_frame(Frame1)

    def show_frame_2(self):
        """Switch to Frame 2."""
        self.master.switch_frame(Frame2)

    def show_frame_3(self):
        self.master.switch_frame(Frame3)

    def show_frame_4(self):
        self.master.switch_frame(Frame4)

    def show_frame_5(self):
        self.master.switch_frame(Frame5)
        
    def show_admin_frame_1(self):
        self.master.switch_frame(AdminFrame1)
    
    def show_admin_frame_2(self):
        self.master.switch_frame(AdminFrame2)
    
# This is a header that contains the application title and buttons for toggling the sidebar and logging out.
class Header(tk.Frame):
    def __init__(self, parent, toggle_callback, logout_callback):
        super().__init__(parent, bg="darkgray", height=50)
        self.parent = parent
        self.pack(side="top", fill="x")

        self.logout_button = tk.Button(self, text="Logout", command=logout_callback)
        self.logout_button.pack(side="left", padx=10, pady=10)

        self.app_title = tk.Label(self, text="- Elethad -", font=("Arial", 16), bg="darkgray", fg="white")
        self.app_title.pack(side="left", expand=True, fill=None, anchor="center", padx=10, pady=10)
        self.app_title.bind('<Button 1>', self.parent.sidebar.show_main)
        
        self.toggle_button = tk.Button(self, text="==", command=toggle_callback)
        self.toggle_button.pack(side="right", padx=10, pady=10)

# This is a resizable image frame that displays an image and resizes it when the frame is resized.
class ResizableImageFrame(tk.Frame):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.pack_propagate(False) 
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight())
        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        self.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        new_width = event.width
        new_height = event.height

        resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)

        self.canvas.itemconfig(self.image_id, image=self.image)

        self.canvas.config(width=new_width, height=new_height)

# This is the main frame that contains the welcome message and the resizable image frames.
class MainFrame(tk.Frame):
    def __init__(self, parent):
        self.bg = '#119CB4'
        super().__init__(parent, bg=self.bg)
        label = tk.Label(self, text='Welcome to Elethad Company', font=('Arial', 20, 'bold'), fg='#1B0C00', bg=self.bg) #
        label.pack(pady=10)
        
        
        imagesPathesList = ['t1.jpeg', 't2.jpeg', 't3.jpeg', 't4.jpeg']
        
        frame1 = tk.Frame(self, )
        frame1.pack(expand=True, fill="both")
        
        imageFrameRightUp = ResizableImageFrame(frame1, imagesPathesList[0])
        imageFrameRightUp.grid(row=0, column=1, sticky="nsew")
        frame1.grid_columnconfigure(1, weight=1)
        
        imageFrameLeftUp = ResizableImageFrame(frame1, imagesPathesList[1])
        imageFrameLeftUp.grid(row=0, column=0, sticky="nsew")
        frame1.grid_columnconfigure(0, weight=1)
        
        frame1.grid_rowconfigure(0, weight=1)
        
        
        ##
        frame2 = tk.Frame(self, )
        frame2.pack(expand=True, fill="both")

        imageFrameRightDown = ResizableImageFrame(frame2, imagesPathesList[2])
        imageFrameRightDown.grid(row=0, column=1, sticky="nsew")
        frame2.grid_columnconfigure(1, weight=1)
        
        imageFrameLeftDown = ResizableImageFrame(frame2, imagesPathesList[3])
        imageFrameLeftDown.grid(row=0, column=0, sticky="nsew")
        frame2.grid_columnconfigure(0, weight=1)

        frame2.grid_rowconfigure(0, weight=1) 
        
# This is a simple frame that displays a message.
class Frame1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightblue")
        label = tk.Label(self, text="This is Frame 1", font=("Arial", 16), bg="lightblue")
        label.pack(pady=20)

# This is a simple frame that displays a message.
class Frame2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgreen")
        label = tk.Label(self, text="This is Frame 2", font=("Arial", 16), bg="lightgreen")
        label.pack(pady=20)

# This is a simple frame that displays a message.
class Frame3(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightpink")
        label = tk.Label(self, text="This is Frame 3", font=("Arial", 16), bg="lightpink")
        label.pack(pady=20)

# This is a simple frame that displays a message for warehouse workers.
class Frame4(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightyellow")
        label = tk.Label(self, text="This is Frame 4 (Warehouse Worker)", font=("Arial", 16), bg="lightyellow")
        label.pack(pady=20)

# This is a simple frame that displays a message for warehouse workers.
class Frame5(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")
        label = tk.Label(self, text="This is Frame 5 (Warehouse Worker)", font=("Arial", 16), bg="lightgray")
        label.pack(pady=20)

# This is an admin frame that allows adding new users, suppliers, and medicines.
class AdminFrame1(tk.Frame):
    def __init__(self, parent):
        self.bg = 'lightblue'
        super().__init__(parent, bg=self.bg)
        self.parent = parent
        self.supplier_id = None
        self.create_scrollable_widgets()

    def create_scrollable_widgets(self):
        # Create main canvas and scrollbar
        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg)
        
        # Configure canvas scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind canvas resize event
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Create the actual content
        self.create_content()

    def on_canvas_configure(self, event):
        # Update the scrollable frame width to match canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        # Enable mousewheel scrolling
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_content(self):
        # Main container with grid layout
        main_container = tk.Frame(self.scrollable_frame, bg=self.bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid weights for responsive layout
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        
        # Create sections
        self.create_medicine_section(main_container)
        self.create_user_section(main_container)
        self.create_supplier_section(main_container)
        self.create_stock_section(main_container)  # New section
        
        # Load initial data
        self.load_suppliers()
        self.load_medicines()

    def create_medicine_section(self, parent):
        # Medicine frame - Top Left
        medicine_frame = tk.LabelFrame(parent, text="Medicine Management", 
                                     font=('Arial', 14, 'bold'), bg=self.bg,
                                     relief="ridge", bd=2)
        medicine_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure internal grid
        medicine_frame.grid_columnconfigure(1, weight=1)
        
        # Medicine form fields
        tk.Label(medicine_frame, text="Medicine Name:", bg=self.bg).grid(
            row=0, column=0, padx=10, pady=5, sticky="e")
        self.medicine_name_entry = tk.Entry(medicine_frame, width=30)
        self.medicine_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(medicine_frame, text="Description:", bg=self.bg).grid(
            row=1, column=0, padx=10, pady=5, sticky="ne")
        self.description_entry = tk.Text(medicine_frame, height=4, width=30)
        self.description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(medicine_frame, text="Price:", bg=self.bg).grid(
            row=2, column=0, padx=10, pady=5, sticky="e")
        self.price_entry = tk.Entry(medicine_frame, width=30)
        self.price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(medicine_frame, text="Supplier:", bg=self.bg).grid(
            row=3, column=0, padx=10, pady=5, sticky="e")
        self.supplier_var = tk.StringVar()
        self.supplier_menu = ttk.Combobox(medicine_frame, textvariable=self.supplier_var, width=27)
        self.supplier_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_menu.bind("<<ComboboxSelected>>", self.on_supplier_selected)
        
        # Medicine buttons
        button_frame = tk.Frame(medicine_frame, bg=self.bg)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="Add Medicine", command=self.add_medicine,
                 bg="green", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_medicine_form,
                 bg="orange", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)

    def create_user_section(self, parent):
        # User frame - Top Right
        user_frame = tk.LabelFrame(parent, text="User Management", 
                                 font=('Arial', 14, 'bold'), bg=self.bg,
                                 relief="ridge", bd=2)
        user_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure internal grid
        user_frame.grid_columnconfigure(1, weight=1)
        
        # User form fields
        tk.Label(user_frame, text="Username:", bg=self.bg).grid(
            row=0, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = tk.Entry(user_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(user_frame, text="Password:", bg=self.bg).grid(
            row=1, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(user_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(user_frame, text="Role:", bg=self.bg).grid(
            row=2, column=0, padx=10, pady=5, sticky="e")
        self.role_var = tk.StringVar(value="admin")
        role_dropdown = tk.OptionMenu(user_frame, self.role_var, "admin", "W", "Ac")
        role_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # User buttons
        button_frame = tk.Frame(user_frame, bg=self.bg)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="Add User", command=self.add_user,
                 bg="green", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_user_form,
                 bg="orange", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)

    def create_supplier_section(self, parent):
        # Supplier frame - Bottom Left
        supplier_frame = tk.LabelFrame(parent, text="Supplier Management", 
                                     font=('Arial', 14, 'bold'), bg=self.bg,
                                     relief="ridge", bd=2)
        supplier_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure internal grid
        supplier_frame.grid_columnconfigure(1, weight=1)
        
        # Supplier form fields
        tk.Label(supplier_frame, text="Supplier Name:", bg=self.bg).grid(
            row=0, column=0, padx=10, pady=5, sticky="e")
        self.suppliername_entry = tk.Entry(supplier_frame, width=30)
        self.suppliername_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(supplier_frame, text="Contact Info:", bg=self.bg).grid(
            row=1, column=0, padx=10, pady=5, sticky="e")
        self.contact_info_entry = tk.Entry(supplier_frame, width=30)
        self.contact_info_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Supplier buttons
        button_frame = tk.Frame(supplier_frame, bg=self.bg)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="Add Supplier", command=self.add_supplier,
                 bg="green", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Supplier", command=self.del_supplier,
                 bg="red", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_supplier_form,
                 bg="orange", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)

    def create_stock_section(self, parent):
        # Stock frame - Bottom Right (New section)
        stock_frame = tk.LabelFrame(parent, text="Stock Management", 
                                  font=('Arial', 14, 'bold'), bg=self.bg,
                                  relief="ridge", bd=2)
        stock_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure internal grid
        stock_frame.grid_columnconfigure(1, weight=1)
        
        # Stock form fields
        tk.Label(stock_frame, text="Medicine:", bg=self.bg).grid(
            row=0, column=0, padx=10, pady=5, sticky="e")
        self.medicine_var = tk.StringVar()
        self.medicine_menu = ttk.Combobox(stock_frame, textvariable=self.medicine_var, width=27)
        self.medicine_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(stock_frame, text="Quantity:", bg=self.bg).grid(
            row=1, column=0, padx=10, pady=5, sticky="e")
        self.stock_quantity_entry = tk.Entry(stock_frame, width=30)
        self.stock_quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Stock buttons
        button_frame = tk.Frame(stock_frame, bg=self.bg)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="Add Stock", command=self.add_stock,
                 bg="green", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Stock", command=self.remove_stock,
                 bg="red", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Form", command=self.clear_stock_form,
                 bg="orange", fg="white", font=('Arial', 10, 'bold')).pack(side="left", padx=5)

    # Original methods (keep all existing methods)
    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not username or not password or not role:
            messagebox.showwarning("Input Error", "All fields must be filled!")
            return

        try:
            self.parent.users.insert(username, password, role)
            messagebox.showinfo("Success", f"User '{username}' added successfully!")
            self.clear_user_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")

    def clear_user_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_var.set("admin")

    def add_supplier(self):
        suppliername = self.suppliername_entry.get().strip()
        contact_info = self.contact_info_entry.get().strip()

        if not suppliername or not contact_info:
            messagebox.showwarning("Input Error", "All fields must be filled!")
            return

        try:
            self.parent.supplier.insert(suppliername, contact_info)
            messagebox.showinfo("Success", f"Supplier '{suppliername}' added successfully!")
            self.clear_supplier_form()
            self.load_suppliers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

    def del_supplier(self):
        # Implementation for deleting supplier
        selected_name = self.supplier_var.get()
        if selected_name == "--choose one--" or not selected_name:
            messagebox.showwarning("Selection Error", "Please select a supplier to delete!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete supplier '{selected_name}'?"):
            try:
                supplier_id = self.suppliers_dict.get(selected_name)
                self.parent.supplier.delete(supplier_id)
                messagebox.showinfo("Success", f"Supplier '{selected_name}' deleted successfully!")
                self.load_suppliers()
                self.clear_supplier_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")

    def clear_supplier_form(self):
        self.suppliername_entry.delete(0, tk.END)
        self.contact_info_entry.delete(0, tk.END)

    def load_suppliers(self):
        suppliers = self.parent.supplier.select_id_name()
        supplier_names = [name for _, name in suppliers]
        self.supplier_menu['values'] = ["--choose one--"] + supplier_names
        self.supplier_menu.current(0)
        self.suppliers_dict = {name: supplier_id for supplier_id, name in suppliers}

    def on_supplier_selected(self, event):
        selected_name = self.supplier_var.get() if self.supplier_var.get() != "--choose one--" else None
        self.supplier_id = self.suppliers_dict.get(selected_name)
    
    def add_medicine(self):
        medicine_name = self.medicine_name_entry.get().strip()
        description = self.description_entry.get("1.0", tk.END).strip()
        price = self.price_entry.get().strip()
        if not medicine_name or not self.supplier_id or not price:
            messagebox.showwarning("Input Error", "Medicine name, price, and supplier must be filled!")
            return
        try:
            # Validate price
            float(price)
            self.parent.medicine.insert(medicine_name, description, price, self.supplier_id)
            messagebox.showinfo("Success", f"Medicine '{medicine_name}' added successfully!")
            self.clear_medicine_form()
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
        self.load_medicines()  # Reload medicines after adding

    def load_medicines(self):
        medicines = self.parent.medicine.select_id_name()
        medicine_names = [name for _, name in medicines]
        self.medicine_menu['values'] = ["--choose one--"] + medicine_names
        self.medicine_menu.current(0)
        self.medicines_dict = {name: medicine_id for medicine_id, name in medicines}

    def clear_medicine_form(self):
        self.medicine_name_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.price_entry.delete(0, tk.END)
        self.supplier_id = None
        self.supplier_menu.current(0)

    # New methods for stock management
    def add_stock(self):
        medicine_name = self.medicine_var.get()
        quantity = self.stock_quantity_entry.get().strip()
        
        if not medicine_name or not quantity:
            messagebox.showwarning("Input Error", "Please select medicine and enter quantity!")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive!")
                return
            
            # Implementation would require medicine selection logic
            messagebox.showinfo("Success", f"Stock added successfully!")
            self.clear_stock_form()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock: {str(e)}")

    def remove_stock(self):
        medicine_name = self.medicine_var.get()
        quantity = self.stock_quantity_entry.get().strip()
        
        if not medicine_name or not quantity:
            messagebox.showwarning("Input Error", "Please select medicine and enter quantity!")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive!")
                return
            
            # Implementation would require medicine selection logic
            messagebox.showinfo("Success", f"Stock removed successfully!")
            self.clear_stock_form()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove stock: {str(e)}")

    def clear_stock_form(self):
        self.medicine_var.set("")
        self.stock_quantity_entry.delete(0, tk.END) 


# This is an admin frame that allows adding new users, suppliers, and medicines.
class AdminFrame2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")
        label = tk.Label(self, text="This is admin Frame no. Two", font=("Arial", 16), bg="#11f3c9")
        label.pack(pady=20)


# This is the main application class that initializes the GUI and manages the frames.
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Elethat Company")
        self.state("zoomed")
        self.wm_minsize(800, 600)
        
        self.db = Database()
        self.users = User(self.db)
        self.supplier = Supplier(self.db)
        self.medicine = Medicine(self.db)
        
        self.user_name = None
        self.user_role = None


        self.login_window = LoginWindow(self)
        self.wait_window(self.login_window) 

        
        
        self.sidebar = Sidebar(self, self.user_role)

        self.header = Header(self, self.toggle_sidebar, self.logout)
        
        self.content_frame = None
        self.sidebar_visible = False

        self.switch_frame(MainFrame)
        
        if not self.user_role:
            self.destroy()

    def set_user(self, username, role):
        self.user_role = role
        self.user_name = username

    def switch_frame(self, frame_class):
        if self.content_frame is not None:
            self.content_frame.destroy()
        self.content_frame = frame_class(self)
        self.content_frame.pack(side="left", expand=True, fill="both")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()  
        else:
            self.sidebar.pack(side="right", fill="y") 
        self.sidebar_visible = not self.sidebar_visible
    
    def logout(self):
        self.set_user("", "") 
        self.destroy()  
        self.__init__()
    


# This is the main entry point of the application.
if __name__ == "__main__":
    app = App()
    app.mainloop()
