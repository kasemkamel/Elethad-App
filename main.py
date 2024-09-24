import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3


class LoginWindow(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def get_user_role(self, username, password):
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        connection.close()

        if result:
            return result[0]
        return None


class Sidebar(tk.Frame):
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
            ]
        else:
            buttons = [
                ("Main", self.show_main), 
            ]

        for text, command in buttons:
            btn = tk.Button(self, text=text, width= 10, command=command)
            btn.pack(fill='x', padx=10, pady=10)


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


class Header(tk.Frame):
    def __init__(self, parent, toggle_callback, logout_callback):
        super().__init__(parent, bg="darkgray", height=50)
        self.parent = parent
        self.pack(side="top", fill="x")

        self.logout_button = tk.Button(self, text="Logout", command=logout_callback)
        self.logout_button.pack(side="left", padx=10, pady=10)

        self.app_title = tk.Label(self, text="- Elethat -", font=("Arial", 16), bg="darkgray", fg="white")
        self.app_title.pack(side="left", expand=True, fill=None, anchor="center", padx=10, pady=10)
        self.app_title.bind('<Button 1>', self.parent.sidebar.show_main)
        
        self.toggle_button = tk.Button(self, text="==", command=toggle_callback)
        self.toggle_button.pack(side="right", padx=10, pady=10)


class ResizableImageFrame(tk.Frame):
    def __init__(self, parent, image_path, bg):
        super().__init__(parent, bg=bg)
        self.pack_propagate(False) 
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight(), fill=bg, outline=bg)
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
        self.bg = '#52DCF5'
        super().__init__(parent, bg=self.bg)
        label = tk.Label(self, text='Welcome to Elethad Company', font=('Arial', 20, 'bold'), fg='#1B0C00', bg=self.bg)
        label.pack(pady=30)
        
        imagesPathesList = ['t1.jpeg', 't2.jpeg', 't3.jpeg', 't4.jpeg']
        
        frame1 = tk.Frame(self, )
        frame1.pack(expand=True, fill="both")
        
        imageFrameRightUp = ResizableImageFrame(frame1, imagesPathesList[0], bg= self.bg)
        imageFrameRightUp.grid(row=0, column=1, sticky="nsew")
        frame1.grid_columnconfigure(1, weight=1)
        
        imageFrameLeftUp = ResizableImageFrame(frame1, imagesPathesList[1], bg= self.bg)
        imageFrameLeftUp.grid(row=0, column=0, sticky="nsew")
        frame1.grid_columnconfigure(0, weight=1)
        
        frame1.grid_rowconfigure(0, weight=1)
        
        
        ##
        frame2 = tk.Frame(self, )
        frame2.pack(expand=True, fill="both")

        imageFrameRightDown = ResizableImageFrame(frame2, imagesPathesList[2], bg= self.bg)
        imageFrameRightDown.grid(row=0, column=1, sticky="nsew")
        frame2.grid_columnconfigure(1, weight=1)
        
        imageFrameLeftDown = ResizableImageFrame(frame2, imagesPathesList[3], bg= self.bg)
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





class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Elethat Company")
        self.state("zoomed")
        
        self.user_name = None
        self.user_role = None


        # self.login_window = LoginWindow(self)
        # self.wait_window(self.login_window) 

        
        
        self.sidebar = Sidebar(self, self.user_role)

        self.header = Header(self, self.toggle_sidebar, self.logout)
        
        self.content_frame = None
        self.sidebar_visible = False

        self.switch_frame(MainFrame)
        
        # if not self.user_role:
        #     self.destroy()

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
