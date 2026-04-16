# overlay.py
import tkinter as tk
import math
import os
import sys
import win32gui
import win32process
import psutil
import win32con 
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

# ============================================================
# CONFIG — change DISPLAY_MODE to switch between styles
#   "knob"  — circular arc that fills like a volume knob (default)
#   "bar"   — ascending block character staircase (▁▂▃▄▅▆▇█)
#   "text"  — percentage number only, no graphic
# ============================================================
DISPLAY_MODE = "knob"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dial_state.txt")
LOCK_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlay.lock")

TARGETS = [
    "foreground",
    "Spotify.exe",
    "Discord.exe",
]

LABELS = {
    0: ("🖥 ", "#aaaaaa"), # you can have text here (or emojis)
    1: ("🎵 ",    "#1db954"),
    2: ("🎙 ",    "#5865f2"),
    3: ("Slot 3",         "#ffa500"),
    4: ("Slot 4",         "#ff0080"),
    5: ("Slot 5",         "#00c8ff"),
}

# --- Single instance lock ---

def check_single_instance():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            if psutil.pid_exists(old_pid):
                return False
        except (ValueError, OSError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

# --- State helpers ---

def get_index():
    try:
        with open(STATE_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def get_foreground_process():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except:
        return None

def get_volume_for_index(index):
    if index < len(TARGETS):
        target_entry = TARGETS[index]
    else:
        return None
    target = get_foreground_process() if target_entry == "foreground" else target_entry
    if not target:
        return None
    try:
        sessions = AudioUtilities.GetAllSessions()
        matching = [s for s in sessions
                    if s.Process and s.Process.name().lower() == target.lower()]
        if not matching:
            return None
        chosen = matching[0]
        for s in matching:
            if s.State == 1:
                chosen = s
                break
        vol = chosen._ctl.QueryInterface(ISimpleAudioVolume)
        return int(vol.GetMasterVolume() * 100)
    except:
        pass
    return None

# --- Display modes ---

BLOCKS = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

def volume_bar(pct):
    if pct is None:
        return "—"
    filled = max(0, min(8, round(pct / 100 * 8)))
    bar = "".join(BLOCKS[i] if i < filled else " " for i in range(8))
    return f"{pct}%  {bar}"

def draw_knob(canvas, pct, color, size=70):
    canvas.delete("all")
    if pct is None:
        pct = 0

    cx, cy = size // 2, size // 2
    r = size // 2 - 6
    track_width = 5

    # Background track
    canvas.create_arc(
        cx - r, cy - r, cx + r, cy + r,
        start=225 - 270,
        extent=270,
        style=tk.ARC,
        outline="#333333",
        width=track_width,
    )

    # Filled arc (clockwise from bottom-left)
    filled_sweep = 270 * (pct / 100)
    if filled_sweep > 0:
        canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=225,
            extent=-filled_sweep,
            style=tk.ARC,
            outline=color,
            width=track_width,
        )

    # Percentage in centre
    canvas.create_text(
        cx, cy,
        text=f"{pct}%",
        fill=color,
        font=("Segoe UI", 10, "bold"),
    )

# --- Poll loop ---

def resize_knob_window(widgets, root, text):
    """Resize the overlay window so it always fits the label text,
    keeping the right edge pinned 20px from the screen edge."""
    from tkinter import font as tkfont

    knob_size   = 70
    padding     = 8 + 4 + 20          # left pad + gap + right pad
    label_font  = tkfont.Font(family="Segoe UI", size=15, weight="bold")
    text_width  = label_font.measure(text)

    width  = knob_size + padding + text_width
    height = knob_size + 10

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    x = screen_w - width - 20
    y = screen_h - height - 60

    root.geometry(f"{width}x{height}+{x}+{y}")

def poll(widgets, root, last_state=[None, None]):
    idx = get_index()
    vol = get_volume_for_index(idx)
    text, color = LABELS.get(idx, (f"Mode {idx}", "#ffffff"))

    if (idx, vol) != (last_state[0], last_state[1]):
        if DISPLAY_MODE == "knob":
            draw_knob(widgets["canvas"], vol, color)
            widgets["app_label"].config(text=text, fg=color)
            resize_knob_window(widgets, root, text)   # <-- resize to fit text

        elif DISPLAY_MODE == "bar":
            widgets["vol_label"].config(text=volume_bar(vol), fg=color)
            widgets["app_label"].config(text=text, fg=color)

        else:
            vol_text = f"{vol}%" if vol is not None else "—"
            widgets["vol_label"].config(text=vol_text, fg=color)
            widgets["app_label"].config(text=text, fg=color)

        last_state[0] = idx
        last_state[1] = vol

    root.after(300, lambda: poll(widgets, root, last_state))

# --- Main ---

def main():
    if not check_single_instance():
        sys.exit(0)

    root = tk.Tk()
    root.title("DialVolumeOverlay")
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "black")
    root.config(bg="black")

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    widgets = {}

    if DISPLAY_MODE == "knob":
        knob_size = 70
        width  = knob_size + 180
        height = knob_size + 10

        x = screen_w - width - 20
        y = screen_h - height - 60
        root.geometry(f"{width}x{height}+{x}+{y}")

        frame = tk.Frame(root, bg="black")
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            frame,
            width=knob_size, height=knob_size,
            bg="black", highlightthickness=0,
        )
        canvas.pack(side="left", padx=(8, 4), pady=4)

        app_label = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 15, "bold"),
            bg="black", fg="#ffffff",
            anchor="w",
            justify="left",
        )
        app_label.pack(side="left", fill="y", padx=(0, 8))

        widgets["canvas"]    = canvas
        widgets["app_label"] = app_label
    else:
        width, height = 230, 60
        x = screen_w - width - 20
        y = screen_h - height - 60
        root.geometry(f"{width}x{height}+{x}+{y}")

        vol_label = tk.Label(
            root, text="",
            font=("Segoe UI", 10, "bold"),
            bg="black", fg="#ffffff",
            anchor="e", padx=10,
        )
        vol_label.pack(fill="x")

        app_label = tk.Label(
            root, text="",
            font=("Segoe UI", 15, "bold"),
            bg="black", fg="#ffffff",
            anchor="e", padx=10,
        )
        app_label.pack(fill="x")

        widgets["vol_label"] = vol_label
        widgets["app_label"] = app_label

    def on_close():
        try:
            os.remove(LOCK_FILE)
        except FileNotFoundError:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    
    poll(widgets, root)
    root.mainloop()

if __name__ == "__main__":
    main()