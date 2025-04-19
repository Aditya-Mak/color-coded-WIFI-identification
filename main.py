import tkinter as tk
from tkinter import ttk
import pywifi
from pywifi import const
import time

def get_color(rssi):
    """Return a color name based on signal strength (RSSI)"""
    if rssi >= -50:
        return "green"
    elif rssi >= -60:
        return "blue"
    elif rssi >= -70:
        return "orange"
    else:
        return "red"

def scan_wifi():
    """Scan for nearby WiFi networks and show them in the table"""
    text_area.delete(*text_area.get_children())  # Clear previous results

    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)  # Let the scan finish
    results = iface.scan_results()

    for network in results:
        ssid = network.ssid
        rssi = int(network.signal)  # Signal strength (usually negative dBm)
        color = get_color(rssi)
        text_area.insert("", "end", values=(ssid, rssi), tags=(color,))

    # Define tag-based background colors
    text_area.tag_configure("green", background="#a5d6a7")
    text_area.tag_configure("blue", background="#81d4fa")
    text_area.tag_configure("orange", background="#ffe082")
    text_area.tag_configure("red", background="#ef9a9a")

# ----- GUI Setup -----
root = tk.Tk()
root.title("WiFi Identifier - Color Coded")
root.geometry("600x400")

label = tk.Label(root, text="Click the button to scan nearby WiFi networks", font=("Helvetica", 14))
label.pack(pady=10)

button = tk.Button(root, text="Scan WiFi", command=scan_wifi, font=("Helvetica", 12))
button.pack(pady=10)

columns = ("SSID", "Signal (RSSI dBm)")
text_area = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    text_area.heading(col, text=col)
    text_area.column(col, anchor=tk.CENTER, width=250)
text_area.pack(pady=10)

root.mainloop()
