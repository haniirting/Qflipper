"""Flipper Phone on the PC: shows the screen of Flipper Phone and sends your mouse and keyboard to it.

Works over USB with adb (Android Debug Bridge). Needs USB debugging on the phone and adb in PATH.
Clicks on the picture become taps on the phone; arrow keys, Enter and Esc become D-pad / OK / Back.
NFC and infrared still use the phone's own hardware, so the phone must be in range of the card/IR target.
"""
import base64
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

PKG = "com.example.nfcuid"
KEYS = {"Up": 19, "Down": 20, "Left": 21, "Right": 22, "Return": 66, "KP_Enter": 66, "Escape": 4, "BackSpace": 67}


class AdbError(Exception):
    pass


def adb(*args, timeout=20):
    try:
        r = subprocess.run(["adb", *args], capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise AdbError("adb was not found. Install Android platform-tools and add them to PATH.")
    if r.returncode != 0:
        raise AdbError((r.stderr or r.stdout).decode("utf-8", "replace").strip() or "adb failed")
    return r.stdout


def connected_phone():
    out = adb("devices").decode("utf-8", "replace")
    ids = [l.split()[0] for l in out.splitlines()[1:] if l.strip().endswith("\tdevice")]
    if not ids:
        raise AdbError("no phone found: turn on USB debugging and allow it on the phone")
    return ids[0]


def screen_size():
    """Returns (width, height) of the phone screen in pixels, e.g. (1080, 2340)."""
    out = adb("shell", "wm size").decode("utf-8", "replace")
    part = out.strip().splitlines()[-1].split(":")[-1].strip()
    w, h = part.split("x")
    return int(w), int(h)


def screenshot_png():
    return adb("exec-out", "screencap", "-p", timeout=15)


def tap(x, y):
    adb("shell", "input", "tap", str(x), str(y))


def key(code):
    adb("shell", "input", "keyevent", str(code))


def launch():
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")


class Mirror(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flipper Phone (PC)")
        self.configure(bg="#161616")
        self.status = tk.StringVar(value="Connecting...")
        self.size = None
        self.auto = True
        self.busy = False
        self.image = None
        self.label = tk.Label(self, bg="#000", cursor="crosshair")
        self.label.pack(padx=10, pady=10)
        self.label.bind("<Button-1>", self.on_click)
        bar = tk.Frame(self, bg="#161616")
        bar.pack(fill="x", padx=10)
        for text, cmd in (("Launch app", self.do_launch), ("Back", lambda: self.send_key(4)),
                          ("Home", lambda: self.send_key(3)), ("Refresh", self.refresh),
                          ("Auto: on", self.toggle_auto)):
            b = tk.Button(bar, text=text, command=cmd, bg="#2B2B2B", fg="#F2F2F2",
                          activebackground="#444", relief="flat", padx=8, pady=4)
            b.pack(side="left", padx=3, pady=4)
            if text.startswith("Auto"):
                self.auto_btn = b
        tk.Label(self, textvariable=self.status, bg="#161616", fg="#9A9A9A", anchor="w").pack(fill="x", padx=10, pady=(0, 8))
        for k in KEYS:
            self.bind("<Key-%s>" % k, self.on_key)
        self.focus_force()
        self.after(100, self.start)

    def start(self):
        self.run_bg(self._init, self._ready)

    def _init(self):
        connected_phone()
        return screen_size()

    def _ready(self, size):
        self.size = size
        self.status.set("Connected: screen %dx%d. Click the picture to tap." % size)
        self.refresh()
        self.tick()

    def run_bg(self, fn, done=None):
        def work():
            try:
                res = fn()
            except AdbError as e:
                self.after(0, lambda: self.status.set("Error: %s" % e))
                return
            except Exception as e:
                self.after(0, lambda: self.status.set("Error: %s" % e))
                return
            if done:
                self.after(0, lambda: done(res))
        threading.Thread(target=work, daemon=True).start()

    def refresh(self):
        if self.busy or self.size is None:
            return
        self.busy = True

        def grab():
            return screenshot_png()

        def show(png):
            self.busy = False
            self.image = tk.PhotoImage(data=base64.b64encode(png).decode("ascii"), format="png")
            self.label.configure(image=self.image)

        self.run_bg(grab, show)

    def tick(self):
        if self.auto:
            self.refresh()
        self.after(1200, self.tick)

    def toggle_auto(self):
        self.auto = not self.auto
        self.auto_btn.configure(text="Auto: on" if self.auto else "Auto: off")

    def to_device(self, x, y):
        """Maps a point on the picture to a point on the phone screen."""
        dw, dh = self.size
        iw, ih = self.image.width(), self.image.height()
        return int(x * dw / iw), int(y * dh / ih)

    def on_click(self, e):
        if self.size is None or self.image is None:
            return
        x, y = self.to_device(e.x, e.y)
        self.run_bg(lambda: tap(x, y), lambda _: self.status.set("Tap at %d, %d" % (x, y)))
        self.after(400, self.refresh)

    def on_key(self, e):
        code = KEYS.get(e.keysym)
        if code is not None:
            self.send_key(code)

    def send_key(self, code):
        self.run_bg(lambda: key(code), lambda _: self.status.set("Key %d sent" % code))
        self.after(400, self.refresh)

    def do_launch(self):
        self.run_bg(launch, lambda _: self.status.set("Flipper Phone started"))
        self.after(1500, self.refresh)


def main():
    Mirror().mainloop()


if __name__ == "__main__":
    main()
