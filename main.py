import sys
import os
import win32gui
import win32process
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

VOLUME_STEP = 0.05

# --- Target list: add/remove entries here to expand ---
# "foreground" is a special keyword meaning the active window
TARGETS = [
    "foreground",
    "Spotify.exe",
    "Discord.exe",
]

# Store current mode index in a file next to this script
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dial_state.txt")


def get_current_index():
    try:
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0  # default to foreground


def set_current_index(index):
    with open(STATE_FILE, "w") as f:
        f.write(str(index))


def get_foreground_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def adjust_app_volume(delta):
    index = get_current_index()
    target_entry = TARGETS[index]

    if target_entry == "foreground":
        target = get_foreground_process_name()
    else:
        target = target_entry

    if not target:
        return

    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == target.lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            current = volume.GetMasterVolume()
            new_vol = max(0.0, min(1.0, current + delta))
            volume.SetMasterVolume(new_vol, None)
            print(f"[{target_entry}] {target} → {int(new_vol * 100)}%")
            break


def cycle_target():
    index = get_current_index()
    next_index = (index + 1) % len(TARGETS)
    set_current_index(next_index)
    print(f"Switched to: {TARGETS[next_index]}")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "up"
    if action == "cycle":
        cycle_target()
    else:
        delta = +VOLUME_STEP if action == "up" else -VOLUME_STEP
        adjust_app_volume(delta)