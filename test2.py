# import tkinter as tk
# from tkinter import ttk

# root = tk.Tk()
# root.geometry('300x200')
# root.resizable(False, False)
# root.title('Spinbox Demo')

# current_value = tk.StringVar(value=0)
# spin_box = ttk.Spinbox(
#     root,
#     from_=0,
#     to=30,
#     textvariable=current_value,
#     wrap=True
#     )
# spin_box.pack()

# root.mainloop()

import tkinter as tk
from tkinter import ttk

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return
root = tk.Tk()

labelFrame = ttk.LabelFrame(root, text="form")
labelFrame.pack(padx=20, pady=20)

for i in range(5):
    entry = ttk.Entry(labelFrame)
    entry.pack(pady=5)
    entry.bind("<Return>", focus_next_widget)
root.mainloop()

