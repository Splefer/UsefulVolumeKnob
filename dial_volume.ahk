#Requires AutoHotkey v2.0

Volume_Up:: {
    Run('pythonw "C:\path\to\main.py" up',, "Hide")
}

Volume_Down:: {
    Run('pythonw "C:\path\to\main.py" down',, "Hide")
}

; Intercept knob click (mute key) — cycle target instead
Volume_Mute:: {
    Run('pythonw "C:\path\to\main.py" cycle',, "Hide")
}