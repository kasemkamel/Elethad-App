import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from database_new_Architecture import Database, User, Medicine, Supplier, Reports


class LoginWindow(tk.Toplevel):
    """A simple login window that prompts for username and password."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.withdraw()
        self.title("Login - Medicine Warehouse System")
        self.geometry("400x250")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        # Center the window
        self.center_window()

        self.configure(bg="#2C3E50")
        self.create_widgets()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#2C3E50", padx=40, pady=30)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = tk.Label(
            main_frame, 
            text="Medicine Warehouse System", 
            font=("Arial", 16, "bold"), 
            bg="#2C3E50", 
            fg="#ECF0F1"
        )
        title_label.pack(pady=(0, 20))

        # Username frame
        username_frame = tk.Frame(main_frame, bg="#2C3E50")
        username_frame.pack(fill="x", pady=10)

        tk.Label(
            username_frame, 
            text="Username:", 
            bg="#2C3E50", 
            fg="#ECF0F1",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(
            username_frame, 
            bg="#34495E", 
            fg="#ECF0F1",
            font=("Arial", 11),
            insertbackground="#ECF0F1",
            relief="flat",
            bd=10
        )
        self.username_entry.pack(fill="x", ipady=8)

        # Password frame
        password_frame = tk.Frame(main_frame, bg="#2C3E50")
        password_frame.pack(fill="x", pady=10)

        tk.Label(
            password_frame, 
            text="Password:", 
            bg="#2C3E50", 
            fg="#ECF0F1",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(
            password_frame, 
            bg="#34495E", 
            fg="#ECF0F1", 
            show="*",
            font=("Arial", 11),
            insertbackground="#ECF0F1",
            relief="flat",
            bd=10
        )
        self.password_entry.pack(fill="x", ipady=8)

        # Login button
        login_button = tk.Button(
            main_frame, 
            text="Login", 
            command=self.login, 
            bg="#3498DB", 
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#2980B9"
        )
        login_button.pack(fill="x", pady=(20, 0), ipady=10)

        # Bind Enter key events
        self.username_entry.bind("<Return>", self.focus_password_entry)
        self.password_entry.bind("<Return>", self.login)
        
        # Focus on username entry
        self.username_entry.focus()

    def focus_password_entry(self, event=None):
        self.password_entry.focus()

    def login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return

        try:
            user_data = self.parent.user_manager.authenticate(username, password)

            if user_data:
                self.parent.set_user(
                    user_data["username"], user_data["role"], user_data["id"]
                )
                self.destroy()
                self.parent.deiconify()
            else:
                messagebox.showerror("Error", "Invalid username or password!")
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")


class Sidebar(tk.Frame):
    """A sidebar that contains buttons to switch between different frames."""

    def __init__(self, parent, role):
        super().__init__(parent, width=250, bg="#34495E")
        self.parent = parent
        self.role = role
        self.create_widgets()

    def create_widgets(self):
        # User info section
        user_frame = tk.Frame(self, bg="#34495E", pady=20)
        user_frame.pack(fill="x")

        username_label = tk.Label(
            user_frame, 
            text=f"Welcome, {self.parent.user_name}", 
            bg="#34495E", 
            fg="#ECF0F1",
            font=("Arial", 12, "bold")
        )
        username_label.pack()

        role_label = tk.Label(
            user_frame, 
            text=f"Role: {self.role.replace('_', ' ').title()}", 
            bg="#34495E", 
            fg="#BDC3C7",
            font=("Arial", 10)
        )
        role_label.pack(pady=(5, 0))

        # Separator
        separator = tk.Frame(self, height=1, bg="#BDC3C7")
        separator.pack(fill="x", padx=20, pady=10)

        # Navigation buttons
        self.create_navigation_buttons()

    def create_navigation_buttons(self):
        buttons = []
        
        # Common buttons for all roles
        buttons.append(("🏠 Dashboard", self.show_main))
        
        # Role-specific buttons
        if self.role == "accountant":
            buttons.extend([
                ("📊 Financial Reports", self.show_frame_1),
                ("💰 Revenue Analysis", self.show_frame_2),
                ("📋 Audit Logs", self.show_frame_3),
            ])
        elif self.role == "warehouse_worker":
            buttons.extend([
                ("📦 Inventory Management", self.show_frame_4),
                ("🚚 Stock Operations", self.show_frame_5),
            ])
        elif self.role == "admin":
            buttons.extend([
                ("📊 Financial Reports", self.show_frame_1),
                ("💰 Revenue Analysis", self.show_frame_2),
                ("📋 Audit Logs", self.show_frame_3),
                ("📦 Inventory Management", self.show_frame_4),
                ("🚚 Stock Operations", self.show_frame_5),
                ("⚙️ System Management", self.show_admin_frame_1),
                ("📈 Analytics & Reports", self.show_admin_frame_2),
            ])

        for text, command in buttons:
            btn = tk.Button(
                self, 
                text=text, 
                command=command,
                bg="#3498DB",
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                activebackground="#2980B9"
            )
            btn.pack(fill="x", padx=15, pady=5, ipady=8)

    def show_main(self, event=None):
        self.master.switch_frame(MainFrame)

    def show_frame_1(self):
        self.master.switch_frame(Frame1)

    def show_frame_2(self):
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


class Header(tk.Frame):
    def __init__(self, parent, toggle_callback, logout_callback):
        super().__init__(parent, bg="#2C3E50", height=60)
        self.parent = parent
        self.pack(side="top", fill="x")
        self.pack_propagate(False)
        self.create_widgets(toggle_callback, logout_callback)

    def create_widgets(self, toggle_callback, logout_callback):
        # Menu toggle button
        self.toggle_button = tk.Button(
            self, 
            text="☰", 
            command=toggle_callback,
            bg="#3498DB",
            fg="white",
            font=("Arial", 16, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#2980B9"
        )
        self.toggle_button.pack(side="left", padx=15, pady=15)

        # App title
        self.app_title = tk.Label(
            self, 
            text="Medicine Warehouse Management System", 
            font=("Arial", 18, "bold"), 
            bg="#2C3E50", 
            fg="#ECF0F1"
        )
        self.app_title.pack(side="left", expand=True, padx=20, pady=15)
        self.app_title.bind("<Button-1>", self.parent.sidebar.show_main)

        # Logout button
        self.logout_button = tk.Button(
            self, 
            text="Logout", 
            command=logout_callback,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground="#C0392B"
        )
        self.logout_button.pack(side="right", padx=15, pady=15)


class ResizableImageFrame(tk.Frame):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.pack_propagate(False)
        try:
            self.original_image = Image.open(image_path)
            self.image = ImageTk.PhotoImage(self.original_image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Create a placeholder colored rectangle
            self.original_image = Image.new('RGB', (400, 300), color='lightblue')
            self.image = ImageTk.PhotoImage(self.original_image)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        self.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        if event.width > 1 and event.height > 1:
            new_width = event.width
            new_height = event.height

            resized_image = self.original_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            self.image = ImageTk.PhotoImage(resized_image)

            self.canvas.itemconfig(self.image_id, image=self.image)
            self.canvas.config(width=new_width, height=new_height)


class MainFrame(tk.Frame):
    def __init__(self, parent):
        self.bg = "#ECF0F1"
        super().__init__(parent, bg=self.bg)
        self.create_widgets()

    def create_widgets(self):
        # Title section
        title_frame = tk.Frame(self, bg=self.bg, pady=30)
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="Welcome to Medicine Warehouse System",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg=self.bg,
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Efficient pharmacy management at your fingertips",
            font=("Arial", 14),
            fg="#7F8C8D",
            bg=self.bg,
        )
        subtitle_label.pack(pady=(10, 0))

        # Stats/Info cards
        self.create_info_cards()

        # Image gallery
        self.create_image_gallery()

    def create_info_cards(self):
        cards_frame = tk.Frame(self, bg=self.bg, pady=20)
        cards_frame.pack(fill="x", padx=50)

        # Sample cards with system stats
        cards = [
            ("Total Medicines", "125", "#3498DB"),
            ("Active Suppliers", "18", "#2ECC71"),
            ("Stock Alerts", "5", "#E74C3C"),
            ("Monthly Sales", "$45,280", "#F39C12")
        ]

        for i, (title, value, color) in enumerate(cards):
            card_frame = tk.Frame(cards_frame, bg=color, relief="flat", bd=0)
            card_frame.grid(row=0, column=i, padx=15, pady=10, sticky="ew")
            cards_frame.grid_columnconfigure(i, weight=1)

            value_label = tk.Label(
                card_frame,
                text=value,
                font=("Arial", 20, "bold"),
                fg="white",
                bg=color
            )
            value_label.pack(pady=(15, 5))

            title_label = tk.Label(
                card_frame,
                text=title,
                font=("Arial", 12),
                fg="white",
                bg=color
            )
            title_label.pack(pady=(0, 15))

    def create_image_gallery(self):
        gallery_frame = tk.Frame(self, bg=self.bg)
        gallery_frame.pack(expand=True, fill="both", padx=50, pady=20)

        images_paths = ["t1.jpeg", "t2.jpeg", "t3.jpeg", "t4.jpeg"]

        # Create 2x2 grid for images
        for i in range(2):
            for j in range(2):
                idx = i * 2 + j
                if idx < len(images_paths):
                    try:
                        image_frame = ResizableImageFrame(gallery_frame, images_paths[idx])
                        image_frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                    except Exception as e:
                        # Fallback: create a colored frame
                        fallback_frame = tk.Frame(gallery_frame, bg=f"#{300 + idx * 100:03x}")
                        fallback_frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                        tk.Label(
                            fallback_frame,
                            text=f"Image {idx + 1}",
                            font=("Arial", 16),
                            bg=fallback_frame['bg']
                        ).pack(expand=True)

        # Configure grid weights
        for i in range(2):
            gallery_frame.grid_rowconfigure(i, weight=1)
            gallery_frame.grid_columnconfigure(i, weight=1)


class Frame1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#E8F6F3")
        self.create_content("Financial Reports", "📊", "View and analyze financial data")

    def create_content(self, title, icon, description):
        container = tk.Frame(self, bg=self['bg'])
        container.pack(expand=True, fill="both")

        icon_label = tk.Label(
            container, text=icon, font=("Arial", 48), bg=self['bg'], fg="#2C3E50"
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            container, text=title, font=("Arial", 24, "bold"), bg=self['bg'], fg="#2C3E50"
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            container, text=description, font=("Arial", 14), bg=self['bg'], fg="#7F8C8D"
        )
        desc_label.pack(pady=10)


class Frame2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#E8F8F5")
        self.create_content("Revenue Analysis", "💰", "Track revenue trends and patterns")

    def create_content(self, title, icon, description):
        container = tk.Frame(self, bg=self['bg'])
        container.pack(expand=True, fill="both")

        icon_label = tk.Label(
            container, text=icon, font=("Arial", 48), bg=self['bg'], fg="#2C3E50"
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            container, text=title, font=("Arial", 24, "bold"), bg=self['bg'], fg="#2C3E50"
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            container, text=description, font=("Arial", 14), bg=self['bg'], fg="#7F8C8D"
        )
        desc_label.pack(pady=10)


class Frame3(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#FDF2E9")
        self.create_content("Audit Logs", "📋", "Review system activities and changes")

    def create_content(self, title, icon, description):
        container = tk.Frame(self, bg=self['bg'])
        container.pack(expand=True, fill="both")

        icon_label = tk.Label(
            container, text=icon, font=("Arial", 48), bg=self['bg'], fg="#2C3E50"
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            container, text=title, font=("Arial", 24, "bold"), bg=self['bg'], fg="#2C3E50"
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            container, text=description, font=("Arial", 14), bg=self['bg'], fg="#7F8C8D"
        )
        desc_label.pack(pady=10)


class Frame4(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#EBF5FB")
        self.create_content("Inventory Management", "📦", "Manage stock levels and inventory")

    def create_content(self, title, icon, description):
        container = tk.Frame(self, bg=self['bg'])
        container.pack(expand=True, fill="both")

        icon_label = tk.Label(
            container, text=icon, font=("Arial", 48), bg=self['bg'], fg="#2C3E50"
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            container, text=title, font=("Arial", 24, "bold"), bg=self['bg'], fg="#2C3E50"
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            container, text=description, font=("Arial", 14), bg=self['bg'], fg="#7F8C8D"
        )
        desc_label.pack(pady=10)


class Frame5(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F4F6F6")
        self.create_content("Stock Operations", "🚚", "Handle stock movements and transfers")

    def create_content(self, title, icon, description):
        container = tk.Frame(self, bg=self['bg'])
        container.pack(expand=True, fill="both")

        icon_label = tk.Label(
            container, text=icon, font=("Arial", 48), bg=self['bg'], fg="#2C3E50"
        )
        icon_label.pack(pady=(50, 20))

        title_label = tk.Label(
            container, text=title, font=("Arial", 24, "bold"), bg=self['bg'], fg="#2C3E50"
        )
        title_label.pack(pady=10)

        desc_label = tk.Label(
            container, text=description, font=("Arial", 14), bg=self['bg'], fg="#7F8C8D"
        )
        desc_label.pack(pady=10)


class AdminFrame1(tk.Frame):
    def __init__(self, parent):
        self.bg = "#F8F9FA"
        super().__init__(parent, bg=self.bg)
        self.parent = parent
        self.supplier_id = None
        self.medicine_id = None
        self.create_scrollable_widgets()

    def create_scrollable_widgets(self):
        # Create main canvas and scrollbar
        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg)

        # Configure canvas scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
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
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_content(self):
        # Title
        title_label = tk.Label(
            self.scrollable_frame,
            text="System Management",
            font=("Arial", 20, "bold"),
            fg="#2C3E50",
            bg=self.bg,
        )
        title_label.pack(pady=20)

        # Main container with grid layout
        main_container = tk.Frame(self.scrollable_frame, bg=self.bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure grid weights for responsive layout
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Create sections
        self.create_medicine_section(main_container)
        self.create_user_section(main_container)
        self.create_supplier_section(main_container)
        self.create_stock_section(main_container)

        # Load initial data
        self.load_suppliers()
        self.load_medicines()

    def create_medicine_section(self, parent):
        # Medicine frame - Top Left
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

        # Configure internal grid
        medicine_frame.grid_columnconfigure(1, weight=1)

        # Medicine form fields
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

        tk.Label(medicine_frame, text="Supplier:", bg=self.bg, fg="#2C3E50").grid(
            row=3, column=0, padx=10, pady=5, sticky="e"
        )
        self.supplier_var = tk.StringVar()
        self.supplier_menu = ttk.Combobox(
            medicine_frame, textvariable=self.supplier_var, width=27, font=("Arial", 10)
        )
        self.supplier_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_menu.bind("<<ComboboxSelected>>", self.on_supplier_selected)

        # Medicine buttons
        button_frame = tk.Frame(medicine_frame, bg=self.bg)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)

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

    def create_user_section(self, parent):
        # User frame - Top Right
        user_frame = tk.LabelFrame(
            parent,
            text="User Management",
            font=("Arial", 14, "bold"),
            bg=self.bg,
            fg="#2C3E50",
            relief="solid",
            bd=1,
        )
        user_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Configure internal grid
        user_frame.grid_columnconfigure(1, weight=1)

        # User form fields
        tk.Label(user_frame, text="Username:", bg=self.bg, fg="#2C3E50").grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.username_entry = tk.Entry(user_frame, width=30, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(user_frame, text="Password:", bg=self.bg, fg="#2C3E50").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.password_entry = tk.Entry(user_frame, show="*", width=30, font=("Arial", 10))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(user_frame, text="Role:", bg=self.bg, fg="#2C3E50").grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.role_var = tk.StringVar(value="admin")
        role_dropdown = ttk.Combobox(
            user_frame, 
            textvariable=self.role_var, 
            values=["admin", "warehouse_worker", "accountant"],
            state="readonly",
            width=27,
            font=("Arial", 10)
        )
        role_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(user_frame, text="Full Name:", bg=self.bg, fg="#2C3E50").grid(
            row=3, column=0, padx=10, pady=5, sticky="e"
        )
        self.full_name_entry = tk.Entry(user_frame, width=30, font=("Arial", 10))
        self.full_name_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")