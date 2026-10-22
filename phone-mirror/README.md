# Flipper Phone on PC (mirror)

Shows the screen of Flipper Phone on this PC and sends your mouse and keyboard to it, over USB with adb.

## Before you start
1. Install Android platform-tools (adb) and add the folder to PATH. Check: `adb version`.
2. On the phone: Settings → About phone → tap MIUI version 7 times → Developer options → USB debugging on.
3. Connect the phone with a USB cable, allow debugging on the phone.
4. Install Flipper Phone on the phone.
5. Check: `adb devices` shows the phone with the word **device**.

## Run
    python flipper_phone_mirror.py

## Controls
- Click the picture: tap on the phone at that point.
- Arrow keys: up, down, left, right. Enter: OK. Backspace: back key. Esc: Back.
- Buttons: Launch app (opens Flipper Phone), Back, Home, Refresh, Auto on/off (the picture updates about every 1.2 s).

## Limits
- It is a mirror of the phone: NFC and infrared use the phone's own hardware, so put the card or the IR target next to the phone.
- Updates are about one second behind the phone.
- The phone must stay unlocked.

## Test without a phone
    python test_mirror.py
