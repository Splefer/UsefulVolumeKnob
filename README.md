# Dial Volume Control

A small app that intercepts the CORSAIR K70 CORE TKL's rotary dial and adjusts only a **target app's volume** in the Windows Volume Mixer — not the system master volume. Click the knob to cycle between target apps, and optionally show an on-screen indicator for the current mode.

***

## Requirements

### Software
- **Windows 10 or 11**
- **Python 3.8+** — [python.org/downloads](https://www.python.org/downloads/)
  - During install, check ✅ **"Add Python to PATH"**
- **AutoHotkey v2.0** — [autohotkey.com](https://www.autohotkey.com/)
- **CORSAIR iCUE** — dial must be set to **Volume Control** mode (solid white indicator light on the keyboard)
  - Note: This should also work with other dials that send standard volume inputs; this is just the keyboard it was tested with.

### Python Libraries
Open a terminal and run:

```py
pip install pywin32 psutil pycaw
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Adjusts the target app's volume in the Windows mixer; handles mode cycling |
| `dial_volume.ahk` | Intercepts dial input and knob click, calls `main.py`, and can optionally launch the overlay |
| `overlay.py` | Optional on-screen indicator that shows the current target mode and volume |
| `dial_state.txt` | Auto-generated — stores which target is currently active (do not edit manually) |
| `overlay.lock` | Auto-generated — prevents duplicate overlay instances (do not edit manually) |

***

## Setup

### 1. Update the file paths in `dial_volume.ahk`

Open `dial_volume.ahk` in any text editor and replace the placeholder paths with the actual locations of `main.py` and `overlay.py` on your machine:

```ahk
#Requires AutoHotkey v2.0

; === CONFIG ===
; Set to 1 to enable on-screen overlay, 0 to disable
overlayEnabled := 1
; ==============

if (overlayEnabled) {
    Run('pythonw "C:\\Users\\YourName\\dial-volume\\overlay.py"',, "Hide")
}

Volume_Up:: {
    Run('pythonw "C:\\Users\\YourName\\dial-volume\\main.py" up',, "Hide")
}

Volume_Down:: {
    Run('pythonw "C:\\Users\\YourName\\dial-volume\\main.py" down',, "Hide")
}

; Intercept knob click (mute key) — cycle target instead
Volume_Mute:: {
    Run('pythonw "C:\\Users\\YourName\\dial-volume\\main.py" cycle',, "Hide")
}

; Exit everything cleanly (overlay + this script)
Esc:: {
    WinClose("DialVolumeOverlay ahk_class TkTopLevel")
    ExitApp()
}
```

> **Tip:** Right-click `main.py` or `overlay.py` → Properties → copy the full path from the Location field, then append `\\main.py` or `\\overlay.py`.

### 2. Run the AutoHotkey script

Double-click `dial_volume.ahk`. A green **H** icon will appear in your system tray — this means it's running.

That's it. The dial will now control the volume of whichever target is currently active.

***

## Overlay indicator

The on-screen overlay is **optional**. When enabled, it shows a small always-on-top widget in the bottom-right corner of your screen with the current target and its volume level.

### Enabling or disabling the overlay

In `dial_volume.ahk`, set the flag at the top of the file:

```ahk
overlayEnabled := 1   ; show the overlay
overlayEnabled := 0   ; hide the overlay
```

### Choosing a display style

Open `overlay.py` and change `DISPLAY_MODE` near the top of the file:

```python
# Options:
#   "knob"  — circular arc that fills like a volume knob (default)
#   "bar"   — ascending block staircase  ▁▂▃▄▅▆▇█
#   "text"  — percentage number only, no graphic
DISPLAY_MODE = "knob"
```

| Mode | Appearance |
|------|-----------|
| `"knob"` | Circular arc that fills clockwise as volume increases, with percentage in the centre |
| `"bar"` | Eight ascending block characters (`▁▂▃▄▅▆▇█`) that grow as volume increases |
| `"text"` | Plain percentage number only — most minimal |

### Changing overlay colours

Each target slot has its own colour, defined in the `LABELS` dictionary in `overlay.py`. The colour applies to both the app name label and the volume indicator:

```python
LABELS = {
    0: ("🖥  Foreground", "#aaaaaa"),   # grey
    1: ("🎵  Spotify",    "#1db954"),   # Spotify green
    2: ("🎙  Discord",    "#5865f2"),   # Discord blurple
    3: ("Slot 3",         "#ffa500"),   # orange
    4: ("Slot 4",         "#ff0080"),   # pink
    5: ("Slot 5",         "#00c8ff"),   # cyan
}
```

Replace any hex colour value (e.g. `"#1db954"`) with any standard HTML hex colour. The index must match the position of the app in the `TARGETS` list.

> **Note:** If you add new apps to `TARGETS`, add a matching entry to `LABELS` in `overlay.py` at the same index, otherwise the overlay will fall back to white for that slot.

### Keeping `TARGETS` in sync

The `TARGETS` list must be **identical** in both `main.py` and `overlay.py`. `main.py` uses it to know which app to adjust; `overlay.py` uses it to know which app's volume to read and display.

***

## Usage

### Rotating the dial
Rotating the dial adjusts the volume of the **currently active target** only. All other apps and master volume are unaffected.

### Clicking the knob
Each click cycles to the next target in the list:

| Click count | Active target |
|-------------|--------------|
| 0 (default) | Foreground window (whatever app is focused) |
| 1 | Spotify |
| 2 | Discord |
| 3 | Wraps back to foreground window |

> **Example:** You're in a game and a friend on Discord is hard to hear. Click the knob once to skip past Spotify, click again to land on Discord, then turn the dial up — only Discord's volume changes. Click once more to return to foreground mode.

### Exiting cleanly
Press `Esc` while `dial_volume.ahk` is running to close both the overlay and the AHK script together.

### Adding more apps to the cycle
Open `main.py` and edit the `TARGETS` list near the top of the file:

```python
TARGETS = [
    "foreground",   # always keep this — it's the default mode
    "Spotify.exe",
    "Discord.exe",
    "vlc.exe",      # example: add any .exe name here
]
```

Then add a matching entry to `LABELS` in `overlay.py` at the same index:

```python
LABELS = {
    ...
    3: ("🎬  VLC", "#ff6600"),
}
```

To find the correct `.exe` name for any app, open **Task Manager** → Details tab and look for the process name while the app is running.

***

## Auto-Start on Boot (Optional)

To have the script start automatically when Windows loads:

1. Press `Win + R`, type `shell:startup`, and press Enter
2. Copy (or create a shortcut to) `dial_volume.ahk` into that folder

***

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dial still changes master volume | Make sure `dial_volume.ahk` is running (check system tray for H icon) |
| Knob click still mutes instead of cycling | Same as above — `dial_volume.ahk` must be running |
| No audio change when rotating | The target app may have no active audio session; make sure it is playing audio |
| App not found in cycle mode | Check Task Manager → Details for the exact `.exe` name and update `TARGETS` in both `main.py` and `overlay.py` |
| `pythonw` not found | Ensure Python is installed and added to PATH; try replacing `pythonw` with the full path e.g. `C:\\Python312\\pythonw.exe` |
| iCUE dial mode is wrong | Open iCUE → K70 CORE TKL → dial settings → set to **Volume Control** |
| Want to reset the cycle to foreground | Delete `dial_state.txt` from the app folder, or click the knob until back at default |
| Overlay is showing but not wanted | Set `overlayEnabled := 0` in `dial_volume.ahk` |
| Overlay does not appear | Make sure `overlayEnabled := 1`, `overlay.py` exists at the path in `dial_volume.ahk`, and Python can run `tkinter` |
| Two overlays stacked on screen | Run `taskkill /F /IM pythonw.exe` in a terminal to kill all instances, then relaunch `dial_volume.ahk` |
| Overlay stuck after closing AHK | Same fix — run `taskkill /F /IM pythonw.exe`, then delete `overlay.lock` from the app folder if it still exists |
| Overlay colour is wrong for a slot | Make sure the index in `LABELS` in `overlay.py` matches the position in `TARGETS` |

***

## Adjusting Sensitivity

The volume step per dial tick defaults to **5%**. To change it, open `main.py` and edit the top of the file:

```python
VOLUME_STEP = 0.05  # 0.02 = 2% per tick (finer), 0.10 = 10% per tick (coarser)
```
