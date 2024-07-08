import tkinter as tk
from ttkbootstrap import Style

def create_navbar(parent, on_refresh, on_show_charts, on_search):
    # Create a frame for the navigation bar
    nav_frame = tk.Frame(parent, bg='lightgrey', pady=10)

    # Search entry
    search_term_var = tk.StringVar()
    search_entry = tk.Entry(nav_frame, textvariable=search_term_var, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)

    # Search button
    search_btn = tk.Button(nav_frame, text="Search", command=lambda: on_search(search_term_var.get()))
    search_btn.pack(side=tk.LEFT, padx=5)

    # Refresh button
    refresh_btn = tk.Button(nav_frame, text="Refresh Data", command=on_refresh)
    refresh_btn.pack(side=tk.LEFT, padx=5)

    # Show Charts button
    chart_btn = tk.Button(nav_frame, text="Show Charts", command=on_show_charts)
    chart_btn.pack(side=tk.LEFT, padx=5)

    return nav_frame
