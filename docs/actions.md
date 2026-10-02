# What each action does

Choose only the steps you understand. The first run should use **Show a PanicStick notification** by itself.

When the Pico arrives or the button is held, the Mac shows an action review. Nothing in the list runs until you choose **Run**. **Cancel** records the cancellation and does not run the sequence.

## Actions in the setup window

| Choice | What PanicStick does | Keep in mind |
| --- | --- | --- |
| Show a notification | Shows a macOS notification and records the event. | A good first test. |
| Quit selected apps | Asks each named app to quit normally. | Apps may ask you to save. PanicStick does not force-close them. |
| Quit all apps | Asks open foreground apps to quit, while skipping key macOS processes. | Save work first. Apps may present their own save prompts. |
| Turn Wi-Fi off | Uses the Mac's networksetup command to power off its Wi-Fi interface. | Turn it back on in System Settings afterward. |
| Turn Bluetooth off | Uses blueutil, if you already installed it. | PanicStick does not install tools. If blueutil is missing, that step fails and later steps stop. |
| Turn off incoming SSH / Remote Login | Changes the macOS Remote Login setting and may request an administrator password. | This affects incoming SSH access. It does not disable the SSH client. |
| Open Sharing settings | Opens the macOS Sharing settings page. | You must switch Screen Sharing off yourself. |
| Quit selected virtual-machine apps | Asks the named VM apps to quit normally. | This does not prove that a headless/background VM has stopped. Check your VM software. |
| Run a Shortcut | Runs the exact Shortcut name you entered in the Shortcuts app. | Review the Shortcut first; it can do anything its own actions allow. It runs before connectivity or app changes. |
| Quit Terminal | Asks Terminal to quit near the end of the sequence. | PanicStick keeps running as a separate login helper. |
| Shut down the Mac | Asks once more immediately before requesting shutdown. | Shutdown is always last. No later PanicStick step can run after it. |

## Order and failures

PanicStick runs a selected Shortcut first, then connectivity changes, then selected app actions, then Terminal, and finally shutdown. If any step fails, the remaining steps are skipped. PanicStick cannot roll back a change that already completed; for example, switch Wi-Fi back on yourself if a later app step fails.

A canceled action review runs no actions. A canceled shutdown confirmation leaves the Mac on, after the earlier selected steps have completed.
