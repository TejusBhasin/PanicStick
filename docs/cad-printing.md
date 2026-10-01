# Print and assemble the PanicStick case

Files in this folder are an editable OpenSCAD model and ready-to-slice STL meshes. The case is designed around the **Raspberry Pi Pico 2 (non-W)**: a 51 × 21 mm board with a Micro-USB-B connector.

## Files

- [OpenSCAD source](../cad/panicstick_case.scad) — editable, parametric source.
- [Base STL](../cad/printable/panicstick_base.stl) — lower tray with connector opening, board rails, and screw bosses.
- [Lid STL](../cad/printable/panicstick_lid.stl) — top plate with a guarded GP14 button opening, indicator opening, and screw holes.

The enclosure measures 62 × 31 × 16.4 mm assembled. The port is Micro-USB-B; use a data-capable cable. It is not a USB-A stick and the Pico connector is not built for direct insertion into a computer's USB-A socket.

## Check the fit first

If your printer is not calibrated, open [fit_gauge.scad](../cad/fit_gauge.scad) in OpenSCAD and export the small coupon. It has three slots measuring 21.4, 21.8, and 22.2 mm. The Pico board is nominally 21 mm wide; choose the slot with a gentle fit, then adjust `board_clearance` in the main model if needed.

## Print

1. Download both STL files from GitHub (open the file and use the download button).
2. Import each STL into your slicer. Keep the base and lid as separate parts.
3. Print the base with its flat floor on the build plate. Print the lid flat, outer face on the build plate.
4. Start with 0.2 mm layers, 2–3 walls, and 15–25% infill in PLA or PETG. Supports are not needed.
5. Before inserting electronics, check that the Pico board sits on the rails and the Micro-USB-B plug passes through the opening. Printer calibration and material shrinkage vary; adjust the OpenSCAD `board_clearance` parameter or case dimensions or lightly file the port if needed.

## Assembly and wiring

See the [GP14 button wiring diagram](button-wiring.svg) before soldering or attaching jumper wires.

- Wire a normally-open momentary switch between **GP14** and **GND**. The Pico firmware uses its internal pull-up; do not connect the switch to 3V3.
- Place the switch so its actuator sits under the guarded square opening. The opening is 9 mm square; resize `button_aperture` to suit another switch.
- Route switch wires clear of the board edge pads and connector.
- Align the lid's small LED opening to the Pico's onboard LED before fastening.
- Fasten the lid to the four printed bosses using four M2 × 8 mm screws (2.8 mm lid clearance, 2.2 mm pilot holes). If your printer makes pilot holes tight, carefully size them before assembly.

Test the board and button outside the enclosure first. Do not force the connector or press the board against the case. This is a prototype fit, not a certified enclosure; print a fit sample and adjust parameters for your printer before committing to a final build.
