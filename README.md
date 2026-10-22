# Flipper PC apps

Desktop programs for the Flipper Zero ecosystem, written in Python (tkinter):

| Folder | What it is | Needs |
| --- | --- | --- |
| `flipper-desk/` | Flipper Desk: manages a real Flipper over USB or through the Flipper Link phone app (files, remote screen, GPIO, apps) | Flipper Zero, or a phone with Flipper Link + adb |
| `phone-desk/` | Flipper Phone Desk: files of the Flipper Phone app (Archive, saved remotes), Bad USB script upload | Phone with the debug build of Flipper Phone + adb |
| `phone-mirror/` | Flipper Phone mirror: shows the Flipper Phone screen on the PC and sends mouse and keys to it | Phone with Flipper Phone + adb |

All three use Python 3.8+ with tkinter. `flipper-desk` also needs `pyserial` for the USB cable mode.

## Run
    python flipper-desk/flipper_desk.py
    python phone-desk/flipper_phone_desk.py
    python phone-mirror/flipper_phone_mirror.py

## Tests (no hardware needed)
    python flipper-desk/test_rpc.py
    python phone-desk/test_desk.py
    python phone-mirror/test_mirror.py

Windows builds (`.exe`) are produced by the GitHub Actions workflow in `.github/workflows/ci.yml` and attached to the run as artifacts.

## Releases from the repository (no computer needed to build)
1. Upload `flipper-pc.zip` to the repository root: Add file → Upload files (do not unzip it).
2. Actions → "Unpack and release" → Run workflow. Optionally enter a version such as `1.0.0`.
3. The workflow unpacks the archive into the repository, commits, runs the tests, builds the three `.exe` files and publishes them in Releases.

## License
GPL-3.0 (see `LICENSE`). `flipper-desk` contains icons and dolphin frames taken from the Flipper firmware (GPL-3.0). The Flipper name and logo are trademarks of Flipper Devices Inc.; this is an unofficial fan project.
