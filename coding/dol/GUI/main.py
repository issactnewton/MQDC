#!/usr/bin/env python
# coding: utf-8

# # LIBRARY

# In[90]:


import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from tkinter import messagebox
import requests
import re
import time
import datetime
from tkinter import filedialog
from tkinter import messagebox
import PIL
import folium
import sys,os


# # FUNCTION

# In[95]:


def get_input():
    minlat = entry_minlat.get()
    minlon = entry_minlon.get()
    maxlat = entry_maxlat.get()
    maxlon = entry_maxlon.get()
    utm = entry_utm.get()
    resolution = resolution_combobox.get()
    parcel = parcel_combobox.get()
    
    inputs = [minlat, minlon, maxlat, maxlon, utm]
    if all(inputs) == False:
        messagebox.showerror("", "Please complete the information")
    
    else:
        # Split the resolution into width and height
        width, height = resolution.split(" x ")

        # Do something with the input values
    
        url = f"""https://landsmaps.dol.go.th/geoserver/LANDSMAPS/wms?transparent=true&format=image%2Fpng&viewparams=utmmap%3A{utm}&=&service=WMS&version=1.1.1&request=GetMap&styles=&layers=LANDSMAPS%3AV_PARCEL{parcel}&bbox={minlon}%2C{minlat}%2C{maxlon}%2C{maxlat}&width={width}&height={height}&srs=EPSG%3A4326
        """
        global response
        response = requests.get(url)
    
        global x
        global file_name
        global file_path
        label_loading.pack()
        if response.status_code:
            x = datetime.datetime.now()
            x = x.strftime("%d%m%y%H%M%S")
            delete_button.config(state="disabled")
            file_name = str(x)
            # Open file dialog with the generated file name as initial file name
            file_path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=".png",
                                             filetypes=[("PNG Files", "*.png")])
        
            if file_path:
                try:
                    # Open the PNG file in write+binary mode
                    with open(file_path, "wb") as file:
                        # Write data to the file
                        file.write(response.content)

                        # Calculate the center of the bbox
                        center_lat = (float(minlat) + float(maxlat)) / 2
                        center_lon = (float(minlon) + float(maxlon)) / 2

                    # Create a map object
                    maps = folium.Map(location=[center_lat, center_lon], zoom_start=20)

                    # Add a rectangle representing the bbox
                    folium.Rectangle(bounds=[[float(minlat),float(minlon)], [float(maxlat), float(maxlon)]], color='red', fill=False).add_to(maps)
                    
                    # Add markers for the corner coordinates
                    folium.Marker([float(minlat), float(minlon)], popup=f"{float(minlat)}, {float(minlon)}", icon=folium.Icon(color='blue')).add_to(maps)
                    folium.Marker([float(minlat), float(maxlon)], popup=f"{float(minlat)}, {float(maxlon)}", icon=folium.Icon(color='blue')).add_to(maps)
                    folium.Marker([float(maxlat), float(minlon)], popup=f"{float(maxlat)}, {float(minlon)}", icon=folium.Icon(color='blue')).add_to(maps)
                    folium.Marker([float(maxlat), float(maxlon)], popup=f"{float(maxlat)}, {float(maxlon)}", icon=folium.Icon(color='blue')).add_to(maps)
                    
                    # Save the map as an HTML file
                    maps.save(f"{file_path[:(len(file_path)-4)]}.html")
                except IOError:
                    print("An error occurred while writing to the PNG file.")
            else:
                print("No file path selected.")
    
        # Show the "Show Image" button
        show_image_button.pack_forget()
        time.sleep(5)
        label_loading.pack_forget()
        delete_button.config(state="enabled")
        minlat = minlon = maxlat = maxlon =  utm = ""
        show_image_button.pack()

def show_image():
    # Open and display the image
    try:
        image = Image.open(file_path)
        image.show()
        show_image_button.pack_forget()
    except (PIL.UnidentifiedImageError, FileNotFoundError, AttributeError):
        messagebox.showerror("", "The file is incompatible or has been removed")
        show_image_button.pack_forget()
        
    
def validate(string):
    regex = re.compile(r"()?[0-9.]*$")
    result = regex.match(string)
    return (string == ""
            or (string.count('.') <= 1
                and result is not None
                and result.group(0) != ""))

def validate_utm(string):
    regex = re.compile(r"()?[0-9]*$")
    result = regex.match(string)
    return (string == ""
            or (result is not None
                and result.group(0) != ""))

def restrict_utm(string):
    if len(entry_utm.get()) >= 9 and string.keysym != 'BackSpace':
        return 'break'
    
def on_validate(P):
    return validate(P)

def on_validate_utm(P):
    return validate_utm(P)

def clear_entries():
    entry_utm.delete(0, tk.END)
    entry_minlat.delete(0, tk.END)
    entry_minlon.delete(0, tk.END)
    entry_maxlat.delete(0, tk.END)
    entry_maxlon.delete(0, tk.END)
    
def fill_input():
    confirmation = messagebox.askquestion("", "Are you sure to fill the example data")
    if confirmation == 'yes':
        entry_utm.delete(0, tk.END)
        entry_minlat.delete(0, tk.END)
        entry_minlon.delete(0, tk.END)
        entry_maxlat.delete(0, tk.END)
        entry_maxlon.delete(0, tk.END)
        entry_utm.insert(0, "513647834")
        entry_minlat.insert(0, "13.8404")
        entry_minlon.insert(0, "100.5469")
        entry_maxlat.insert(0, "13.8872")
        entry_maxlon.insert(0, "100.5981")

def clear_some_entries(entry):
    entry.delete(0, tk.END)

def resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# # GUI

# In[102]:


# Create the main window
window = tk.Tk()
window.title("Boundary line retriever application")
window.geometry("500x500")
window.resizable(False, False)


# Create a frame to hold the input fields
input_frame = ttk.Frame(window, padding=50)
input_frame.pack(anchor="center")


# Create labels and entry fields for UTM
label_utm = ttk.Label(input_frame, text="UTM:")
label_utm.grid(row=0, column=0, sticky=tk.W)
entry_utm = ttk.Entry(input_frame, validate='key')
vcmd0 = (entry_utm.register(on_validate_utm), '%P')
entry_utm.config(validatecommand=vcmd0)
entry_utm.grid(row=0, column=1)
entry_utm.bind('<KeyPress>', restrict_utm)
clear_utm_button = ttk.Button(input_frame, text="Clear", command=lambda : clear_some_entries(entry_utm))
clear_utm_button.grid(row=0, column=2)

# Create labels and entry fields for MINLAT
label_minlat = ttk.Label(input_frame, text="Minimum Latitude:")
label_minlat.grid(row=1, column=0, sticky=tk.W)
entry_minlat = ttk.Entry(input_frame, validate='key')
vcmd1 = (entry_minlat.register(on_validate), '%P')
entry_minlat.config(validatecommand=vcmd1)
entry_minlat.grid(row=1, column=1)
clear_minlat_button = ttk.Button(input_frame, text="Clear", command=lambda : clear_some_entries(entry_minlat))
clear_minlat_button.grid(row=1, column=2)

# Create labels and entry fields for MINLON
label_minlon = ttk.Label(input_frame, text="Minimum Longitude:")
label_minlon.grid(row=2, column=0, sticky=tk.W)
entry_minlon = ttk.Entry(input_frame, validate='key')
vcmd2 = (entry_minlon.register(on_validate), '%P')
entry_minlon.config(validatecommand=vcmd2)
entry_minlon.grid(row=2, column=1)
clear_minlon_button = ttk.Button(input_frame, text="Clear", command=lambda : clear_some_entries(entry_minlon))
clear_minlon_button.grid(row=2, column=2)

# Create labels and entry fields for MAXLAT
label_maxlat = ttk.Label(input_frame, text="Maximum Latitude:")
label_maxlat.grid(row=3, column=0, sticky=tk.W)
entry_maxlat = ttk.Entry(input_frame, validate='key')
vcmd3 = (entry_maxlat.register(on_validate), '%P')
entry_maxlat.config(validatecommand=vcmd3)
entry_maxlat.grid(row=3, column=1)
clear_maxlat_button = ttk.Button(input_frame, text="Clear", command=lambda : clear_some_entries(entry_maxlat))
clear_maxlat_button.grid(row=3, column=2)

# Create labels and entry fields for MAXLON
label_maxlon = ttk.Label(input_frame, text="Maximum Longitude:")
label_maxlon.grid(row=4, column=0, sticky=tk.W)
entry_maxlon = ttk.Entry(input_frame, validate='key')
vcmd4 = (entry_maxlon.register(on_validate), '%P')
entry_maxlon.config(validatecommand=vcmd4)
entry_maxlon.grid(row=4, column=1)
clear_maxlon_button = ttk.Button(input_frame, text="Clear", command=lambda : clear_some_entries(entry_maxlon))
clear_maxlon_button.grid(row=4, column=2)

# Create a label and option box for PARCEL selection
label_parcel = ttk.Label(input_frame, text="Parcel:")
label_parcel.grid(row=5, column=0, sticky=tk.W)

# Create labels and entry fields for PARCEL
parcels = ["47","48"]
parcel_combobox = ttk.Combobox(input_frame, values=parcels, state="readonly")
parcel_combobox.current(0)  # Set default selection
parcel_combobox.grid(row=5, column=1)


# Create a label and option box for resolution selection
label_resolution = ttk.Label(input_frame, text="Resolution:")
label_resolution.grid(row=6, column=0, sticky=tk.W)

# Create labels and entry fields for input
resolutions = ["256 x 256", "500 x 500", "1080 x 720", "1920 x 1080", "1000 x 1000", "2000 x 2000", "3000 x 3000"]
resolution_combobox = ttk.Combobox(input_frame, values=resolutions, state="readonly")
resolution_combobox.current(3)  # Set default selection
resolution_combobox.grid(row=6, column=1)

# Create a button to submit the input
submit_button = ttk.Button(window, text="Retreive the boundary line", command=get_input)
submit_button.pack()

# Delete all input
delete_button = ttk.Button(window, text="Clear all fields", command=clear_entries)
delete_button.pack()


# Create a loading text
label_loading = ttk.Label(window, text="Loading image...")

# Create a button to show the image
show_image_button = ttk.Button(window, text="Show image", command=show_image)

# Create a auto complete button
fill_input_button = ttk.Button(window, text="Auto fill the example data", command=fill_input)
fill_input_button.pack(side=tk.BOTTOM, anchor=tk.S,pady = 50)


# Run the main window loop
logo = resource("mqdc.ico")
window.iconbitmap(logo)
window.mainloop()


# In[ ]:




