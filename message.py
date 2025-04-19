import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pywifi
from pywifi import const
import time
import threading
import json

IGNORED_FILE = "ignored_ssids.json"
try:
    with open(IGNORED_FILE, "r") as f:
        ignored_ssids = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    ignored_ssids = set()

def get_color(rssi):
    if rssi >= -50:
        return "lightblue"
    elif rssi >= -60:
        return "green"
    elif rssi >= -70:
        return "yellow"
    else:
        return "red"

def scan_wifi():
    try:
        min_dBm = int(min_dBm_entry.get())
        max_bssids = int(bssids_entry.get())

        text_area.delete(*text_area.get_children())

        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        time.sleep(2)
        results = iface.scan_results()

        if not results:
            print("No Wi-Fi networks found!")
            return

        scanned_data = []
        ssid_dict = {}
        bssid_tracker = {}

        for network in results:
            ssid = network.ssid
            bssid = network.bssid
            rssi = int(network.signal)

            bssid_tracker.setdefault(ssid, []).append({"bssid": bssid, "rssi": rssi})
            if ssid not in ssid_dict or rssi > ssid_dict[ssid]["signal"]:
                ssid_dict[ssid] = {"ssid": ssid, "bssid": bssid, "signal": rssi}

        for ssid, networks in bssid_tracker.items():
            if ssid in ignored_ssids:
                continue
            if len(networks) > max_bssids:
                rssi_values = [net["rssi"] for net in networks]
                if max(rssi_values) - min(rssi_values) > 10:
                    text_area.insert(
                        "", "end",
                        values=(ssid, "Suspicious", "Multiple BSSIDs with signal variance"),
                        tags=("suspicious",)
                    )
                    scanned_data.append({"ssid": ssid, "bssid": "Multiple BSSIDs", "signal": "Suspicious"})

        for net in ssid_dict.values():
            if net["signal"] >= min_dBm:
                text_area.insert("", "end", values=(net["ssid"], net["signal"], net["bssid"]))
                scanned_data.append(net)

        save_to_json(scanned_data)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid integers for dBm range and BSSID count.")

def save_to_json(scan_data):
    with open("scan_results.json", "w") as f:
        json.dump(scan_data, f, indent=4)

def ignore_selected():
    sel = text_area.selection()
    if not sel:
        messagebox.showwarning("Nothing selected", "Select a network first.")
        return
    for iid in sel:
        tags = text_area.item(iid, "tags")
        if "suspicious" in tags:
            ssid = text_area.item(iid, "values")[0]
            ignored_ssids.add(ssid)
            text_area.delete(iid)
    with open(IGNORED_FILE, "w") as f:
        json.dump(list(ignored_ssids), f, indent=4)

def toggle_auto_refresh():
    global auto_refresh_enabled
    auto_refresh_enabled = auto_refresh_var.get()
    if auto_refresh_enabled:
        try:
            delay = int(refresh_delay_entry.get())
            auto_refresh(delay)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of seconds for refresh delay.")

def auto_refresh(delay):
    if auto_refresh_enabled:
        threading.Thread(target=scan_wifi).start()
        root.after(delay * 1000, lambda: auto_refresh(delay))

root = tk.Tk()
root.title("WiFi Identifier - Auto Refresh Enabled and Ignore List")
root.geometry("600x700")
root.resizable(False, False)

main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill=tk.BOTH, expand=True)

label = tk.Label(
    main_frame,
    text="Scan for nearby Wi-Fi networks and customize thresholds",
    font=("Helvetica", 14, "bold"),
    bg="white"
)
label.grid(row=0, column=0, columnspan=2, pady=20)

input_frame = tk.Frame(main_frame, bg="white")
input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")

min_dBm_label = tk.Label(input_frame, text="Enter minimum dBm (signal strength):", font=("Helvetica", 12), bg="white")
min_dBm_label.grid(row=0, column=0, sticky="w", pady=5)
min_dBm_entry = tk.Entry(input_frame, font=("Helvetica", 12))
min_dBm_entry.grid(row=0, column=1, padx=10)
min_dBm_entry.insert(0, "-70")

bssids_label = tk.Label(input_frame, text="Enter max number of BSSIDs per SSID:", font=("Helvetica", 12), bg="white")
bssids_label.grid(row=1, column=0, sticky="w", pady=5)
bssids_entry = tk.Entry(input_frame, font=("Helvetica", 12))
bssids_entry.grid(row=1, column=1, padx=10)
bssids_entry.insert(0, "3")

refresh_delay_label = tk.Label(input_frame, text="Auto-refresh delay (sec):", font=("Helvetica", 12), bg="white")
refresh_delay_label.grid(row=2, column=0, sticky="w", pady=5)
refresh_delay_entry = tk.Entry(input_frame, font=("Helvetica", 12))
refresh_delay_entry.grid(row=2, column=1, padx=10)
refresh_delay_entry.insert(0, "10")

auto_refresh_var = tk.BooleanVar()
auto_refresh_enabled = False
auto_refresh_check = tk.Checkbutton(
    input_frame,
    text="Enable Auto-Refresh",
    variable=auto_refresh_var,
    command=toggle_auto_refresh,
    font=("Helvetica", 12),
    bg="white"
)
auto_refresh_check.grid(row=3, column=0, columnspan=2, pady=10)

button = tk.Button(input_frame, text="Scan Wi-Fi", command=scan_wifi, font=("Helvetica", 12), width=15)
button.grid(row=4, column=0, columnspan=2, pady=10)

ignore_button = tk.Button(
    input_frame,
    text="Ignore Suspicious",
    command=ignore_selected,
    font=("Helvetica", 12),
    width=15
)
ignore_button.grid(row=5, column=0, columnspan=2, pady=5)

columns = ("SSID", "Signal (RSSI dBm)", "BSSID (MAC Address)")
text_area = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
text_area.grid(row=6, column=0, columnspan=2, pady=10, padx=20)
for col in columns:
    text_area.heading(col, text=col)
    text_area.column(col, anchor=tk.CENTER, width=200)

root.mainloop()
