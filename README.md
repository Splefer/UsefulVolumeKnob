# Dial Volume Control

A two-file app that intercepts the CORSAIR K70 CORE TKL's rotary dial and adjusts only a **target app's volume** in the Windows Volume Mixer — not the system master volume. Click the knob to cycle between target apps.
Note: Should work on every rotary dial that can increase/decrease/mute system volume, this is just the keyboard I tested it with.

***

## Requirements

### Software
- **Windows 10 or 11**
- **Python 3.8+** — [python.org/downloads](https://www.python.org/downloads/)
  - During install, check ✅ **"Add Python to PATH"**
- **AutoHotkey v2.0** — [autohotkey.com](https://www.autohotkey.com/)
- **CORSAIR iCUE** — dial must be set to **Volume Control** mode (solid white indicator light on the keyboard)
  - Again, should work with any keyboard software just make sure it is on volume control.

### Python Libraries
Open a terminal and run:
```
pip install pywin32 psutil pycaw
```

***

## Files

| File | Purpose |
|------|---------|
| `main.py` | Adjusts the target app's volume in the Windows mixer; handles mode cycling |
| `dial_volume.ahk` | Intercepts dial input and knob click, calls `main.py` (suppresses default master volume/mute behaviour) |
| `dial_state.txt` | Auto-generated — stores which target is currently active (do not edit manually) |

***

## Setup

### 1. Update the file path in `dial_volume.ahk`

Open `dial_volume.ahk` in any text editor and replace the placeholder path with the actual location of `main.py` on your machine:

```ahk
#Requires AutoHotkey v2.0

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
```

> **Tip:** Right-click `main.py` → Properties → copy the full path from the Location field, then append `\\main.py`.

### 2. Run the AutoHotkey script

Double-click `dial_volume.ahk`. A green **H** icon will appear in your system tray — this means it's running.

That's it. The dial will now control the volume of whichever target is currently active.

***

## Usage

### Rotating the dial
Rotates adjust the volume of the **currently active target** only. All other apps and master volume are unaffected.

### Clicking the knob
Each click cycles to the next target in the list:

| Click count | Active target |
|-------------|--------------|
| 0 (default) | Foreground window (whatever app is focused) |
| 1 | Spotify |
| 2 | Discord |
| 3 | Wraps back to foreground window |

> **Example:** You're in a game and a friend on Discord is hard to hear. Click the knob once to skip past Spotify, click again to land on Discord, then turn the dial up — only Discord's volume changes. Click once more to return to foreground mode.

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
| App not found in cycle mode | Check Task Manager → Details for the exact `.exe` name and update `TARGETS` in `main.py` |
| `pythonw` not found | Ensure Python is installed and added to PATH; try replacing `pythonw` with the full path e.g. `C:\\Python312\\pythonw.exe` |
| iCUE dial mode is wrong | Open iCUE → K70 CORE TKL → dial settings → set to **Volume Control** |
| Want to reset the cycle to foreground | Delete `dial_state.txt` from the app folder, or click the knob until back at default |

***

## Adjusting Sensitivity

The volume step per dial tick defaults to **5%**. To change it, open `main.py` and edit the top of the file:

```python
VOLUME_STEP = 0.05  # 0.02 = 2% per tick (finer), 0.10 = 10% per tick (coarser)
```
