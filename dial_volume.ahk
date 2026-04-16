#Requires AutoHotkey v2.0

; === CONFIG ===
; Set to 1 to enable on-screen overlay, 0 to disable
overlayEnabled := 1
; ==============

if (overlayEnabled) {
    Run('pythonw "C:\path\to\overlay.py"',, "Hide")
}

Volume_Up:: {
    Run('pythonw "C:\path\to\main.py" up',, "Hide")
}

Volume_Down:: {
    Run('pythonw "C:\path\to\main.py" down',, "Hide")
}

; Knob click = cycle target
Volume_Mute:: {
    Run('pythonw "C:\path\to\main.py" cycle',, "Hide")
}

; Global exit hotkey: closes this script AND overlay, keybind to close is Alt+Shift+Q
!+q:: {
    ; Try to close overlay window by title
    WinClose("DialVolumeOverlay ahk_class TkTopLevel")
    ExitApp()
}

; Hiding the overlay if it is obstructing something, default keybind is Alt+Shift+G
!+g:: {
    static overlayVisible := true
    if overlayVisible {
        WinHide("DialVolumeOverlay ahk_class TkTopLevel")
        overlayVisible := false
    } else {
        WinShow("DialVolumeOverlay ahk_class TkTopLevel")
        WinSetAlwaysOnTop(1, "DialVolumeOverlay ahk_class TkTopLevel")
        overlayVisible := true
    }
}