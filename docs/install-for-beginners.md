# PanicStick setup for beginners

This guide is written for someone who has not used Git or a command line before. PanicStick needs a Raspberry Pi Pico 2 (non-W), a button, a USB data cable, and a Mac.

## Before you start

You will need:

- A Pico 2 (not Pico 2 W)
- A normally-open momentary button and two jumper wires
- A USB cable that carries data, not just power
- A Mac running a recent macOS version
- Internet access during setup, to download Python dependencies

PanicStick is a prototype. Start with notification-only mode. Save your work before trying any option that closes apps or changes connectivity.

## Part 1: install the Pico's firmware

1. Install [Thonny](https://thonny.org/) on the Mac and open it.
2. Download the Pico 2 MicroPython firmware from the [official Raspberry Pi MicroPython downloads](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html).
3. Unplug the Pico. Hold its small **BOOTSEL** button while plugging it into the Mac. A drive named **RPI-RP2** should appear in Finder.
4. Copy the downloaded UF2 firmware file onto **RPI-RP2**. The Pico restarts and the drive disappears. This is expected.
5. In Thonny, choose the interpreter for **Raspberry Pi Pico 2** from the interpreter menu.
6. From the PanicStick folder, open the file pico/main.py in Thonny.
7. Choose **File → Save as… → Raspberry Pi Pico**, and name it main.py.
8. Click the green **Run** button. The shell at the bottom should show a line containing the word hello.

If Finder does not show RPI-RP2, try another USB cable. Some charging cables cannot transfer files.

## Part 2: connect the button

With the Pico unplugged:

1. Connect one button leg to pin **GP14**.
2. Connect the other button leg to any **GND** pin.
3. Do not connect the button to **3V3**.
4. Plug the Pico back into the Mac.

The board's internal pull-up means no resistor is needed. A short press should do nothing. Holding the button for two seconds produces a test event in the serial output.

## Part 3: get PanicStick onto the Mac

Download the project ZIP from the public GitHub page:

1. Open the PanicStick GitHub page.
2. Click the green **Code** button, then **Download ZIP**.
3. Open the downloaded ZIP in Finder. A folder named similar to PanicStick-main appears.
4. Install Python 3 from [python.org](https://www.python.org/downloads/macos/) if the Mac does not already have a Python 3 that includes Tk.
5. In the PanicStick folder, open the mac folder and double-click **install.command**.
6. A Terminal window opens while setup runs. It creates a private Python environment, downloads pySerial, and opens the PanicStick setup window. This needs an internet connection.
7. In the setup window, leave **Show a PanicStick notification** selected for the first test. Choose whether plugging in the Pico should ask to run actions. Add other actions only after reading their descriptions.
8. Click **Save settings**. The helper starts when you sign in to your Mac. Keep the Terminal window open until the installer says setup is complete; then you may close it.

If macOS says the installer cannot be opened, Control-click install.command, choose **Open**, then choose **Open** again. Only do this for a copy you downloaded from the official PanicStick repository and have reviewed.

## Part 4: first safe test

1. Confirm notification-only is the only selected action in setup.
2. Unplug the Pico for five seconds.
3. Plug it in. The Mac should show the configured action confirmation/notification. If it says the Pico was already connected when the helper started, unplug and plug it in again.
4. Choose **No** once to confirm that cancellation works.
5. Plug it in again and choose **Run**. You should see a notification and a new line in the event log at ~/Library/Application Support/PanicStick/events.jsonl.
6. Hold the button for at least two seconds only if you enabled the button trigger in setup.

## Changing your choices

To reopen setup, open Terminal, type the following command, then press Return:

    "$HOME/Library/Application Support/PanicStick/app/.venv/bin/python" "$HOME/Library/Application Support/PanicStick/app/panicstick.py" --setup

Uncheck actions you no longer want, then click **Save settings**. You can also quit the PanicStick login helper from Activity Monitor or use mac/uninstall.command from the original downloaded folder.

## What the choices really do

- **Quit apps:** asks apps to quit. Unsaved documents may show their own save dialog. PanicStick does not force-kill applications.
- **Wi-Fi:** turns off the Mac's Wi-Fi interface. You will need to turn it back on in System Settings.
- **Bluetooth:** needs the optional blueutil utility already installed. PanicStick will not install it for you.
- **SSH / Remote Login:** turns off incoming SSH and asks macOS for an administrator password. It does not disable the SSH client used to connect to other computers.
- **Screen Sharing:** opens the Sharing settings; you must turn the switch off yourself. For remote management and other specialized access, use a Shortcut you created and inspect it carefully.
- **Virtual machines:** quits the app names you entered. It cannot guarantee that a headless/background VM has stopped.
- **Shortcuts:** runs the exact Shortcut name you entered. Shortcuts can perform their own actions, so inspect and test yours first.
- **Terminal:** is asked to quit near the end. PanicStick runs as a login helper, not inside Terminal.
- **Shut down:** gets a second confirmation and runs after every other selected action. No Shortcut or other action is run after shutdown is requested.

Every action set has a confirmation window each time it is triggered. If you cancel, nothing in the action list runs.
