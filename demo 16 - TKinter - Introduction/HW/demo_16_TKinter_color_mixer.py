import tkinter as Tk

def update_color():
    r = int(red_var.get())
    g = int(green_var.get())
    b = int(blue_var.get())
    
    # hex color
    hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    color_box.config(bg=hex_color)
    hex_entry.delete(0, Tk.END)
    hex_entry.insert(0, hex_color.upper())

def save_color():
    hex_color = hex_entry.get()
    color_list.insert(Tk.END, hex_color)

def load_color(event):
    try:
        index = color_list.curselection()[0]
        hex_color = color_list.get(index)    
        # convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # set sliders
        red_var.set(r)
        green_var.set(g)
        blue_var.set(b)
        update_color()
    except:
        pass

def set_preset():
    choice = preset_var.get()
    
    if choice == 1:  # red
        red_var.set(255)
        green_var.set(0)
        blue_var.set(0)
    elif choice == 2:  # green
        red_var.set(0)
        green_var.set(255)
        blue_var.set(0)
    elif choice == 3:  # blue
        red_var.set(0)
        green_var.set(0)
        blue_var.set(255)
    update_color()

root = Tk.Tk()
root.title("Color Mixer")
root.geometry("400x600")

title = Tk.Label(root, text="Color Mixer", font=('Arial', 16, 'bold'))
title.pack(pady=10)
color_box = Tk.Frame(root, bg='white', width=300, height=100, relief=Tk.SOLID, bd=2)
color_box.pack(pady=10)
color_box.pack_propagate(False)
entry_label = Tk.Label(root, text="Hex Code:", font=('Arial', 10))
entry_label.pack()

hex_entry = Tk.Entry(root, font=('Arial', 12), width=15, justify='center')
hex_entry.pack(pady=5)
hex_entry.insert(0, "#FFFFFF")

# red scale
red_label = Tk.Label(root, text="Red", fg='red', font=('Arial', 10, 'bold'))
red_label.pack()
red_var = Tk.IntVar(value=255)
red_scale = Tk.Scale(root, from_=0, to=255, orient=Tk.HORIZONTAL,
                     variable=red_var, command=lambda x: update_color(),
                     length=350, bg='#ffcccc')
red_scale.pack()

# green scale
green_label = Tk.Label(root, text="Green", fg='green', font=('Arial', 10, 'bold'))
green_label.pack()
green_var = Tk.IntVar(value=255)
green_scale = Tk.Scale(root, from_=0, to=255, orient=Tk.HORIZONTAL,
                       variable=green_var, command=lambda x: update_color(),
                       length=350, bg='#ccffcc')
green_scale.pack()

# blue scale
blue_label = Tk.Label(root, text="Blue", fg='blue', font=('Arial', 10, 'bold'))
blue_label.pack()
blue_var = Tk.IntVar(value=255)
blue_scale = Tk.Scale(root, from_=0, to=255, orient=Tk.HORIZONTAL,
                      variable=blue_var, command=lambda x: update_color(),
                      length=350, bg='#ccccff')
blue_scale.pack()

# presets
preset_label = Tk.Label(root, text="Quick Colors:", font=('Arial', 10, 'bold'))
preset_label.pack(pady=(10, 5))
preset_var = Tk.IntVar(value=0)
radio_frame = Tk.Frame(root)
radio_frame.pack()

r1 = Tk.Radiobutton(radio_frame, text="Red", variable=preset_var, value=1, command=set_preset)
r1.pack(side=Tk.LEFT, padx=5)
r2 = Tk.Radiobutton(radio_frame, text="Green", variable=preset_var, value=2, command=set_preset)
r2.pack(side=Tk.LEFT, padx=5)
r3 = Tk.Radiobutton(radio_frame, text="Blue", variable=preset_var, value=3, command=set_preset)
r3.pack(side=Tk.LEFT, padx=5)

# save button
save_btn = Tk.Button(root, text="Save Color", command=save_color, font=('Arial', 10))
save_btn.pack(pady=10)
list_label = Tk.Label(root, text="Saved Colors (click to load):", font=('Arial', 10))
list_label.pack()

color_list = Tk.Listbox(root, height=5, width=20, font=('Courier', 11))
color_list.pack(pady=5)
color_list.bind('<<ListboxSelect>>', load_color)

# quit button
quit_btn = Tk.Button(root, text="Quit", command=root.quit, font=('Arial', 10))
quit_btn.pack(pady=10)

root.mainloop()