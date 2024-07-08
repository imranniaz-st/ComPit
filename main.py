import tkinter as tk
from tkinter import ttk
import pymysql
import psutil
import os
import time
import threading
import pyperclip
from pynput import keyboard
import pygetwindow as gw
import socket
import requests
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from navbar import create_navbar  # Import the navbar module
from sidebar import create_sidebar  # Import the sidebar module

# Function to fetch data from MySQL and populate the GUI table
def load_data(search_term=None):
    try:
        # Connect to MySQL database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     database='s22',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Select all rows from the system_activity table or filter based on the search term
            if search_term:
                sql = "SELECT * FROM system_activity WHERE action_type LIKE %s OR details LIKE %s"
                cursor.execute(sql, ('%' + search_term + '%', '%' + search_term + '%'))
            else:
                sql = "SELECT * FROM system_activity"
                cursor.execute(sql)
            data = cursor.fetchall()

            # Clear previous table content
            for row in tree.get_children():
                tree.delete(row)

            # Insert data into the GUI table
            for row in data:
                tree.insert("", "end", values=(row['id'], row['cpu_percent'], row['memory_percent'], row['disk_percent'], row['action_type'], row['details'], row['ip_address'], row['pc_name'], row['ram'], row['cpu'], row['created_at']))

    except pymysql.MySQLError as e:
        print(f"Error fetching data from MySQL: {e}")

    finally:
        # Close the connection
        if connection:
            connection.close()

# Function to monitor activities including keystrokes and active windows
def monitor_activities():
    def on_press(key):
        try:
            # Log the key pressed
            insert_activity("Key Press", str(key))

        except Exception as e:
            print(f"Error logging keystroke: {e}")

    def track_active_windows():
        while True:
            try:
                # Get a list of active windows
                active_windows = gw.getAllTitles()
                active_windows_str = ', '.join(active_windows)

                # Log active windows
                insert_activity("Active Windows", active_windows_str)

            except Exception as e:
                print(f"Error tracking active windows: {e}")

            # Adjust the sleep time based on how frequently you want to check active windows
            time.sleep(10)  # Check every 10 seconds

    # Monitor keyboard events
    with keyboard.Listener(on_press=on_press) as listener:
        # Start tracking active windows in a separate thread
        window_thread = threading.Thread(target=track_active_windows)
        window_thread.daemon = True
        window_thread.start()

        # Keep listening to keyboard events
        listener.join()

# Function to insert activity into MySQL database
def insert_activity(action_type, details):
    try:
        # Get IP address
        ip_address = requests.get('https://api.ipify.org').text

        # Get PC name
        pc_name = socket.gethostname()

        # Get RAM and CPU details
        ram_info = psutil.virtual_memory()
        ram_details = f"Total: {ram_info.total}, Available: {ram_info.available}, Percent: {ram_info.percent}"
        cpu_details = f"Physical cores: {psutil.cpu_count(logical=False)}, Total cores: {psutil.cpu_count(logical=True)}, Usage: {psutil.cpu_percent(interval=1)}%"

        # Connect to MySQL database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     database='s22',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Insert data into the database
            sql = """INSERT INTO system_activity (action_type, details, ip_address, pc_name, ram, cpu)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (action_type, details, ip_address, pc_name, ram_details, cpu_details))

            # Commit changes to the database
            connection.commit()
            print(f"Activity '{action_type}' logged successfully: {details}")

    except pymysql.MySQLError as e:
        print(f"Error inserting data into MySQL: {e}")

    finally:
        # Close the connection
        if connection:
            connection.close()

# Create a separate thread to monitor activities continuously
activity_thread = threading.Thread(target=monitor_activities)
activity_thread.daemon = True
activity_thread.start()

# Create the main window using ttkbootstrap
root = ttkb.Window(themename="cosmo")
root.title("System Activity Viewer")
root.geometry("1200x600")

# Create a frame for the main content
main_frame = tk.Frame(root)
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create the sidebar
sidebar_frame = create_sidebar(root, load_data, lambda: show_charts(tree), load_data)
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create the navigation bar
nav_frame = create_navbar(main_frame, load_data, lambda: show_charts(tree), load_data)
nav_frame.pack(fill=tk.X)

# Create a treeview widget (table) to display data
tree = ttkb.Treeview(main_frame, columns=('ID', 'CPU %', 'Memory %', 'Disk %', 'Action Type', 'Details', 'IP Address', 'PC Name', 'RAM', 'CPU', 'Created At'), show='headings', bootstyle='info')
tree.heading('ID', text='ID')
tree.heading('CPU %', text='CPU %')
tree.heading('Memory %', text='Memory %')
tree.heading('Disk %', text='Disk %')
tree.heading('Action Type', text='Action Type')
tree.heading('Details', text='Details')
tree.heading('IP Address', text='IP Address')
tree.heading('PC Name', text='PC Name')
tree.heading('RAM', text='RAM')
tree.heading('CPU', text='CPU')
tree.heading('Created At', text='Created At')

# Add a vertical scrollbar
scrollbar = ttkb.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)

# Pack the treeview widget
tree.pack(pady=10, expand=True, fill=tk.BOTH)

# Load initial data into the table
load_data()

# Function to create and display a CPU and memory usage chart
def show_charts(tree):
    # Fetch data from the treeview for charting
    data = []
    for child in tree.get_children():
        item = tree.item(child)
        data.append(item['values'])

    fig, ax = plt.subplots(2, 1, figsize=(10, 6))

    # CPU usage chart
    ax[0].set_title('CPU Usage')
    ax[0].plot([x[1] for x in data], label='CPU %', color='blue')
    ax[0].legend()

    # Memory usage chart
    ax[1].set_title('Memory Usage')
    ax[1].plot([x[2] for x in data], label='Memory %', color='red')
    ax[1].legend()

    # Display the charts in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, expand=True, fill=tk.BOTH)

# Run the Tkinter main loop
root.mainloop()
