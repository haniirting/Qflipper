"""Flipper Phone Desk: connect Flipper Phone to this PC over USB and manage it.

Uses adb (Android Debug Bridge). The phone needs USB debugging on and the debug build of
Flipper Phone (the one built by the GitHub workflow), because it reads the app's own folder with run-as.

What it does: list / download / delete saved keys (Archive) and saved IR remotes, upload a Bad USB
script and run it on the phone, open the Apps screen. NFC and IR are hardware of the phone itself,
so they work only with the phone in hand.
"""
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

PKG = "com.example.nfcuid"
ACT_BADUSB = PKG + "/.BadUsbActivity"
ACT_APPS = PKG + "/.AppsActivity"
ARCHIVE = "files/archive"
REMOTES = "files/remotes"
SCRIPT_FILE = "badusb.txt"


class AdbError(Exception):
    pass


def adb(*args, input_bytes=None, timeout=60):
    try:
        r = subprocess.run(["adb", *args], input=input_bytes, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise AdbError("adb was not found. Install Android platform-tools and add them to PATH.")
    if r.returncode != 0:
        raise AdbError((r.stderr or r.stdout).decode("utf-8", "replace").strip() or "adb failed")
    return r.stdout


def devices():
    """Returns the serial numbers of phones that are connected and authorized."""
    out = adb("devices").decode("utf-8", "replace")
    return [l.split()[0] for l in out.splitlines()[1:] if l.strip().endswith("\tdevice")]


def list_dir(path):
    out = adb("shell", "run-as %s ls -1 %s" % (PKG, path)).decode("utf-8", "replace")
    return sorted(l.strip() for l in out.splitlines() if l.strip() and "No such" not in l)


def pull(path):
    return adb("exec-out", "run-as %s cat %s" % (PKG, path), timeout=120)


def push(path, data):
    adb("shell", "run-as %s sh -c 'cat > %s'" % (PKG, path), input_bytes=data, timeout=120)


def delete(path):
    adb("shell", "run-as %s rm -f %s" % (PKG, path))


def start_badusb():
    adb("shell", "am start -n %s --es file %s" % (ACT_BADUSB, SCRIPT_FILE))


def open_apps():
    adb("shell", "am start -n %s" % ACT_APPS)


# ---------- window ----------
ORANGE = "#FF8200"
DARK = "#161616"
PANEL = "#212121"
TEXT = "#F2F2F2"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flipper Phone Desk")
        self.configure(bg=DARK)
        self.geometry("720x480")
        self.state_var = tk.StringVar(value="Connect the phone with USB debugging on")
        self.folder = ARCHIVE
        self._build()
        self.refresh()

    def _build(self):
        head = tk.Frame(self, bg=DARK)
        head.pack(fill="x", padx=16, pady=12)
        tk.Label(head, text="Flipper Phone", bg=DARK, fg=ORANGE, font=("Segoe UI", 18, "bold")).pack(side="left")
        self._btn(head, "Refresh", self.refresh).pack(side="right")
        tk.Label(self, textvariable=self.state_var, bg=DARK, fg=TEXT, font=("Segoe UI", 10), anchor="w").pack(
            fill="x", padx=16)

        body = tk.Frame(self, bg=DARK)
        body.pack(fill="both", expand=True, padx=16, pady=10)
        self.box = tk.Listbox(body, bg=PANEL, fg=TEXT, selectbackground=ORANGE, selectforeground="#000",
                              font=("Consolas", 11), relief="flat", highlightthickness=0)
        self.box.pack(side="left", fill="both", expand=True)
        side = tk.Frame(body, bg=DARK)
        side.pack(side="right", fill="y", padx=(12, 0))
        self._btn(side, "Archive (.nfc, .ir)", lambda: self.show_folder(ARCHIVE)).pack(fill="x", pady=2)
        self._btn(side, "Saved remotes", lambda: self.show_folder(REMOTES)).pack(fill="x", pady=2)
        self._btn(side, "Download selected", self.download).pack(fill="x", pady=2)
        self._btn(side, "Delete selected", self.delete).pack(fill="x", pady=2)
        self._btn(side, "Upload Bad USB script", self.upload_script).pack(fill="x", pady=(14, 2))
        self._btn(side, "Run script on phone", self.run_script).pack(fill="x", pady=2)
        self._btn(side, "Open Apps on phone", self.open_apps).pack(fill="x", pady=(14, 2))

    def _btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=PANEL, fg=TEXT, activebackground="#333",
                         activeforeground=ORANGE, relief="flat", font=("Segoe UI", 10, "bold"), padx=10, pady=6)

    def run_bg(self, fn, done=None):
        def work():
            try:
                res = fn()
            except AdbError as e:
                self.after(0, lambda: self.state_var.set("Error: %s" % e))
                return
            except Exception as e:
                self.after(0, lambda: self.state_var.set("Error: %s" % e))
                return
            if done:
                self.after(0, lambda: done(res))
        threading.Thread(target=work, daemon=True).start()

    def refresh(self):
        def check():
            ids = devices()
            if not ids:
                raise AdbError("no phone found (turn on USB debugging and accept the prompt on the phone)")
            return ids
        self.run_bg(check, lambda ids: (self.state_var.set("Connected: %s" % ids[0]), self.show_folder(self.folder)))

    def show_folder(self, folder):
        self.folder = folder
        self.box.delete(0, "end")
        self.run_bg(lambda: list_dir(folder), self._fill)

    def _fill(self, names):
        self.box.delete(0, "end")
        for n in names:
            self.box.insert("end", n)
        self.state_var.set("%s: %d files" % (self.folder, len(names)))

    def _selected(self):
        sel = self.box.curselection()
        if not sel:
            self.state_var.set("Select a file first")
            return None
        return self.box.get(sel[0])

    def download(self):
        name = self._selected()
        if not name:
            return
        dest = filedialog.asksaveasfilename(initialfile=name)
        if not dest:
            return
        path = "%s/%s" % (self.folder, name)

        def work():
            data = pull(path)
            with open(dest, "wb") as f:
                f.write(data)
            return "Saved %s (%d bytes)" % (dest, len(data))
        self.run_bg(work, self.state_var.set)

    def delete(self):
        name = self._selected()
        if not name or not messagebox.askyesno("Delete", "Delete %s from the phone?" % name):
            return
        path = "%s/%s" % (self.folder, name)
        self.run_bg(lambda: delete(path), lambda _: (self.state_var.set("Deleted %s" % name), self.show_folder(self.folder)))

    def upload_script(self):
        src = filedialog.askopenfilename(filetypes=[("Bad USB script", "*.txt"), ("All files", "*.*")])
        if not src:
            return
        with open(src, "rb") as f:
            data = f.read()
        if len(data) > 500_000:
            messagebox.showerror("Upload", "Script is too large (max 500 KB)")
            return
        self.run_bg(lambda: push(SCRIPT_FILE, data),
                    lambda _: self.state_var.set("Script uploaded to the phone. Press Run script on phone."))

    def run_script(self):
        self.run_bg(start_badusb, lambda _: self.state_var.set("Bad USB opened on the phone: connect to the PC there"))

    def open_apps(self):
        self.run_bg(open_apps, lambda _: self.state_var.set("Apps opened on the phone"))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
