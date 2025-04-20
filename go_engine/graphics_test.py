import tkinter as tk

root = tk.Tk()

thing1 = tk.Canvas(root, bg = "red")
thing1.grid(row=0, column=0, columnspan=10, sticky='n')

label2 = tk.Label(root, text="Label 2", bg="blue")
label2.grid(row=0, column=0, sticky='nw')

root.mainloop()