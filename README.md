# Dial Volume Control

A two-file app that intercepts the CORSAIR K70 CORE TKL's rotary dial and adjusts only the **focused app's volume** in the Windows Volume Mixer — not the system master volume.

***

## Requirements

### Software
- **Windows 10 or 11**
- **Python 3.8+** — [python.org/downloads](https://www.python.org/downloads/)
  - During install, check **"Add Python to PATH"**
- **AutoHotkey v2.0** — [autohotkey.com](https://www.autohotkey.com/)
- **CORSAIR iCUE** — dial must be set to **Volume Control** mode (solid white indicator light on the keyboard)
  - Note: Should work on every other dial that has volume control, this is just the one I tested it with.

### Python Libraries
Open a terminal and run:
```
pip install pywin32 psutil pycaw
```

***

## Files

| File | Purpose |
|------|---------|
| `main.py` | Adjusts the focused app's volume in the Windows mixer |
| `dial_volume.ahk` | Intercepts dial input and calls `main.py` (suppresses default master volume behaviour) |

***

## Setup

### 1. Update the file path in `dial_volume.ahk`

Open `dial_volume.ahk` in any text editor and replace the placeholder path with the actual location of `main.py` on your machine:

```ahk
#Requires AutoHotkey v2.0

Volume_Up:: {
    Run('pythonw "C:\Users\YourName\dial-volume\main.py" up',, "Hide")
}

Volume_Down:: {
    Run('pythonw "C:\Users\YourName\dial-volume\main.py" down',, "Hide")
}
```

> **Tip:** Right-click `main.py` → Properties → copy the full path from the Location field, then append `\main.py`.

### 2. Run the AutoHotkey script

Double-click `dial_volume.ahk`. A green **H** icon will appear in your system tray — this means it's running.

That's it. The dial will now control the volume of whichever app is in the foreground.

***

## Usage

1. Tab into any app that is playing audio (game, browser, music player, etc.)
2. Rotate the dial — volume changes apply **only to that app** in the mixer
3. Tab into a different app and rotate — that app's volume is adjusted instead
4. Master volume and other apps are unaffected

> **Example:** You're in a game call and the game is too loud. Tab into the game window, turn the dial down, then tab back to your call. Your friend's voice is now clearer without you ever opening the volume mixer.

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
| `No active audio session found` | The focused app has no audio playing at that moment — play some audio first |
| App volume not found for a game | Some games register audio under a different process name; check Task Manager for the exact `.exe` name |
| `pythonw` not found | Ensure Python is installed and added to PATH; try replacing `pythonw` with the full path e.g. `C:\Python312\pythonw.exe` |
| iCUE dial mode is wrong | Open iCUE → K70 CORE TKL → dial settings → set to **Volume Control** |

***

## Adjusting Sensitivity

The volume step per dial tick defaults to **5%**. To change it, open `main.py` and edit line 6:

```python
VOLUME_STEP = 0.05  # 0.02 = 2% per tick (finer), 0.10 = 10% per tick (coarser)
```
