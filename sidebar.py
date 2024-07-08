import tkinter as tk
from ttkbootstrap import Style

def create_sidebar(parent, on_refresh, on_show_charts, on_search):
    # Create a frame for the sidebar
    sidebar_frame = tk.Frame(parent, bg='lightgrey', pady=10)

    # Add buttons to the sidebar
    refresh_btn = tk.Button(sidebar_frame, text="Refresh Data", command=on_refresh)
    refresh_btn.pack(pady=10)

    chart_btn = tk.Button(sidebar_frame, text="Show Charts", command=on_show_charts)
    chart_btn.pack(pady=10)

    # You can add more buttons as needed
    # e.g., search functionality
    search_term_var = tk.StringVar()
    search_entry = tk.Entry(sidebar_frame, textvariable=search_term_var, width=20)
    search_entry.pack(pady=10)

    search_btn = tk.Button(sidebar_frame, text="Search", command=lambda: on_search(search_term_var.get()))
    search_btn.pack(pady=10)

    return sidebar_frame
