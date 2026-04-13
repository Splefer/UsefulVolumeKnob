import sys
import win32gui
import win32process
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

VOLUME_STEP = 0.05

def get_foreground_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def adjust_app_volume(delta):
    target = get_foreground_process_name()
    if not target:
        return

    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == target.lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            current = volume.GetMasterVolume()
            new_vol = max(0.0, min(1.0, current + delta))
            volume.SetMasterVolume(new_vol, None)
            break

if __name__ == "__main__":
    direction = sys.argv[1] if len(sys.argv) > 1 else "up"
    delta = +VOLUME_STEP if direction == "up" else -VOLUME_STEP
    adjust_app_volume(delta)