"""Checks the adb commands and the click mapping without a phone or a display."""
import subprocess
import sys
import types

_tk = types.ModuleType("tkinter")
for _n in ("Tk", "Frame", "Label", "Button", "StringVar", "PhotoImage"):
    setattr(_tk, _n, type(_n, (), {"__init__": lambda self, *a, **k: None}))
_mb = types.ModuleType("tkinter.messagebox")
sys.modules.update({"tkinter": _tk, "tkinter.messagebox": _mb})

import flipper_phone_mirror as m

calls = []


class R:
    def __init__(self, out=b""):
        self.stdout, self.returncode, self.stderr = out, 0, b""


def fake(out=b""):
    def run(args, capture_output=None, timeout=None):
        calls.append(args)
        return R(out)
    return run


subprocess.run = fake(b"List of devices attached\nABC\tdevice\nXYZ\toffline\n")
assert m.connected_phone() == "ABC"

subprocess.run = fake(b"Physical size: 1080x2340\n")
assert m.screen_size() == (1080, 2340)

subprocess.run = fake()
m.tap(540, 1170)
assert calls[-1] == ["adb", "shell", "input", "tap", "540", "1170"]
m.key(66)
assert calls[-1] == ["adb", "shell", "input", "keyevent", "66"]
m.launch()
assert calls[-1][:3] == ["adb", "shell", "monkey"] and "com.example.nfcuid" in calls[-1]

subprocess.run = fake(b"\x89PNG")
assert m.screenshot_png() == b"\x89PNG"
assert calls[-1] == ["adb", "exec-out", "screencap", "-p"]

# click mapping: picture 540x1170 shows a 1080x2340 screen -> a click at (100, 200) is (200, 400)
class Img:
    def width(self): return 540
    def height(self): return 1170


class Fake(m.Mirror):
    def __init__(self):
        self.size = (1080, 2340)
        self.image = Img()


f = Fake()
assert f.to_device(100, 200) == (200, 400)
assert f.to_device(540, 1170) == (1080, 2340)
print("PHONE MIRROR TESTS PASSED")
