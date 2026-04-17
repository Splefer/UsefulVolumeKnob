# setup.py — Dial Volume Control installer & configurator
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import json
import shutil

APP_FOLDER_NAME = "UsefulVolumeKnob"
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# ── Default colours for new TARGETS slots ──────────────────────────────────
DEFAULT_COLORS = ["#ffa500", "#ff0080", "#00c8ff", "#ff4444", "#aa44ff", "#00ffaa"]

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_config.json")

# ── Helpers ─────────────────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def find_file_in_dir(folder, filename):
    path = os.path.join(folder, filename)
    return path if os.path.isfile(path) else None

# ── Patch helpers ────────────────────────────────────────────────────────────

def patch_targets_and_mode(filepath, targets, display_mode, labels, volume_step=None):
    """Rewrite TARGETS, DISPLAY_MODE, LABELS (and optionally VOLUME_STEP) in a .py file."""
    with open(filepath, "r", encoding="utf-8") as f:
        src = f.read()

    # TARGETS block
    targets_str = "TARGETS = [\n"
    for t in targets:
        targets_str += f'    "{t}",\n'
    targets_str += "]"
    src = re.sub(r"TARGETS\s*=\s*\[.*?\]", targets_str, src, flags=re.DOTALL)

    # DISPLAY_MODE (overlay only)
    if display_mode is not None:
        src = re.sub(r'DISPLAY_MODE\s*=\s*"[^"]*"', f'DISPLAY_MODE = "{display_mode}"', src)

    # LABELS (overlay only)
    if labels is not None:
        labels_str = "LABELS = {\n"
        for idx, (text, color) in labels.items():
            escaped = text.replace('"', '\\"')
            labels_str += f'    {idx}: ("{escaped}", "{color}"),\n'
        labels_str += "}"
        src = re.sub(r"LABELS\s*=\s*\{.*?\}", labels_str, src, flags=re.DOTALL)

    # VOLUME_STEP (main only)
    if volume_step is not None:
        src = re.sub(r"VOLUME_STEP\s*=\s*[\d.]+", f"VOLUME_STEP = {volume_step}", src)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(src)

def write_ahk(folder, main_path, overlay_path, overlay_enabled):
    ahk_path = os.path.join(folder, "dial_volume.ahk")
    enabled_val = 1 if overlay_enabled else 0
    content = f"""#Requires AutoHotkey v2.0

; === CONFIG ===
; Set to 1 to enable on-screen overlay, 0 to disable
overlayEnabled := {enabled_val}
; ==============

if (overlayEnabled) {{
    Run('pythonw "{overlay_path}"',, "Hide")
}}

Volume_Up:: {{
    Run('pythonw "{main_path}" up',, "Hide")
}}

Volume_Down:: {{
    Run('pythonw "{main_path}" down',, "Hide")
}}

; Intercept knob click (mute key) — cycle target instead
Volume_Mute:: {{
    Run('pythonw "{main_path}" cycle',, "Hide")
}}

; Exit everything cleanly (overlay + this script)
Esc:: {{
    WinClose("DialVolumeOverlay ahk_class TkTopLevel")
    ExitApp()
}}
"""
    with open(ahk_path, "w", encoding="utf-8") as f:
        f.write(content)
    return ahk_path

# ── GUI ──────────────────────────────────────────────────────────────────────
def ensure_app_installed(parent_folder):
    """
    Ensure that parent_folder\\UsefulVolumeKnob exists and contains
    main.py and overlay.py copied from the setup.py directory.

    Returns the full app folder path.
    """
    app_folder = os.path.join(parent_folder, APP_FOLDER_NAME)
    os.makedirs(app_folder, exist_ok=True)

    # Source files live next to setup.py
    src_main = os.path.join(THIS_DIR, "main.py")
    src_overlay = os.path.join(THIS_DIR, "overlay.py")

    if not os.path.isfile(src_main):
        raise FileNotFoundError(f"main.py not found next to setup.py ({src_main})")
    if not os.path.isfile(src_overlay):
        raise FileNotFoundError(f"overlay.py not found next to setup.py ({src_overlay})")

    dst_main = os.path.join(app_folder, "main.py")
    dst_overlay = os.path.join(app_folder, "overlay.py")

    shutil.copy2(src_main, dst_main)
    shutil.copy2(src_overlay, dst_overlay)

    return app_folder

class SetupApp:
    def __init__(self, root):
        self.root = root
        root.title("Dial Volume Control — Setup")
        root.resizable(False, False)
        root.configure(bg="#1e1e1e")

        self.cfg = load_config()

        # ── style ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel",       background="#1e1e1e", foreground="#cccccc", font=("Segoe UI", 10))
        style.configure("TFrame",       background="#1e1e1e")
        style.configure("TButton",      background="#2d2d2d", foreground="#ffffff", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry",       fieldbackground="#2d2d2d", foreground="#ffffff", insertcolor="#ffffff")
        style.configure("TCombobox",    fieldbackground="#2d2d2d", foreground="#ffffff")
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#cccccc")
        style.map("TButton", background=[("active", "#3d3d3d")])

        pad = {"padx": 10, "pady": 5}

        # ── Section: Install folder ──
        self._section("📁 Install location (parent folder)", 0)
        self.folder_var = tk.StringVar(value=self.cfg.get("folder", ""))
        folder_frame = ttk.Frame(root)
        folder_frame.grid(row=1, column=0, columnspan=3, sticky="ew", **pad)
        ttk.Entry(folder_frame, textvariable=self.folder_var, width=52).pack(side="left", padx=(0,6))
        ttk.Button(folder_frame, text="Browse…", command=self._browse_folder).pack(side="left")

        # ── Section: Overlay toggle ──
        self._section("🖥  Overlay", 2)
        self.overlay_var = tk.BooleanVar(value=self.cfg.get("overlay_enabled", True))
        ttk.Checkbutton(root, text="Enable on-screen overlay", variable=self.overlay_var).grid(
            row=3, column=0, columnspan=3, sticky="w", **pad)

        # ── Section: Display mode ──
        self._section("🎨  Overlay display mode", 4)
        self.mode_var = tk.StringVar(value=self.cfg.get("display_mode", "knob"))
        mode_frame = ttk.Frame(root)
        mode_frame.grid(row=5, column=0, columnspan=3, sticky="w", **pad)
        for val, label in [("knob", "Knob  (circular arc)"),
                            ("bar",  "Bar   (▁▂▃▄▅▆▇█)"),
                            ("text", "Text  (% only)")]:
            ttk.Radiobutton(mode_frame, text=label, variable=self.mode_var, value=val).pack(anchor="w")

        # ── Section: Volume step ──
        self._section("🔊  Volume step per dial tick", 6)
        self.step_var = tk.StringVar(value=str(self.cfg.get("volume_step", 0.05)))
        step_frame = ttk.Frame(root)
        step_frame.grid(row=7, column=0, columnspan=3, sticky="w", **pad)
        ttk.Entry(step_frame, textvariable=self.step_var, width=8).pack(side="left", padx=(0,8))
        ttk.Label(step_frame, text="e.g. 0.05 = 5%  |  0.02 = 2%  |  0.10 = 10%").pack(side="left")

        # ── Section: Target apps ──
        self._section("🎯  Target apps (dial cycle)", 8)

        list_frame = ttk.Frame(root)
        list_frame.grid(row=9, column=0, columnspan=3, sticky="ew", **pad)

        saved_targets = self.cfg.get("targets", ["foreground", "Spotify.exe", "Discord.exe"])
        saved_labels  = self.cfg.get("labels",  {})

        self.target_rows = []   # list of (exe_var, label_var, color_var, row_frame)
        self.targets_frame = ttk.Frame(list_frame)
        self.targets_frame.pack(fill="x")

        for i, exe in enumerate(saved_targets):
            lbl_text  = saved_labels.get(str(i), [None, None])[0] or ("🖥  Foreground" if exe == "foreground" else exe.replace(".exe","").capitalize())
            lbl_color = saved_labels.get(str(i), [None, None])[1] or "#aaaaaa"
            self._add_target_row(exe, lbl_text, lbl_color)

        btn_row = ttk.Frame(list_frame)
        btn_row.pack(fill="x", pady=(6,0))
        ttk.Button(btn_row, text="+ Add app", command=self._add_empty_row).pack(side="left", padx=(0,6))
        ttk.Label(btn_row, text="'foreground' = whatever window is focused", foreground="#666666").pack(side="left")

        # ── Apply button ──
        ttk.Button(root, text="✅  Save & apply", command=self._apply).grid(
            row=10, column=0, columnspan=3, pady=16)

        root.columnconfigure(0, weight=1)

    def _section(self, title, row):
        ttk.Label(self.root, text=title, font=("Segoe UI", 10, "bold"),
                  foreground="#ffffff").grid(row=row, column=0, columnspan=3,
                                             sticky="w", padx=10, pady=(12,0))

    def _add_target_row(self, exe="", label_text="", color="#aaaaaa"):
        row_frame = ttk.Frame(self.targets_frame)
        row_frame.pack(fill="x", pady=2)

        exe_var   = tk.StringVar(value=exe)
        label_var = tk.StringVar(value=label_text)
        color_var = tk.StringVar(value=color)

        is_fg = exe == "foreground"

        ttk.Label(row_frame, text=".exe name:", width=10).pack(side="left")
        exe_entry = ttk.Entry(row_frame, textvariable=exe_var, width=18)
        exe_entry.pack(side="left", padx=(0,6))
        if is_fg:
            exe_entry.config(state="disabled")

        ttk.Label(row_frame, text="Label:").pack(side="left")
        ttk.Entry(row_frame, textvariable=label_var, width=16).pack(side="left", padx=(0,6))

        ttk.Label(row_frame, text="Colour:").pack(side="left")
        color_entry = tk.Entry(row_frame, textvariable=color_var, width=9,
                               bg=color, fg="#ffffff", insertbackground="#ffffff",
                               font=("Segoe UI", 10))
        color_entry.pack(side="left", padx=(0,6))

        # Live colour preview on the entry background
        def on_color_change(*_):
            try:
                color_entry.config(bg=color_var.get())
            except:
                pass
        color_var.trace_add("write", on_color_change)

        if not is_fg:
            ttk.Button(row_frame, text="✕", width=2,
                       command=lambda f=row_frame, r=(exe_var,label_var,color_var,None): self._remove_row(f, r)
                       ).pack(side="left")

        self.target_rows.append((exe_var, label_var, color_var, row_frame))

    def _remove_row(self, frame, row_data):
        frame.destroy()
        self.target_rows = [r for r in self.target_rows if r[3] is not frame]

    def _add_empty_row(self):
        idx   = len(self.target_rows)
        color = DEFAULT_COLORS[(idx - 1) % len(DEFAULT_COLORS)]
        self._add_target_row("", f"Slot {idx}", color)

    def _browse_folder(self):
        folder = filedialog.askdirectory(
            title="Select the folder where UsefulVolumeKnob should be installed"
        )
        if folder:
            self.folder_var.set(folder)

    def _apply(self):
        parent_folder = self.folder_var.get().strip()
        if not parent_folder or not os.path.isdir(parent_folder):
            messagebox.showerror(
                "Error",
                "Please choose a valid folder to install UsefulVolumeKnob into."
            )
            return

        try:
            # This will create parent_folder\\UsefulVolumeKnob and copy main/overlay into it.
            app_folder = ensure_app_installed(parent_folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install files:\n{e}")
            return

        # From this point on, treat app_folder as the “dial-volume app folder”
        folder = app_folder

        main_path = find_file_in_dir(folder, "main.py")
        overlay_path = find_file_in_dir(folder, "overlay.py")

        if not main_path:
            messagebox.showerror("Error", f"main.py not found in:\n{folder}")
            return
        if not overlay_path:
            messagebox.showerror("Error", f"overlay.py not found in:\n{folder}")
            return

        # Collect targets and labels
        targets = []
        labels  = {}
        for i, (exe_var, label_var, color_var, _) in enumerate(self.target_rows):
            exe = exe_var.get().strip()
            if not exe:
                continue
            targets.append(exe)
            labels[i] = (label_var.get().strip() or exe, color_var.get().strip() or "#ffffff")

        if not targets:
            messagebox.showerror("Error", "You need at least one target app.")
            return

        try:
            step = float(self.step_var.get())
            assert 0 < step <= 1
        except:
            messagebox.showerror("Error", "Volume step must be a number between 0.01 and 1.0 (e.g. 0.05).")
            return

        display_mode = self.mode_var.get()
        overlay_enabled = self.overlay_var.get()

        # Patch main.py
        patch_targets_and_mode(main_path, targets, display_mode=None, labels=None, volume_step=step)

        # Patch overlay.py
        patch_targets_and_mode(overlay_path, targets, display_mode=display_mode, labels=labels)

        # Write dial_volume.ahk
        # Use Windows-style double-backslash paths for AHK
        main_ahk    = main_path.replace("/", "\\")
        overlay_ahk = overlay_path.replace("/", "\\")
        ahk_path = write_ahk(folder, main_ahk, overlay_ahk, overlay_enabled)

        # Save config for next run
        save_config({
            "folder":          folder,
            "overlay_enabled": overlay_enabled,
            "display_mode":    display_mode,
            "volume_step":     step,
            "targets":         targets,
            "labels":          {str(k): list(v) for k, v in labels.items()},
        })

        messagebox.showinfo(
            "Done!",
            f"All files updated.\n\n"
            f"main.py      ✅\n"
            f"overlay.py   ✅\n"
            f"dial_volume.ahk  ✅\n\n"
            f"Double-click dial_volume.ahk to launch."
        )

if __name__ == "__main__":
    root = tk.Tk()
    SetupApp(root)
    root.mainloop()
