#Requires AutoHotkey v2.0

Volume_Up:: {
    Run('pythonw "C:\Users\raiya\Downloads\UsefulVolumeKnob\main.py" up',, "Hide")
}

Volume_Down:: {
    Run('pythonw "C:\Users\raiya\Downloads\UsefulVolumeKnob\main.py" down',, "Hide")
}
