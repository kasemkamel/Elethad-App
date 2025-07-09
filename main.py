import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from database import *


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
        

class Frame1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightblue")
        label = tk.Label(self, text="This is Frame 1", font=("Arial", 16), bg="lightblue")
        label.pack(pady=20)


class Frame2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgreen")
        label = tk.Label(self, text="This is Frame 2", font=("Arial", 16), bg="lightgreen")
        label.pack(pady=20)


class Frame3(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightpink")
        label = tk.Label(self, text="This is Frame 3", font=("Arial", 16), bg="lightpink")
        label.pack(pady=20)


class Frame4(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightyellow")
        label = tk.Label(self, text="This is Frame 4 (Warehouse Worker)", font=("Arial", 16), bg="lightyellow")
        label.pack(pady=20)


class Frame5(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")
        label = tk.Label(self, text="This is Frame 5 (Warehouse Worker)", font=("Arial", 16), bg="lightgray")
        label.pack(pady=20)


class AdminFrame1(tk.Frame):
    def __init__(self, parent):
        self.bg = 'lightblue'
        super().__init__(parent, bg=self.bg)
        self.parent = parent
        self.supplier_id = None
        self.create_widgets()

    def create_widgets(self):
        leftFrame = tk.Frame(self, )
        leftFrame.pack(expand=True, fill="both", side='left')
        
        rightFrame = tk.Frame(self, )
        rightFrame.pack(expand=True, fill="both", side='right')
        
        
        bottomRightFrame = tk.Frame(rightFrame, )
        bottomRightFrame.grid(row=0, column=1, sticky="nsew")
        
        bottomleftFrame = tk.Frame(rightFrame, )
        bottomleftFrame.grid(row=0, column=0, sticky="nsew")
        
        
        # top Right Frame ## user frame 
        topRightFrame = tk.Frame(rightFrame, )
        topRightFrame.grid(row=0, column=1, sticky="nsew")

        title_label = tk.Label(topRightFrame, text="Add New User", font=('Arial', 20, 'bold'), bg=self.bg)
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        username_label = tk.Label(topRightFrame, text="Username:", bg=self.bg)
        username_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = tk.Entry(topRightFrame)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        password_label = tk.Label(topRightFrame, text="Password:", bg=self.bg)
        password_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(topRightFrame, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        role_label = tk.Label(topRightFrame, text="Role:", bg=self.bg)
        role_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.role_var = tk.StringVar(value="admin")  # Default value for role
        role_dropdown = tk.OptionMenu(topRightFrame, self.role_var, "admin", "W", "Ac")
        role_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        add_user_button = tk.Button(topRightFrame, text="Add User", command=self.add_user)
        add_user_button.grid(row=4, column=0, columnspan=2, pady=20)


        # bottom right Frame ## supplier frame
        bottomRightFrame = tk.Frame(rightFrame, )
        bottomRightFrame.grid(row=1, column=1, sticky="nsew", pady=40)
        
        title_label = tk.Label(bottomRightFrame, text="Add New supplier", font=('Arial', 20, 'bold'), bg=self.bg)
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        suppliername_label = tk.Label(bottomRightFrame, text="supplier name:", bg=self.bg)
        suppliername_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.suppliername_entry = tk.Entry(bottomRightFrame)
        self.suppliername_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        contact_info_label = tk.Label(bottomRightFrame, text="supplier contact info:", bg=self.bg)
        contact_info_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.contact_info_entry = tk.Entry(bottomRightFrame, )
        self.contact_info_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        add_supplier_button = tk.Button(bottomRightFrame, text="Add supplier", command=self.add_supplier)
        add_supplier_button.grid(row=4, column=0, columnspan=2, pady=20)


        # top Left Frame ## medicine frame
        topleftFrame = tk.Frame(leftFrame, )
        topleftFrame.grid(row=0, column=0, sticky="nsew")
        
        title_label = tk.Label(topleftFrame, text="Add New Medicine", font=('Arial', 20, 'bold'), bg=self.bg)
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        medicine_name_label = tk.Label(topleftFrame, text="medicine name:", bg=self.bg)
        medicine_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.medicine_name_entry = tk.Entry(topleftFrame)
        self.medicine_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        description_label = tk.Label(topleftFrame, text="description:", bg=self.bg)
        description_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.description_entry = tk.Text(topleftFrame, height=20)
        self.description_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        price_label = tk.Label(topleftFrame, text="price 'P':", bg=self.bg)
        price_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.price_entry = tk.Entry(topleftFrame,)
        self.price_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.supplier_var = tk.StringVar()
        supplier_label = tk.Label(topleftFrame, text="supplier 'P':", bg=self.bg)
        supplier_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.supplier_menu = ttk.Combobox(topleftFrame, textvariable=self.supplier_var)
        self.supplier_menu.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        self.supplier_menu.bind("<<ComboboxSelected>>", self.on_supplier_selected)
        
        add_medicine_button = tk.Button(topleftFrame, text="Add medicine", command=self.add_medicine)
        add_medicine_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        
        
        self.load_suppliers()
        
        
    def add_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
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
        suppliername = self.suppliername_entry.get()
        contact_info = self.contact_info_entry.get()

        if not suppliername or not contact_info :
            messagebox.showwarning("Input Error", "All fields must be filled!")
            return

        try:
            self.parent.supplier.insert(suppliername, contact_info)
            messagebox.showinfo("Success", f"supplier '{suppliername}' added successfully!")
            self.clear_supplier_form()
            self.load_suppliers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

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
        medicine_name = self.medicine_name_entry.get()
        description = self.description_entry.get("1.0", tk.END)
        price = self.price_entry.get()
        
        
        if not medicine_name or not self.supplier_id :
            messagebox.showwarning("Input Error", "All fields must be filled!")
            return
        
        try:
            self.parent.medicine.insert(medicine_name, description, price, self.supplier_id)
            messagebox.showinfo("Success", f"medicine '{medicine_name}' added successfully!")
            self.clear_medicine_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
        
        

    def clear_medicine_form(self):
        self.medicine_name_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.price_entry.delete(0, tk.END)
        self.supplier_id = None
        self.supplier_menu.current(0)
    


class AdminFrame2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray")
        label = tk.Label(self, text="This is admin Frame no. Two", font=("Arial", 16), bg="#11f3c9")
        label.pack(pady=20)


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
    



if __name__ == "__main__":
    app = App()
    app.mainloop()
