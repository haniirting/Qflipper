# Flipper Phone Desk (PC)

Connects Flipper Phone to this PC over USB through adb and manages it:
- Archive and saved remotes: list, download, delete
- Bad USB: upload a script and run it on the phone (the phone then types it on a paired PC over Bluetooth)
- Open the Apps screen on the phone

## Before you start
1. Install Android platform-tools (adb) and add the folder to PATH. Check: `adb version`.
2. On the phone: Settings → About phone → tap MIUI version 7 times; then Developer options → USB debugging on.
3. Install the **debug** build of Flipper Phone (the `Flipper-Phone.apk` from the GitHub Releases, not a release build).
4. Connect the phone with a USB cable and accept "Allow USB debugging" on the phone.

## Run
    python flipper_phone_desk.py

## Test without a phone
    python test_desk.py

## Limits
- NFC and infrared are the phone's own hardware: they are used only with the phone in hand.
- Works with the debug build only (run-as needs a debuggable app).
- Bad USB needs the phone paired with the PC over Bluetooth, and the phone screen open while it types.
- The file transfer commands were checked by a command test only; test them once on your phone.
