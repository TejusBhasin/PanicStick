# PanicStick setup for beginners

This guide is written for someone who has not used Git or a command line before. You need a Raspberry Pi Pico 2 (non-W), a button, a data-capable USB cable, and a Mac.

## Before you start

- Pico 2 (not Pico 2 W)
- Normally-open momentary button and two jumper wires
- USB Micro-B data cable (many newer Macs also need a USB-C adapter or hub)
- Mac running a recent macOS version
- Internet access during setup
- Optional: 3D printer and four M2 × 8 mm screws for the enclosure

PanicStick is a prototype. Start with notification-only mode. Save your work before testing actions that close apps or change connectivity.

## Part 1: put the firmware on the Pico

1. Install [Thonny](https://thonny.org/) and open it.
2. Download the Pico 2 MicroPython firmware from the [official Raspberry Pi MicroPython page](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html).
3. Unplug the Pico. Hold its small **BOOTSEL** button while connecting it to the Mac. A drive named **RPI-RP2** should appear in Finder.
4. Copy the downloaded UF2 firmware file onto **RPI-RP2**. The Pico restarts and the drive disappears. This is expected.
5. In Thonny, choose the **Raspberry Pi Pico 2** interpreter.
6. In Thonny, open `pico/button_monitor.py` and choose **File → Save as… → Raspberry Pi Pico**. Save it as `button_monitor.py`.
7. Open `pico/main.py` and save it to the Pico as `main.py`.
8. Click the green **Run** button. The shell should show a line with `hello`.

If Finder does not show RPI-RP2, try a different data cable. Some cables provide power only.

![Pico 2 board and external button](images/pico2-and-button.svg)

## Part 2: connect the button

Unplug the Pico before wiring.

1. Connect one button leg to pin **GP14**.
2. Connect the other button leg to any **GND** pin.
3. Do not connect it to **3V3**.
4. Plug the Pico back in. A short press should do nothing; holding it for two seconds sends a test event.

## Part 3: install the Mac companion

1. Open the [PanicStick GitHub page](https://github.com/TejusBhasin/PanicStick).
2. Click the green **Code** button, then **Download ZIP**.
3. Open the downloaded ZIP in Finder; a folder named something like `PanicStick-main` appears.
4. Install Python 3 from [python.org](https://www.python.org/downloads/macos/) if needed. The Mac installer needs a Python 3 build that includes Tk.
5. Open the downloaded folder, then the `mac` folder. Double-click **install.command**.
6. A Terminal window opens during setup. The installer prepares a private Python environment, installs pySerial, and opens the setup window. Keep the Mac online for this step.
7. Keep **Ask before each run** for your first test and select notification only. You can later choose unattended mode and select checkpoints immediately before chosen actions. A shutdown checkpoint is selected by default when power-off is enabled.
8. Click **Save settings**. The helper starts when you sign in to your Mac. Keep the installer window open until it reports completion.

If macOS blocks the installer, Control-click `install.command`, choose **Open**, then choose **Open** again. Only do this for a copy from the official repository that you have reviewed.

![Safe first-test flow](images/setup-flow.svg)

## Part 4: test safely

1. In setup, choose notification-only.
2. Unplug the Pico for five seconds.
3. Plug it in. Read the action confirmation, then choose **Cancel**. No selected action should run.
4. Plug it in again and choose **Run**. You should see the notification and a new event line in `~/Library/Application Support/PanicStick/events.jsonl`.
5. Try the two-second physical hold only if you enabled that trigger.

By default the Mac asks before each run. Unattended mode skips that start prompt, but your selected checkpoints still pause before the chosen actions. If the Mac is taken over, you may not be able to select Confirm.

## Optional: print the case

Follow [the case printing guide](cad-printing.md) from the repository's `docs` folder. Download the two STL parts, print the base and lid separately, and test the fit with the Pico unpowered before wiring it into the case. The opening is for the Pico's Micro-USB-B connector; it is not a USB-A plug. A 3D printer is optional—the device can be tested on a nonconductive surface without the enclosure.

## Change or remove settings

To reopen setup, open Terminal, paste this command, and press Return:

    "$HOME/Library/Application Support/PanicStick/app/.venv/bin/python" "$HOME/Library/Application Support/PanicStick/app/panicstick.py" --setup

To remove the login helper, reopen the downloaded folder and double-click `mac/uninstall.command`.

## What the choices do

- **Quit apps:** asks apps to quit; unsaved documents may show their own save dialog. It does not force-kill apps.
- **Wi-Fi:** turns off the Mac's Wi-Fi interface until you switch it back on in System Settings.
- **Bluetooth:** needs the optional blueutil utility; PanicStick will not install it.
- **SSH / Remote Login:** turns off incoming SSH and may ask for an administrator password. It does not disable the SSH client.
- **Screen Sharing:** opens Sharing settings; you switch the setting off yourself.
- **Virtual machines:** quits named VM apps. It cannot guarantee a background/headless VM has stopped.
- **Shortcuts:** runs the named Shortcut. Inspect it first because Shortcuts can perform their own actions.
- **Terminal:** asks Terminal to quit near the end. PanicStick runs independently as a login helper.
- **Power off:** runs last. Its confirmation checkpoint is selected by default and can be removed in setup. Nothing runs after shutdown is requested.

If any action fails, the remaining action sequence stops. Canceling the confirmation runs nothing.
