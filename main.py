import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from database_new_Architecture import Database, User, Medicine, Supplier, Reports
from datetime import date, datetime
import calendar



class ActivityMonitor:
    """Monitor user activity and handle automatic logout after inactivity"""
    
    def __init__(self, parent, timeout_minutes=10):
        self.parent = parent
        self.timeout_minutes = timeout_minutes
        self.timeout_ms = timeout_minutes * 60 * 100 # ms
        self.last_activity = datetime.now()
        self.warning_shown = False
        self.logout_job = None
        self.warning_job = None
        self.check_job = None
        self.is_active = False
        
        self.activity_events = [
            '<Motion>', '<Button-1>', '<Button-2>', '<Button-3>', 
            '<Key>', '<KeyPress>', '<KeyRelease>', '<FocusIn>', 
            '<MouseWheel>', '<Button-4>', '<Button-5>'
        ]
        
    def start_monitoring(self):
        """Start monitoring user activity"""
        self.is_active = True
        self.reset_timer()
        self.bind_activity_events()
        self.schedule_activity_check()
        
    def stop_monitoring(self):
        """Stop monitoring user activity"""
        self.is_active = False
        self.cancel_all_jobs()
        self.unbind_activity_events()
        
    def bind_activity_events(self):
        """Bind activity events to the main window and all child widgets"""
        def bind_recursive(widget):
            for event in self.activity_events:
                widget.bind(event, self.on_activity, add=True)
            
            for child in widget.winfo_children():
                bind_recursive(child)
        
        bind_recursive(self.parent)
        
    def unbind_activity_events(self):
        """Unbind activity events from all widgets"""
        def unbind_recursive(widget):
            for event in self.activity_events:
                try:
                    widget.unbind(event)
                except:
                    pass
            
            for child in widget.winfo_children():
                unbind_recursive(child)
        
        unbind_recursive(self.parent)
        
    def on_activity(self, event=None):
        """Handle user activity"""
        if not self.is_active:
            return
            
        self.last_activity = datetime.now()
        self.warning_shown = False
        
        self.cancel_all_jobs()
        self.reset_timer()
        
    def reset_timer(self):
        """Reset the inactivity timer"""
        warning_time = max(1, (self.timeout_minutes - 2) * 60 * 1000)
        self.warning_job = self.parent.after(warning_time, self.show_warning)
        
        self.logout_job = self.parent.after(self.timeout_ms, self.auto_logout)
        
    def schedule_activity_check(self):
        """Schedule periodic activity checks"""
        if self.is_active:
            self.check_activity()
            self.check_job = self.parent.after(30000, self.schedule_activity_check)
            
    def check_activity(self):
        """Check if user has been inactive for too long"""
        if not self.is_active:
            return
            
        time_since_activity = (datetime.now() - self.last_activity).total_seconds()
        
        if time_since_activity >= (self.timeout_minutes * 60):
            self.auto_logout()
        elif time_since_activity >= ((self.timeout_minutes - 2) * 60) and not self.warning_shown:
            self.show_warning()
            
    def show_warning(self):
        """Show inactivity warning dialog"""
        if not self.is_active or self.warning_shown:
            return
            
        self.warning_shown = True
        
        warning_window = tk.Toplevel(self.parent)
        warning_window.title("Session Timeout Warning")
        warning_window.geometry("400x200")
        warning_window.resizable(False, False)
        warning_window.grab_set()
        warning_window.focus_force()
        
        warning_window.update_idletasks()
        x = (warning_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (warning_window.winfo_screenheight() // 2) - (200 // 2)
        warning_window.geometry(f'400x200+{x}+{y}')
        
        warning_window.configure(bg="#2C3E50")
        
        main_frame = tk.Frame(warning_window, bg="#2C3E50", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        warning_label = tk.Label(
            main_frame,
            text="⚠️ Session Timeout Warning",
            font=("Arial", 16, "bold"),
            bg="#2C3E50",
            fg="#E74C3C"
        )
        warning_label.pack(pady=(0, 10))
        
        message_label = tk.Label(
            main_frame,
            text="You will be logged out in 2 minutes due to inactivity.\nClick 'Stay Logged In' to continue your session.",
            font=("Arial", 12),
            bg="#2C3E50",
            fg="#ECF0F1",
            justify="center"
        )
        message_label.pack(pady=10)
        
        button_frame = tk.Frame(main_frame, bg="#2C3E50")
        button_frame.pack(pady=20)
        
        def stay_logged_in():
            self.on_activity() 
            warning_window.destroy()
            
        def logout_now():
            warning_window.destroy()
            self.auto_logout()
            
        stay_button = tk.Button(
            button_frame,
            text="Stay Logged In",
            command=stay_logged_in,
            bg="#27AE60",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        stay_button.pack(side="left", padx=10)
        
        logout_button = tk.Button(
            button_frame,
            text="Logout Now",
            command=logout_now,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        logout_button.pack(side="left", padx=10)
        
        warning_window.after(120000, lambda: warning_window.destroy() if warning_window.winfo_exists() else None)
        
    def auto_logout(self):
        """Automatically logout the user"""
        if not self.is_active:
            return
            
        self.stop_monitoring()
        
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "Session Expired", 
                f"You have been logged out due to {self.timeout_minutes} minutes of inactivity."
            )
        except:
            pass
        
        self.parent.logout()
        
    def cancel_all_jobs(self):
        """Cancel all scheduled jobs"""
        if self.logout_job:
            self.parent.after_cancel(self.logout_job)
            self.logout_job = None
            
        if self.warning_job:
            self.parent.after_cancel(self.warning_job)
            self.warning_job = None
            
        if self.check_job:
            self.parent.after_cancel(self.check_job)
            self.check_job = None


class LoginWindow(tk.Toplevel):
    """A simple login window that prompts for username and password."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.withdraw()
        self.title("Login - Medicine Warehouse System")
        self.geometry("400x500")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
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
        main_frame = tk.Frame(self, bg="#2C3E50", padx=40, pady=30)
        main_frame.pack(fill="both", expand=True)
        title_label = tk.Label(
            main_frame, 
            text="Medicine Warehouse System", 
            font=("Arial", 16, "bold"), 
            bg="#2C3E50", 
            fg="#ECF0F1"
        )
        title_label.pack(pady=(0, 20))
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

        self.username_entry.bind("<Return>", self.focus_password_entry)
        self.password_entry.bind("<Return>", self.login)
        
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
    def __init__(self, parent):
        super().__init__(parent, width=250, bg="#34495E")
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
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
            text=f"Role: {self.parent.user_role.replace('_', ' ').title()}", 
            bg="#34495E", 
            fg="#BDC3C7",
            font=("Arial", 10)
        )
        role_label.pack(pady=(5, 0))

        separator = tk.Frame(self, height=1, bg="#BDC3C7")
        separator.pack(fill="x", padx=20, pady=10)

        self.create_navigation_buttons()

    def show_Dashboard(self, event=None):
        self.update_button_colors(0)
        self.master.switch_frame(Dashboard)

    def show_Financial_Reports(self):
        self.update_button_colors(1)
        self.master.switch_frame(Financial_Reports)

    def show_Revenue_Analysis(self):
        self.update_button_colors(2)
        self.master.switch_frame(Revenue_Analysis)

    def show_Audit_Logs(self):
        self.update_button_colors(3)
        self.master.switch_frame(Audit_Logs)

    def show_Inventory_Management(self):
        self.update_button_colors(4)
        self.master.switch_frame(Inventory_Management)

    def show_Stock_Operations(self):
        self.update_button_colors(5)
        self.master.switch_frame(Stock_Operations)

    def show_System_Management(self):
        self.update_button_colors(6)
        self.master.switch_frame(System_Management)

    def show_Analytics_and_Reports(self):
        self.update_button_colors(7)
        self.master.switch_frame(Analytics_and_Reports)

    def update_button_colors(self, active_index):
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.config(bg="#00568F")
            else:
                btn.config(bg="#3498DB")

    def create_navigation_buttons(self):
        buttons = []
        self.nav_buttons = []
        
        buttons.append(("🏠 Dashboard", self.show_Dashboard))
        
        if self.parent.user_role == "accountant":
            buttons.extend([
                ("📊 Financial Reports", self.show_Financial_Reports),
                ("💰 Revenue Analysis", self.show_Revenue_Analysis),
                ("📋 Audit Logs", self.show_Audit_Logs),
            ])
        elif self.parent.user_role == "warehouse_worker":
            buttons.extend([
                ("📦 Inventory Management", self.show_Inventory_Management),
                ("🚚 Stock Operations", self.show_Stock_Operations),
            ])
        elif self.parent.user_role == "admin":
            buttons.extend([
                ("📊 Financial Reports", self.show_Financial_Reports),
                ("💰 Revenue Analysis", self.show_Revenue_Analysis),
                ("📋 Audit Logs", self.show_Audit_Logs),
                ("📦 Inventory Management", self.show_Inventory_Management),
                ("🚚 Stock Operations", self.show_Stock_Operations),
                ("⚙️ System Management", self.show_System_Management),
                ("📈 Analytics & Reports", self.show_Analytics_and_Reports),
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
            self.nav_buttons.append(btn)
            btn.pack(fill="x", padx=15, pady=5, ipady=8)
        self.update_button_colors(0)


class Header(tk.Frame):
    """ """
    def __init__(self, parent, toggle_callback, logout_callback):
        super().__init__(parent, bg="#2C3E50", height=60)
        self.parent = parent
        self.pack(side="top", fill="x")
        self.pack_propagate(False)
        self.create_widgets(toggle_callback, logout_callback)

    def create_widgets(self, toggle_callback, logout_callback):
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

        self.app_title = tk.Label(
            self, 
            text="Elethat Company System", 
            font=("Arial", 18, "bold"), 
            bg="#2C3E50", 
            fg="#ECF0F1"
        )
        self.app_title.pack(side="left", expand=True, padx=20, pady=15)
        self.app_title.bind("<Button-1>", self.parent.sidebar.show_Dashboard)

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
    """ """
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.pack_propagate(False)
        try:
            self.original_image = Image.open(image_path)
            self.image = ImageTk.PhotoImage(self.original_image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
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


class Dashboard(tk.Frame):
    """ """
    def __init__(self, box, parent):
        self.bg = "#ECF0F1"
        super().__init__(box, bg=self.bg)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        title_frame = tk.Frame(self, bg=self.bg, pady=30)
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="Welcome to Elethat Company System",
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

        self.create_info_cards()

        self.create_image_gallery()

    def create_info_cards(self):
        cards_frame = tk.Frame(self, bg=self.bg, pady=20)
        cards_frame.pack(fill="x", padx=50)
        total_med = self.parent.medicine_manager.get_medicine_count()
        active_supp = self.parent.supplier_manager.get_supplier_count()
        low_stock = len(self.parent.medicine_manager.get_low_stock_medicines())
        monthly_sales = self.parent.reports.get_total_monthly_sales_report(date.today().month,date.today().year)

        cards = [
            ("Total Medicines", total_med, "#3498DB"),
            ("Active Suppliers", active_supp, "#2ECC71"),
            ("Stock Alerts", low_stock, "#E74C3C"),
            ("Monthly Sales", monthly_sales, "#F39C12")
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
        """
        images_paths = ["t1.jpeg", "t2.jpeg", "t3.jpeg", "t4.jpeg"]
        images_paths = ["t1.jpeg"]


        for i in range(2):
            for j in range(2):
                idx = i * 2 + j
                if idx < len(images_paths):
                    try:
                        image_frame = ResizableImageFrame(gallery_frame, images_paths[idx])
                        image_frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                    except Exception as e:
                        fallback_frame = tk.Frame(gallery_frame, bg=f"#{300 + idx * 100:03x}")
                        fallback_frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                        tk.Label(
                            fallback_frame,
                            text=f"Image {idx + 1}",
                            font=("Arial", 16),
                            bg=fallback_frame['bg']
                        ).pack(expand=True)
      
        

        for i in range(2):
            gallery_frame.grid_rowconfigure(i, weight=1)
            gallery_frame.grid_columnconfigure(i, weight=1)
      """
        # single image =>> الاربع صور وحشة بعد التعديلات الجديدة فخليتها واحدة
        # single image =>> كود الاربعة فوق عموما لو حبيت ارجعله
        try:
            image_frame = ResizableImageFrame(gallery_frame, "t1.jpeg")
            image_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        except Exception as e:
            fallback_frame = tk.Frame(gallery_frame, bg="#3498db")
            fallback_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            tk.Label(
               fallback_frame,
               text="Main Image",
               font=("Arial", 16),
               bg=fallback_frame['bg']
            ).pack(expand=True)

        gallery_frame.grid_columnconfigure(0, weight=1)
        gallery_frame.grid_rowconfigure(0, weight=1)










class Financial_Reports(tk.Frame):
    """ """
    def __init__(self, box, parent):
        self.bg = "#E8F6F3"
        super().__init__(box, bg=self.bg)
        self.parent = parent
        self.create_scrollable_widgets()

    def create_scrollable_widgets(self):
        """Create scrollable content area"""

        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.bind_all("<MouseWheel>", self.on_mousewheel)

        self.create_content()

    def on_canvas_configure(self, event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_content(self):
        """Create the main content for financial reports"""
        # Title Section
        title_frame = tk.Frame(self.scrollable_frame, bg=self.bg, pady=20)
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="📊 Financial Reports",
            font=("Arial", 24, "bold"),
            fg="#2C3E50",
            bg=self.bg,
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Comprehensive financial analysis and reporting dashboard",
            font=("Arial", 12),
            fg="#7F8C8D",
            bg=self.bg,
        )
        subtitle_label.pack(pady=(5, 0))

        # Create notebook for different report types
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        self.create_summary_tab()
        self.create_sales_tab()
        self.create_purchase_tab()
        self.create_inventory_tab()
        self.create_profit_loss_tab()

    def create_summary_tab(self):
        """Create financial summary tab"""
        summary_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(summary_frame, text="Summary")

        # Control panel
        control_panel = tk.Frame(summary_frame, bg="#F8F9FA", relief="solid", bd=1)
        control_panel.pack(fill="x", padx=10, pady=10)

        tk.Label(
            control_panel,
            text="Financial Summary Dashboard",
            font=("Arial", 14, "bold"),
            bg="#F8F9FA",
            fg="#2C3E50"
        ).pack(pady=10)

        # Date range selection
        date_frame = tk.Frame(control_panel, bg="#F8F9FA")
        date_frame.pack(pady=10)

        tk.Label(date_frame, text="From:", bg="#F8F9FA", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5)
        self.summary_start_date = DateEntry(
            date_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.summary_start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(date_frame, text="To:", bg="#F8F9FA", fg="#2C3E50").grid(row=0, column=2, padx=5, pady=5)
        self.summary_end_date = DateEntry(
            date_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.summary_end_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            date_frame,
            text="Generate Summary",
            command=self.generate_financial_summary,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=0, column=4, padx=10, pady=5)

        # Summary cards container
        self.summary_cards_frame = tk.Frame(summary_frame, bg="#FFFFFF")
        self.summary_cards_frame.pack(fill="x", padx=20, pady=20)

        # Summary text area
        text_frame = tk.Frame(summary_frame, bg="#FFFFFF")
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.summary_text = tk.Text(
            text_frame,
            height=15,
            font=("Courier", 10),
            bg="#F8F9FA",
            fg="#2C3E50",
            yscrollcommand=scrollbar.set
        )
        self.summary_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.summary_text.yview)

    def create_sales_tab(self):
        """Create sales report tab"""
        sales_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(sales_frame, text="Sales Reports")

        # Control panel
        control_panel = tk.Frame(sales_frame, bg="#E8F8F5", relief="solid", bd=1)
        control_panel.pack(fill="x", padx=10, pady=10)

        tk.Label(
            control_panel,
            text="Sales Analysis & Reports",
            font=("Arial", 14, "bold"),
            bg="#E8F8F5",
            fg="#2C3E50"
        ).pack(pady=10)

        # Filters
        filter_frame = tk.Frame(control_panel, bg="#E8F8F5")
        filter_frame.pack(pady=10)

        # Period selection
        tk.Label(filter_frame, text="Period:", bg="#E8F8F5", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5)
        self.sales_period_var = tk.StringVar(value="monthly")
        period_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sales_period_var,
            values=["daily", "weekly", "monthly", "quarterly", "yearly"],
            state="readonly",
            width=10
        )
        period_combo.grid(row=0, column=1, padx=5, pady=5)

        # Date range
        tk.Label(filter_frame, text="From:", bg="#E8F8F5", fg="#2C3E50").grid(row=0, column=2, padx=5, pady=5)
        self.sales_start_date = DateEntry(
            filter_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.sales_start_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="To:", bg="#E8F8F5", fg="#2C3E50").grid(row=0, column=4, padx=5, pady=5)
        self.sales_end_date = DateEntry(
            filter_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.sales_end_date.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(
            filter_frame,
            text="Generate Sales Report",
            command=self.generate_sales_report,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=0, column=6, padx=10, pady=5)

        # Sales data table
        table_frame = tk.Frame(sales_frame, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Date", "Medicine", "Quantity", "Unit Price", "Total", "Profit")
        self.sales_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.sales_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.sales_tree.xview)
        
        self.sales_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.sales_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def create_purchase_tab(self):
        """Create purchase report tab"""
        purchase_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(purchase_frame, text="Purchase Reports")

        # Control panel
        control_panel = tk.Frame(purchase_frame, bg="#FDF2E9", relief="solid", bd=1)
        control_panel.pack(fill="x", padx=10, pady=10)

        tk.Label(
            control_panel,
            text="Purchase Analysis & Reports",
            font=("Arial", 14, "bold"),
            bg="#FDF2E9",
            fg="#2C3E50"
        ).pack(pady=10)

        # Filters
        filter_frame = tk.Frame(control_panel, bg="#FDF2E9")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Supplier:", bg="#FDF2E9", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5)
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.supplier_var,
            width=15
        )
        self.supplier_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="From:", bg="#FDF2E9", fg="#2C3E50").grid(row=0, column=2, padx=5, pady=5)
        self.purchase_start_date = DateEntry(
            filter_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.purchase_start_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="To:", bg="#FDF2E9", fg="#2C3E50").grid(row=0, column=4, padx=5, pady=5)
        self.purchase_end_date = DateEntry(
            filter_frame, width=12, background='darkblue',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.purchase_end_date.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(
            filter_frame,
            text="Generate Purchase Report",
            command=self.generate_purchase_report,
            bg="#E67E22",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=0, column=6, padx=10, pady=5)

        # Purchase data table
        table_frame = tk.Frame(purchase_frame, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Date", "Supplier", "Medicine", "Quantity", "Unit Cost", "Total Cost")
        self.purchase_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=120, anchor="center")

        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.purchase_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.purchase_tree.xview)
        
        self.purchase_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.purchase_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def create_inventory_tab(self):
        """Create inventory valuation tab"""
        inventory_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(inventory_frame, text="Inventory Valuation")

        # Control panel
        control_panel = tk.Frame(inventory_frame, bg="#EBF5FB", relief="solid", bd=1)
        control_panel.pack(fill="x", padx=10, pady=10)

        tk.Label(
            control_panel,
            text="Inventory Valuation & Analysis",
            font=("Arial", 14, "bold"),
            bg="#EBF5FB",
            fg="#2C3E50"
        ).pack(pady=10)

        button_frame = tk.Frame(control_panel, bg="#EBF5FB")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Current Inventory Value",
            command=self.generate_inventory_valuation,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Low Stock Alert",
            command=self.generate_low_stock_report,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Expiry Alert",
            command=self.generate_expiry_report,
            bg="#F39C12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        # Inventory data table
        table_frame = tk.Frame(inventory_frame, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = ("Medicine", "Batch", "Quantity", "Unit Price", "Total Value", "Expiry Date", "Status")
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100, anchor="center")

        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.inventory_tree.xview)
        
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def create_profit_loss_tab(self):
        """Create profit & loss statement tab"""
        pl_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(pl_frame, text="Profit & Loss")

        # Control panel
        control_panel = tk.Frame(pl_frame, bg="#F4F6F6", relief="solid", bd=1)
        control_panel.pack(fill="x", padx=10, pady=10)

        tk.Label(
            control_panel,
            text="Profit & Loss Statement",
            font=("Arial", 14, "bold"),
            bg="#F4F6F6",
            fg="#2C3E50"
        ).pack(pady=10)

        # Period selection
        period_frame = tk.Frame(control_panel, bg="#F4F6F6")
        period_frame.pack(pady=10)

        tk.Label(period_frame, text="Period:", bg="#F4F6F6", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5)
        self.pl_period_var = tk.StringVar(value="monthly")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.pl_period_var,
            values=["monthly", "quarterly", "yearly"],
            state="readonly",
            width=10
        )
        period_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(period_frame, text="Year:", bg="#F4F6F6", fg="#2C3E50").grid(row=0, column=2, padx=5, pady=5)
        current_year = datetime.now().year
        self.pl_year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(
            period_frame,
            textvariable=self.pl_year_var,
            values=[str(year) for year in range(current_year-5, current_year+2)],
            state="readonly",
            width=8
        )
        year_combo.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            period_frame,
            text="Generate P&L Statement",
            command=self.generate_pl_statement,
            bg="#8E44AD",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).grid(row=0, column=4, padx=10, pady=5)

        # P&L statement display
        pl_text_frame = tk.Frame(pl_frame, bg="#FFFFFF")
        pl_text_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = ttk.Scrollbar(pl_text_frame)
        scrollbar.pack(side="right", fill="y")

        self.pl_text = tk.Text(
            pl_text_frame,
            height=20,
            font=("Courier", 11),
            bg="#F8F9FA",
            fg="#2C3E50",
            yscrollcommand=scrollbar.set
        )
        self.pl_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.pl_text.yview)

    def generate_financial_summary(self):
        """Generate comprehensive financial summary"""
        try:
            start_date = self.summary_start_date.get()
            end_date = self.summary_end_date.get()
            
            # Clear existing content
            for widget in self.summary_cards_frame.winfo_children():
                widget.destroy()
            self.summary_text.delete(1.0, tk.END)
            
            # Generate summary data (placeholder - replace with actual database queries)
            total_sales = 15750.00  # Replace with actual query
            total_purchases = 12300.00  # Replace with actual query
            gross_profit = total_sales - total_purchases
            profit_margin = (gross_profit / total_sales) * 100 if total_sales > 0 else 0
            
            # Create summary cards
            cards_data = [
                ("Total Sales", f"${total_sales:,.2f}", "#27AE60"),
                ("Total Purchases", f"${total_purchases:,.2f}", "#E74C3C"),
                ("Gross Profit", f"${gross_profit:,.2f}", "#3498DB"),
                ("Profit Margin", f"{profit_margin:.1f}%", "#9B59B6")
            ]
            
            for i, (title, value, color) in enumerate(cards_data):
                card = tk.Frame(self.summary_cards_frame, bg=color, relief="flat", bd=0)
                card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
                self.summary_cards_frame.grid_columnconfigure(i, weight=1)
                
                tk.Label(
                    card, text=value, font=("Arial", 18, "bold"),
                    fg="white", bg=color
                ).pack(pady=(15, 5))
                
                tk.Label(
                    card, text=title, font=("Arial", 11),
                    fg="white", bg=color
                ).pack(pady=(0, 15))
            
            # Generate detailed text summary
            summary_text = f"""
                FINANCIAL SUMMARY REPORT
                Period: {start_date} to {end_date}
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                {'='*60}

                REVENUE OVERVIEW:
                • Total Sales Revenue: ${total_sales:,.2f}
                • Average Daily Sales: ${total_sales/30:,.2f}
                • Number of Transactions: 145
                • Average Transaction Value: ${total_sales/145:,.2f}

                COST ANALYSIS:
                • Total Purchase Costs: ${total_purchases:,.2f}
                • Cost of Goods Sold: ${total_purchases:,.2f}
                • Gross Profit: ${gross_profit:,.2f}
                • Gross Profit Margin: {profit_margin:.1f}%

                INVENTORY METRICS:
                • Current Inventory Value: $8,450.00
                • Inventory Turnover: 2.3x
                • Days in Inventory: 159 days
                • Stock-out Events: 3

                TOP PERFORMING PRODUCTS:
                1. Paracetamol 500mg - $2,350.00 (15% of sales)
                2. Amoxicillin 250mg - $1,890.00 (12% of sales)
                3. Ibuprofen 400mg - $1,640.00 (10% of sales)

                FINANCIAL HEALTH INDICATORS:
                • Current Ratio: 2.4:1 (Good)
                • Quick Ratio: 1.8:1 (Adequate)
                • Working Capital: $12,450.00
                • Cash Flow: Positive

                RECOMMENDATIONS:
                • Focus on high-margin products
                • Optimize inventory levels for slow-moving items
                • Consider bulk purchasing for top sellers
                • Review pricing strategy for competitive positioning
            """
            
            self.summary_text.insert(1.0, summary_text)
            messagebox.showinfo("Success", "Financial summary generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {str(e)}")

    def generate_sales_report(self):
        """Generate sales report"""
        try:
            # Clear existing data
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            # Sample data (replace with actual database queries)
            sales_data = [
                ("2024-01-15", "Paracetamol 500mg", 50, 2.50, 125.00, 37.50),
                ("2024-01-16", "Amoxicillin 250mg", 30, 4.20, 126.00, 45.00),
                ("2024-01-17", "Ibuprofen 400mg", 25, 3.80, 95.00, 28.50),
                ("2024-01-18", "Vitamin C 1000mg", 40, 1.95, 78.00, 23.40),
                ("2024-01-19", "Aspirin 325mg", 35, 2.10, 73.50, 22.05)
            ]
            
            total_sales = 0
            total_profit = 0
            
            for sale in sales_data:
                self.sales_tree.insert("", "end", values=sale)
                total_sales += sale[4]
                total_profit += sale[5]
            
            # Add totals row
            self.sales_tree.insert("", "end", values=(
                "TOTAL", "", "", "", f"${total_sales:.2f}", f"${total_profit:.2f}"
            ), tags=("total",))
            
            # Configure total row appearance
            self.sales_tree.tag_configure("total", background="#E8F6F3", font=("Arial", 10, "bold"))
            
            messagebox.showinfo("Success", f"Sales report generated! Total Sales: ${total_sales:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sales report: {str(e)}")

    def generate_purchase_report(self):
        """Generate purchase report"""
        try:
            # Clear existing data
            for item in self.purchase_tree.get_children():
                self.purchase_tree.delete(item)
            
            # Sample data (replace with actual database queries)
            purchase_data = [
                ("2024-01-10", "PharmaCorp", "Paracetamol 500mg", 100, 1.50, 150.00),
                ("2024-01-11", "MediSupply", "Amoxicillin 250mg", 75, 2.80, 210.00),
                ("2024-01-12", "HealthDistributors", "Ibuprofen 400mg", 60, 2.50, 150.00),
                ("2024-01-13", "VitaWholesale", "Vitamin C 1000mg", 120, 1.30, 156.00),
                ("2024-01-14", "Generic Solutions", "Aspirin 325mg", 90, 1.40, 126.00)
            ]
            
            total_cost = 0
            
            for purchase in purchase_data:
                self.purchase_tree.insert("", "end", values=purchase)
                total_cost += purchase[5]
            
            # Add totals row
            self.purchase_tree.insert("", "end", values=(
                "TOTAL", "", "", "", "", f"${total_cost:.2f}"
            ), tags=("total",))
            
            self.purchase_tree.tag_configure("total", background="#FDF2E9", font=("Arial", 10, "bold"))
            
            messagebox.showinfo("Success", f"Purchase report generated! Total Cost: ${total_cost:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate purchase report: {str(e)}")

    def generate_inventory_valuation(self):
        messagebox.showinfo("clicked", "generate_inventory_valuation")

    def generate_low_stock_report(self):
        messagebox.showinfo("clicked", "generate_low_stock_report!")
    
    def generate_expiry_report(self):
        messagebox.showinfo("clicked", "generate_expiry_report!")

    def generate_pl_statement(self):
        """Generate profit & loss statement"""
        try:
            period = self.pl_period_var.get()
            year = self.pl_year_var.get()
            
            # Clear existing text
            self.pl_text.delete(1.0, tk.END)
            
            # Sample P&L data (replace with actual database queries)
            revenue = 50000.00
            cost_of_goods_sold = 30000.00
            operating_expenses = 10000.00
            net_income = revenue - cost_of_goods_sold - operating_expenses
            
            pl_statement = f"""
                PROFIT & LOSS STATEMENT
                Period: {period.capitalize()} {year}
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                {'='*60}

                REVENUE:
                • Total Revenue: ${revenue:,.2f}

                COST OF GOODS SOLD:
                • Cost of Goods Sold: ${cost_of_goods_sold:,.2f}
                • Gross Profit: ${revenue - cost_of_goods_sold:,.2f}

                OPERATING EXPENSES:
                • Total Operating Expenses: ${operating_expenses:,.2f}

                NET INCOME:
                • Net Income: ${net_income:,.2f}
            """
            
            self.pl_text.insert(1.0, pl_statement)
            messagebox.showinfo("Success", "Profit & Loss statement generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate P&L statement: {str(e)}")











class Revenue_Analysis(tk.Frame):
    """ """
    def __init__(self, box, parent):
        super().__init__(box, bg="#E8F8F5")
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


class Audit_Logs(tk.Frame):
    """ """
    def __init__(self, box, parent):
        super().__init__(box, bg="#FDF2E9")
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


class Inventory_Management(tk.Frame):
    """ """
    def __init__(self, box, parent):
        super().__init__(box, bg="#EBF5FB")
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


class Stock_Operations(tk.Frame):
    """ """
    def __init__(self, box, parent):
        super().__init__(box, bg="#F4F6F6")
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


class System_Management(tk.Frame):
    """ """
    def __init__(self, box, parent):
        self.bg = "#F8F9FA"
        super().__init__(box, bg=self.bg)
        self.parent = parent
        self.supplier_id = None
        self.medicine_id = None
        self.create_scrollable_widgets()

    def create_scrollable_widgets(self):

        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg)


        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.bind_all("<MouseWheel>", self.on_mousewheel)

        self.create_content()

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_content(self):
        title_label = tk.Label(
            self.scrollable_frame,
            text="System Management",
            font=("Arial", 20, "bold"),
            fg="#2C3E50",
            bg=self.bg,
        )
        title_label.pack(pady=20)


        main_container = tk.Frame(self.scrollable_frame, bg=self.bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # for example, if you want to add more sections later.
        # main_container.grid_rowconfigure(2, weight=1)
        # main_container.grid_rowconfigure(3, weight=1)
        self.create_medicine_section(main_container)
        self.create_user_section(main_container)
        self.create_supplier_section(main_container)
        self.create_stock_section(main_container)
        # don't forget to add this ^^^ code if you want to add more sections.
        # and create the respective methods for them mf.

        self.load_suppliers()
        self.load_medicines()

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
        self.medicine_name_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(medicine_frame, text="Description:", bg=self.bg, fg="#2C3E50").grid(
            row=1, column=0, padx=10, pady=5, sticky="ne"
        )
        self.description_entry = tk.Text(medicine_frame, height=4, width=30, font=("Arial", 10))
        self.description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.description_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(medicine_frame, text="Price:", bg=self.bg, fg="#2C3E50").grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.price_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
        self.price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.price_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(medicine_frame, text="Batch Number:", bg=self.bg, fg="#2C3E50").grid(
            row=3, column=0, padx=10, pady=5, sticky="e"
        )
        self.batch_number_entry = tk.Entry(medicine_frame, width=30, font=("Arial", 10))
        self.batch_number_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.batch_number_entry.bind("<Return>", self.focus_on_next_widget)
        

        tk.Label(medicine_frame, text="Expiry Date:", bg=self.bg, fg="#2C3E50").grid(
            row=4, column=0, padx=10, pady=5, sticky="e"
        )
        current_date = date.today()
        self.datevar = tk.StringVar(value=current_date)

        self.expiry_date_entry = DateEntry(
            medicine_frame,
            width=27,
            background='white',             
            foreground='black', 
            borderwidth=1,
            font=("Arial", 10),
            textvariable= self.datevar,
            date_pattern='YYYY-MM-DD',         
            mindate=date.today(),
            maxdate=date.today().replace(year=date.today().year + 10),
        )
        self.expiry_date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.expiry_date_entry.bind("<Return>", self.focus_on_next_widget)

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

    def create_user_section(self, parent):
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

        user_frame.grid_columnconfigure(1, weight=1)

        tk.Label(user_frame, text="Username:", bg=self.bg, fg="#2C3E50").grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.username_entry = tk.Entry(user_frame, width=30, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.username_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(user_frame, text="Password:", bg=self.bg, fg="#2C3E50").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.password_entry = tk.Entry(user_frame, show="*", width=30, font=("Arial", 10))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.password_entry.bind("<Return>", self.focus_on_next_widget)

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
        self.full_name_entry.bind("<Return>", self.focus_on_next_widget)
        tk.Label(user_frame, text="Email:", bg=self.bg, fg="#2C3E50").grid(
            row=4, column=0, padx=10, pady=5, sticky="e"
        )
        self.email_entry = tk.Entry(user_frame, width=30, font=("Arial", 10))
        self.email_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.email_entry.bind("<Return>", self.focus_on_next_widget)

        user_button_frame = tk.Frame(user_frame, bg=self.bg)
        user_button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(
            user_button_frame,
            text="Add User",
            command=self.add_user,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            user_button_frame,
            text="Clear Form",
            command=self.clear_user_form,
            bg="#F39C12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

    def create_supplier_section(self, parent):
        supplier_frame = tk.LabelFrame(
            parent,
            text="Supplier Management",
            font=("Arial", 14, "bold"),
            bg=self.bg,
            fg="#2C3E50",
            relief="solid",
            bd=1,
        )
        supplier_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        supplier_frame.grid_columnconfigure(1, weight=1)

        tk.Label(supplier_frame, text="Supplier Name:", bg=self.bg, fg="#2C3E50").grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.supplier_name_entry = tk.Entry(supplier_frame, width=30, font=("Arial", 10))
        self.supplier_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_name_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(supplier_frame, text="Email:", bg=self.bg, fg="#2C3E50").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.supplier_email_entry = tk.Entry(supplier_frame, width=30, font=("Arial", 10))
        self.supplier_email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_email_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(supplier_frame, text="Phone:", bg=self.bg, fg="#2C3E50").grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.supplier_phone_entry = tk.Entry(supplier_frame, width=30, font=("Arial", 10))
        self.supplier_phone_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_phone_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(supplier_frame, text="Address:", bg=self.bg, fg="#2C3E50").grid(
            row=3, column=0, padx=10, pady=5, sticky="ne"
        )
        self.supplier_address_entry = tk.Text(supplier_frame, height=3, width=30, font=("Arial", 10))
        self.supplier_address_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.supplier_address_entry.bind("<Return>", self.focus_on_next_widget)

        supplier_button_frame = tk.Frame(supplier_frame, bg=self.bg)
        supplier_button_frame.grid(row=4, column=0, columnspan=2, pady=15)

        tk.Button(
            supplier_button_frame,
            text="Add Supplier",
            command=self.add_supplier,
            bg="#9B59B6",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            supplier_button_frame,
            text="Clear Form",
            command=self.clear_supplier_form,
            bg="#F39C12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

    def create_stock_section(self, parent):
        stock_frame = tk.LabelFrame(
            parent,
            text="Stock Operations",
            font=("Arial", 14, "bold"),
            bg=self.bg,
            fg="#2C3E50",
            relief="solid",
            bd=1,
        )
        stock_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        stock_frame.grid_columnconfigure(1, weight=1)

        tk.Label(stock_frame, text="Medicine:", bg=self.bg, fg="#2C3E50").grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.medicine_var = tk.StringVar()
        self.medicine_menu = ttk.Combobox(
            stock_frame, textvariable=self.medicine_var, width=27, font=("Arial", 10)
        )
        self.medicine_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.medicine_menu.bind("<<ComboboxSelected>>", self.on_medicine_selected)
        tk.Label(stock_frame, text="Quantity:", bg=self.bg, fg="#2C3E50").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.quantity_entry = tk.Entry(stock_frame, width=30, font=("Arial", 10))
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.quantity_entry.bind("<Return>", self.focus_on_next_widget)

        tk.Label(stock_frame, text="Operation:", bg=self.bg, fg="#2C3E50").grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.operation_var = tk.StringVar(value="incoming")
        operation_dropdown = ttk.Combobox(
            stock_frame, 
            textvariable=self.operation_var, 
            values=["incoming", "outgoing"],
            state="readonly",
            width=27,
            font=("Arial", 10)
        )
        operation_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        operation_dropdown.bind("<Return>", self.focus_on_next_widget)

        tk.Label(stock_frame, text="Reason:", bg=self.bg, fg="#2C3E50").grid(
            row=3, column=0, padx=10, pady=5, sticky="ne"
        )
        self.reason_entry = tk.Text(stock_frame, height=3, width=30, font=("Arial", 10))
        self.reason_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.reason_entry.bind("<Return>", self.focus_on_next_widget)

        stock_button_frame = tk.Frame(stock_frame, bg=self.bg)
        stock_button_frame.grid(row=4, column=0, columnspan=2, pady=15)

        tk.Button(
            stock_button_frame,
            text="Update Stock",
            command=self.update_stock,
            bg="#E67E22",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            stock_button_frame,
            text="Clear Form",
            command=self.clear_stock_form,
            bg="#F39C12",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

    def load_suppliers(self):
        try:
            suppliers = self.parent.supplier_manager.get_all_suppliers()
            supplier_names = [f"{supplier['name']} (ID: {supplier['id']})" for supplier in suppliers]
            self.supplier_menu['values'] = supplier_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def load_medicines(self):
        try:
            medicines = self.parent.medicine_manager.get_all_medicines()
            medicine_names = [f"{medicine['name']} (ID: {medicine['id']})" for medicine in medicines]
            self.medicine_menu['values'] = medicine_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")

    def on_supplier_selected(self, event):
        selected = self.supplier_var.get()
        if selected:
            try:
                self.supplier_id = int(selected.split("ID: ")[1].split(")")[0])
                self.supplier_menu.bind("<Return>", self.focus_on_next_widget)
            except:
                self.supplier_id = None

    def on_medicine_selected(self, event):
        selected = self.medicine_var.get()
        if selected:
            try:
                self.medicine_id = int(selected.split("ID: ")[1].split(")")[0])
                self.medicine_menu.bind("<Return>", self.focus_on_next_widget)
            except:
                self.medicine_id = None

    def add_medicine(self):
        try:
            medicine_name = self.medicine_name_entry.get()
            description = self.description_entry.get(1.0, tk.END).strip()
            batch_number = self.batch_number_entry.get()
            expiry_date = self.get_expiry_date()

            supplier = self.supplier_var.get()
            price = float(self.price_entry.get())
            
            if not all([medicine_name, description, price, batch_number, expiry_date, supplier]):
                tk.messagebox.showerror("Error", "Please fill in all fields")
                return
            medicine_data = {
                'name': medicine_name,
                'description': description,
                'price': float(price),
                'batch_number': batch_number,
                'expiry_date': expiry_date,
                'supplier_id': supplier
            }
            medicine_id = self.parent.medicine_manager.add_medicine(**medicine_data)
            
            if medicine_id:
                messagebox.showinfo("Success", f"Medicine '{medicine_name}' added successfully!")
                self.clear_medicine_form()
                self.load_medicines()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")

    def add_user(self):
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            role = self.role_var.get()
            full_name = self.full_name_entry.get().strip()
            email = self.email_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required")
                return
            
            user_id = self.parent.user_manager.create_user(
                username, password, role, full_name, email
            )
            
            if user_id:
                messagebox.showinfo("Success", f"User '{username}' created successfully!")
                self.clear_user_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create user: {str(e)}")

    def add_supplier(self):
        try:
            name = self.supplier_name_entry.get().strip()
            email = self.supplier_email_entry.get().strip()
            phone = self.supplier_phone_entry.get().strip()
            address = self.supplier_address_entry.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Supplier name is required")
                return
            
            supplier_id = self.parent.supplier_manager.add_supplier(
                name, address, email, phone, address
            )
            
            if supplier_id:
                messagebox.showinfo("Success", f"Supplier '{name}' added successfully!")
                self.clear_supplier_form()
                self.load_suppliers()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

    def update_stock(self):
        try:
            if not self.medicine_id:
                messagebox.showerror("Error", "Please select a medicine")
                return
            
            quantity = int(self.quantity_entry.get())
            operation = self.operation_var.get()
            reason = self.reason_entry.get("1.0", tk.END).strip()
            
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
            
            success = self.parent.medicine_manager.update_stock(
                self.medicine_id, quantity, operation, self.parent.user_id, reason=reason
            )
            
            if success:
                messagebox.showinfo("Success", f"Stock updated successfully!")
                self.clear_stock_form()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")

    def clear_medicine_form(self):
        self.medicine_name_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.price_entry.delete(0, tk.END)
        self.batch_number_entry.delete(0, tk.END)
        self.set_expiry_date(date.today())
        self.supplier_var.set("")
        self.supplier_id = None

    def clear_user_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_var.set("admin")
        self.full_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def clear_supplier_form(self):
        self.supplier_name_entry.delete(0, tk.END)
        self.supplier_email_entry.delete(0, tk.END)
        self.supplier_phone_entry.delete(0, tk.END)
        self.supplier_address_entry.delete("1.0", tk.END)

    def clear_stock_form(self):
        self.medicine_var.set("")
        self.quantity_entry.delete(0, tk.END)
        self.operation_var.set("incoming")
        self.reason_entry.delete("1.0", tk.END)
        self.medicine_id = None

    def set_expiry_date(self, date_obj):
        """Set the expiry date from a date object"""
        if date_obj:
            self.datevar.set(date_obj)

    def get_expiry_date(self):
        """Get the selected expiry date"""
        try:
            return self.datevar.get()
        except ValueError:
            return None

    def focus_on_next_widget(self, event):
        next_widget = event.widget.tk_focusNext()
        next_widget.focus()

        if isinstance(next_widget, tk.Spinbox):
            next_widget.icursor(tk.END)
        return


class Analytics_and_Reports(tk.Frame):
    """ """
    def __init__(self, box, parent):
        super().__init__(box, bg="#F8F9FA")
        self.parent = parent
        self.financial_text = None
        self.create_content()

    def create_content(self):

        title_label = tk.Label(
            self,
            text="Analytics & Reports",
            font=("Arial", 20, "bold"),
            fg="#2C3E50",
            bg="#F8F9FA",
        )
        title_label.pack(pady=20)


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.stock_tab = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.stock_tab, text="Stock Report")
        self.create_stock_report_tab()

        self.transaction_tab = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.transaction_tab, text="Transaction Report")
        self.create_transaction_report_tab()

        self.financial_tab = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.financial_tab, text="Financial Summary")
        self.create_financial_summary_tab()

    def create_stock_report_tab(self):
        control_frame = tk.Frame(self.stock_tab, bg="#F8F9FA")
        control_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            control_frame,
            text="Generate Stock Report",
            command=self.generate_stock_report,
            bg="#3498DB",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        self.stock_tree = ttk.Treeview(self.stock_tab, columns=("Name", "Quantity", "Min Stock", "Price", "Status"), show="headings")
        self.stock_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.stock_tree.heading("Name", text="Medicine Name")
        self.stock_tree.heading("Quantity", text="Quantity")
        self.stock_tree.heading("Min Stock", text="Min Stock")
        self.stock_tree.heading("Price", text="Price")
        self.stock_tree.heading("Status", text="Status")

        stock_scrollbar = ttk.Scrollbar(self.stock_tab, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=stock_scrollbar.set)
        stock_scrollbar.pack(side="right", fill="y")

    def create_transaction_report_tab(self):
        control_frame = tk.Frame(self.transaction_tab, bg="#F8F9FA")
        control_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            control_frame,
            text="Generate Transaction Report",
            command=self.generate_transaction_report,
            bg="#27AE60",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=5)

        self.transaction_tree = ttk.Treeview(self.transaction_tab, columns=("Date", "Medicine", "Type", "Quantity", "User"), show="headings")
        self.transaction_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.transaction_tree.heading("Date", text="Date")
        self.transaction_tree.heading("Medicine", text="Medicine")
        self.transaction_tree.heading("Type", text="Type")
        self.transaction_tree.heading("Quantity", text="Quantity")
        self.transaction_tree.heading("User", text="User")

    def create_financial_summary_tab(self):
        summary_frame = tk.Frame(self.financial_tab, bg="#F8F9FA")
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Button(
            summary_frame,
            text="Generate Financial Summary",
            command=self.generate_financial_summary,
            bg="#9B59B6",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2"
        ).pack( pady=10)

        financial_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical")
        financial_scrollbar.pack(side="right", fill="y")

        self.financial_text = tk.Text(summary_frame, height=20, width=80, font=("Arial", 10))
        self.financial_text.pack(fill="both", expand=True)

        financial_scrollbar.configure(command=self.financial_text.yview)
        self.financial_text.configure(yscrollcommand=financial_scrollbar.set)
        
    def generate_stock_report(self):
        try:
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)

            stock_data = self.parent.reports.get_stock_report()
            
            for row in stock_data:
                status = "LOW" if row['quantity'] <= row['minimum_stock'] else "OK"
                self.stock_tree.insert("", "end", values=(
                    row['name'],
                    row['quantity'],
                    row['minimum_stock'],
                    f"${row['price']:.2f}",
                    status
                ))
            
            messagebox.showinfo("Success", "Stock report generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate stock report: {str(e)}")

    def generate_transaction_report(self):
        try:
            for item in self.transaction_tree.get_children():
                self.transaction_tree.delete(item)

            transaction_data = self.parent.reports.get_transaction_report()
            
            for row in transaction_data:
                self.transaction_tree.insert("", "end", values=(
                    row['date'],
                    row['medicine_name'],
                    row['transaction_type'],
                    row['quantity'],
                    row['username']
                ))
            
            messagebox.showinfo("Success", "Transaction report generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate transaction report: {str(e)}")

    def generate_financial_summary(self):
        try:
            self.financial_text.delete("1.0", tk.END)
            
            summary_data = self.parent.reports.get_financial_summary()
            
            summary_text = "FINANCIAL SUMMARY\n"
            summary_text += "=" * 50 + "\n\n"
            summary_text += f"Total Stock Value: ${summary_data['total_stock_value']:.2f}\n\n"
            summary_text += "TRANSACTION SUMMARY:\n"
            summary_text += "-" * 30 + "\n"
            
            for transaction in summary_data['transactions']:
                summary_text += f"{transaction['transaction_type'].title()}: "
                summary_text += f"${transaction['total_amount']:.2f} "
                summary_text += f"({transaction['transaction_count']} transactions)\n"
            
            self.financial_text.insert("1.0", summary_text)
            
            messagebox.showinfo("Success", "Financial summary generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate financial summary: {str(e)}")


class MedicineWarehouseApp(tk.Tk):
    """ """
    def __init__(self):
        super().__init__()
        
        self.db = Database()
        self.user_manager = User(self.db)
        self.medicine_manager = Medicine(self.db)
        self.supplier_manager = Supplier(self.db)
        self.reports = Reports(self.db)

        self.activity_monitor = ActivityMonitor(self, timeout_minutes=5)

        self.state("zoomed")
        self.wm_minsize(800, 600)
        
        self.user_name = None
        self.user_role = None
        self.user_id = None
        
        self.title("Medicine Warehouse Management System")
        self.geometry("1200x700")
        self.configure(bg="#ECF0F1")
        self.state('zoomed')  
        

        self.sidebar = None
        self.header = None
        self.main_content = None
        self.current_frame = None
        
        self.show_login()

    def show_login(self):
        """Show login window"""
        login_window = LoginWindow(self)
        self.wait_window(login_window)

    def set_user(self, username, role, user_id):
        """Set user session after successful login"""
        self.user_name = username
        self.user_role = role
        self.user_id = user_id
        self.setup_main_interface()
        self.activity_monitor.start_monitoring()

    def setup_main_interface(self):
        """Setup the main application interface"""
        self.main_container = tk.Frame(self, bg="#ECF0F1")
        self.sidebar = Sidebar(self)
        self.header = Header(self, self.toggle_sidebar, self.logout)
        
        self.main_container.pack(fill="both", expand=True)
        
        self.main_content = tk.Frame(self.main_container, bg="#ECF0F1")
        self.main_content.pack(side="right", fill="both", expand=True)
        
        self.switch_frame(Dashboard)

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar.winfo_viewable():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y", before=self.main_content)

    def switch_frame(self, frame_class):
        """Switch to a different frame"""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = frame_class(self.main_content,self)
        self.current_frame.pack(fill="both", expand=True)

        if hasattr(self, 'activity_monitor') and self.activity_monitor.is_active:
            self.activity_monitor.bind_activity_events()

    def logout(self):
        """Logout and return to login screen"""
        self.activity_monitor.stop_monitoring()

        self.user_name = None
        self.user_role = None
        self.user_id = None
        
        if self.header:
            self.header.destroy()
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        self.show_login()

    def set_session_timeout(self, minutes):
        """Set session timeout in minutes"""
        self.activity_monitor.timeout_minutes = minutes
        self.activity_monitor.timeout_ms = minutes * 60 * 1000


if __name__ == "__main__":
    app = MedicineWarehouseApp()
    app.mainloop()

