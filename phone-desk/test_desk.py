"""Checks the adb commands without a phone: replaces subprocess.run with a recorder."""
import sys
import types

# tkinter is not needed to test the adb commands: stub it so the module imports without a display
_tk = types.ModuleType("tkinter")
for _n in ("Tk", "Frame", "Label", "Listbox", "Button", "StringVar"):
    setattr(_tk, _n, type(_n, (), {"__init__": lambda self, *a, **k: None}))
_fd = types.ModuleType("tkinter.filedialog")
_mb = types.ModuleType("tkinter.messagebox")
sys.modules.update({"tkinter": _tk, "tkinter.filedialog": _fd, "tkinter.messagebox": _mb})

import subprocess
import flipper_phone_desk as d

calls = []


class R:
    def __init__(self, out=b"", code=0, err=b""):
        self.stdout, self.returncode, self.stderr = out, code, err


def fake(out=b""):
    def run(args, input=None, capture_output=None, timeout=None):
        calls.append((args, input))
        return R(out)
    return run


subprocess.run = fake(b"List of devices attached\nABC123\tdevice\nXYZ\toffline\n")
assert d.devices() == ["ABC123"]

subprocess.run = fake(b"archive_1.nfc\nbad.txt\n")
assert d.list_dir("files/archive") == ["archive_1.nfc", "bad.txt"]
assert calls[-1][0] == ["adb", "shell", "run-as com.example.nfcuid ls -1 files/archive"]

subprocess.run = fake(b"DATA")
assert d.pull("files/archive/a.nfc") == b"DATA"
assert calls[-1][0] == ["adb", "exec-out", "run-as com.example.nfcuid cat files/archive/a.nfc"]

subprocess.run = fake()
d.push("badusb.txt", b"STRING hi\n")
assert calls[-1][1] == b"STRING hi\n"
assert calls[-1][0][:2] == ["adb", "shell"] and "cat > badusb.txt" in calls[-1][0][2]

subprocess.run = fake()
d.start_badusb()
assert calls[-1][0] == ["adb", "shell", "am start -n com.example.nfcuid/.BadUsbActivity --es file badusb.txt"]

d.delete("files/archive/a.nfc")
assert "rm -f files/archive/a.nfc" in calls[-1][0][2]
print("PHONE DESK COMMAND TESTS PASSED")
