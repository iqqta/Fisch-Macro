#!/usr/bin/env python3
import threading
import time
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import pyautogui

# ---------- Konfigurasi ----------
DEADZONE = 12
TAP_DURATION = 0.05
CAPTURE_DELAY = 0.04
SMOOTH_FACTOR = 0.35
MASK_SUM_THRESH = 2000
CONSECUTIVE_DETECT = 2
CONSECUTIVE_LOST = 8
WATCHDOG_TIMEOUT = 4.0  # detik

bar_coords = [283, 687, 391, 26]

running = False
mouse_down = False
mouse_lock = threading.Lock()
last_gx = None
stop_event = threading.Event()

# ---------- Deteksi Reel Bar ----------
def analyze_frame(pil_img):
    try:
        bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        return 0, None

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 70])
    upper = np.array([180, 50, 220])
    mask = cv2.inRange(hsv, lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    mask_sum = int(mask.sum())

    if mask_sum < MASK_SUM_THRESH:
        return mask_sum, None

    moments = cv2.moments(mask)
    if moments.get("m00", 0) == 0:
        return mask_sum, None
    cx = int(moments["m10"] / moments["m00"])
    return mask_sum, cx

# ---------- Kontrol Mouse ----------
def safe_mouse_down():
    global mouse_down
    with mouse_lock:
        if not mouse_down:
            try:
                pyautogui.mouseDown()
                mouse_down = True
            except Exception as e:
                print("[mouse] down failed:", e)

def safe_mouse_up():
    global mouse_down
    with mouse_lock:
        if mouse_down:
            try:
                pyautogui.mouseUp()
            except Exception as e:
                print("[mouse] up failed:", e)
            mouse_down = False

# ---------- Worker ----------
def worker_loop(gui_update_callback=None):
    global last_gx
    print("[worker] started")
    consec_detect = 0
    consec_lost = 0
    last_gx = None
    last_state_change = time.time()
    current_state = None

    time.sleep(1.5)  # delay awal

    while running and not stop_event.is_set():
        x, y, w, h = bar_coords
        try:
            shot = pyautogui.screenshot(region=(x, y, w, h))
        except Exception as e:
            print("[worker] screenshot error:", e)
            time.sleep(0.2)
            continue

        mask_sum, cx = analyze_frame(shot)
        present = cx is not None

        if present:
            consec_detect += 1
            consec_lost = 0
        else:
            consec_lost += 1
            consec_detect = 0

        if consec_lost >= CONSECUTIVE_LOST:
            safe_mouse_up()
            last_gx = None
            gui_update_callback("Idle / Bar Not Found")
            time.sleep(0.1)
            continue

        if cx is not None:
            if last_gx is not None:
                gx = int(last_gx * SMOOTH_FACTOR + cx * (1 - SMOOTH_FACTOR))
            else:
                gx = cx
            last_gx = gx
        else:
            gx = last_gx

        if gx is None:
            time.sleep(CAPTURE_DELAY)
            continue

        center = (w // 2)
        diff = gx - center

        if abs(diff) <= DEADZONE:
            safe_mouse_up()
            try:
                pyautogui.mouseDown()
                time.sleep(TAP_DURATION)
                pyautogui.mouseUp()
            except Exception as e:
                print("[tap] error:", e)
            new_state = "Center Tap"
        elif diff > 0:
            safe_mouse_down()
            new_state = "Hold Left (→)"
        else:
            safe_mouse_up()
            new_state = "Release (←)"

        if new_state != current_state:
            gui_update_callback(new_state)
            current_state = new_state
            last_state_change = time.time()

        if time.time() - last_state_change > WATCHDOG_TIMEOUT:
            print("[watchdog] refresh mouse")
            safe_mouse_up()
            try:
                pyautogui.mouseDown()
                time.sleep(TAP_DURATION)
                pyautogui.mouseUp()
            except Exception as e:
                print("[watchdog tap] error:", e)
            current_state = "Center Tap (Recovered)"
            gui_update_callback(current_state)
            last_state_change = time.time()

        time.sleep(CAPTURE_DELAY)

    safe_mouse_up()
    print("[worker] stopped")
    gui_update_callback("Stopped")

# ---------- GUI ----------
root = tk.Tk()
root.title("Fisch Macro V1")
root.geometry("480x360")
root.minsize(420, 320)
root.resizable(True, True)

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# ---------- Bagian Status ----------
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill="x", pady=(0, 8))

status_label = ttk.Label(status_frame, text="Status: OFF", foreground="red", font=("Arial", 12, "bold"))
status_label.pack(side="left")

state_var = tk.StringVar(value="STATE: -")
state_lbl = ttk.Label(status_frame, textvariable=state_var, font=("Arial", 11))
state_lbl.pack(side="right")

# ---------- Area Koordinat ----------
coords_frame = ttk.LabelFrame(main_frame, text="Capture Area", padding=8)
coords_frame.pack(fill="x", pady=6)

ttk.Label(coords_frame, text="X").grid(row=0, column=0, sticky="e")
x_var = tk.IntVar(value=bar_coords[0]); ttk.Entry(coords_frame, textvariable=x_var, width=8).grid(row=0, column=1, padx=6)
ttk.Label(coords_frame, text="Y").grid(row=0, column=2, sticky="e")
y_var = tk.IntVar(value=bar_coords[1]); ttk.Entry(coords_frame, textvariable=y_var, width=8).grid(row=0, column=3, padx=6)

ttk.Label(coords_frame, text="W").grid(row=1, column=0, sticky="e")
w_var = tk.IntVar(value=bar_coords[2]); ttk.Entry(coords_frame, textvariable=w_var, width=8).grid(row=1, column=1, padx=6)
ttk.Label(coords_frame, text="H").grid(row=1, column=2, sticky="e")
h_var = tk.IntVar(value=bar_coords[3]); ttk.Entry(coords_frame, textvariable=h_var, width=8).grid(row=1, column=3, padx=6)

coords_frame.columnconfigure((1, 3), weight=1)

# ---------- Tombol Aksi ----------
btn_frame = ttk.Frame(main_frame)
btn_frame.pack(fill="x", pady=10)

# Pisahkan tombol kiri & kanan agar responsif
left_btns = ttk.Frame(btn_frame)
left_btns.pack(side="left", anchor="w")

right_btns = ttk.Frame(btn_frame)
right_btns.pack(side="right", anchor="e")

# Tombol kiri
ttk.Button(left_btns, text="Open Overlay", command=lambda: open_overlay()).pack(side="left", padx=4)

# Tombol kanan
ttk.Button(right_btns, text="Stop", command=lambda: stop_macro()).pack(side="right", padx=4)
ttk.Button(right_btns, text="Start", command=lambda: start_macro()).pack(side="right", padx=4)

# ---------- Spacer ----------
ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=8)

# ---------- Log Area ----------
log_frame = ttk.Frame(main_frame)
log_frame.pack(fill="both", expand=True)

log_text = tk.Text(log_frame, height=6, wrap="word", state="disabled", font=("Courier", 9))
log_text.pack(fill="both", expand=True, padx=4, pady=4)

def gui_update_state(new_state):
    def _update():
        state_var.set(f"STATE: {new_state}")
        log_text.config(state="normal")
        log_text.insert("end", f"[STATE] {new_state}\n")
        log_text.see("end")
        log_text.config(state="disabled")
    root.after(0, _update)

# ---------- Overlay Window ----------
overlay_win = None
def open_overlay():
    global overlay_win
    if overlay_win and overlay_win.winfo_exists():
        overlay_win.lift()
        return
    overlay_win = tk.Toplevel(root)
    overlay_win.title("Overlay Selector")
    overlay_win.configure(bg="red")
    overlay_win.attributes("-topmost", True)
    overlay_win.attributes("-alpha", 0.35)
    x, y, w, h = bar_coords
    overlay_win.geometry(f"{w}x{h}+{x}+{y}")

    drag = {"x":0, "y":0}
    def start_drag(e):
        drag["x"], drag["y"] = e.x, e.y
    def do_drag(e):
        nx = overlay_win.winfo_x() + (e.x - drag["x"])
        ny = overlay_win.winfo_y() + (e.y - drag["y"])
        overlay_win.geometry(f"+{nx}+{ny}")
    overlay_win.bind("<Button-1>", start_drag)
    overlay_win.bind("<B1-Motion>", do_drag)

    def save_area():
        x2, y2 = overlay_win.winfo_x(), overlay_win.winfo_y()
        w2, h2 = overlay_win.winfo_width(), overlay_win.winfo_height()
        bar_coords[:] = [x2, y2, w2, h2]
        x_var.set(x2); y_var.set(y2); w_var.set(w2); h_var.set(h2)
        print("[Overlay] saved:", bar_coords)
    ttk.Button(overlay_win, text="Save", command=save_area).pack(pady=8, side="bottom")

# ---------- Start/Stop Macro ----------
worker_thread = None
def start_macro():
    global running, worker_thread, stop_event
    if running: return
    bar_coords[:] = [x_var.get(), y_var.get(), w_var.get(), h_var.get()]
    stop_event.clear()
    running = True
    status_label.config(text="Status: ON", foreground="green")
    worker_thread = threading.Thread(target=worker_loop, kwargs={"gui_update_callback": gui_update_state}, daemon=True)
    worker_thread.start()
    gui_update_state("Reeling Active")
    print("[GUI] started")

def stop_macro():
    global running
    running = False
    stop_event.set()
    safe_mouse_up()
    status_label.config(text="Status: OFF", foreground="red")
    gui_update_state("Stopped")
    print("[GUI] stopped")

def on_close():
    stop_macro()
    try:
        if overlay_win and overlay_win.winfo_exists():
            overlay_win.destroy()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
