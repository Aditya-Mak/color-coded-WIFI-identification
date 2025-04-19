import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import pywifi
from pywifi import const
import time
import json
import os

# File to store known routers and their colors
CONFIG_FILE = "known_networks.json"

# Load saved known networks
def load_known_networks():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# Save known networks
def save_known_networks(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Ask user to pick color for new router
def prompt_color(ssid, bssid):
    result = messagebox.askyesno("New WiFi Detected", f"You just connected to '{ssid}'. Would you like to assign a color to this WiFi?")
    if result:
        color_code = colorchooser.askcolor(title=f"Pick a color for '{ssid}'")[1]
        if color_code:
            known[bssid] = {"ssid": ssid, "color": color_code}
            save_known_networks(known)
            messagebox.showinfo("Saved", f"Color saved for '{ssid}'.")

# Get the current connected WiFi BSSID
def get_current_bssid():
    iface = pywifi.PyWiFi().interfaces()[0]
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()
    connected_bssid = None
    for net in results:
        if iface.status() == const.IFACE_CONNECTED and net.ssid:
            connected_bssid = net.bssid.lower()
            break
    return connected_bssid

# Main scan function
def scan_wifi():
    text_area.delete(*text_area.get_children())

    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()

    current_bssid = get_current_bssid()
    if current_bssid and current_bssid not in known:
        for net in results:
            if net.bssid.lower() == current_bssid:
                prompt_color(net.ssid, net.bssid.lower())
                break

    added = set()
    for net in results:
        ssid = net.ssid
        bssid = net.bssid.lower()

        if ssid and ssid not in added:
            tags = ()
            if bssid in known:
                tag_name = bssid.replace(":", "")
                tags = (tag_name,)
                text_area.tag_configure(tag_name, background=known[bssid]["color"])

            text_area.insert("", "end", values=(ssid,), tags=tags)
            added.add(ssid)

# GUI Setup
root = tk.Tk()
root.title("Smart WiFi Identifier")
root.geometry("420x400")

label = tk.Label(root, text="Click to know your network", font=("Helvetica", 14))
label.pack(pady=10)

button = tk.Button(root, text="Scan WiFi", command=scan_wifi, font=("Helvetica", 12))
button.pack(pady=10)

columns = ("SSID",)
text_area = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    text_area.heading(col, text=col)
    text_area.column(col, anchor=tk.CENTER, width=350)
text_area.pack(pady=10)

known = load_known_networks()

root.mainloop()
