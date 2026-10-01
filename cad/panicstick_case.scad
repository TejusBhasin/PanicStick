// PanicStick enclosure for Raspberry Pi Pico 2 (non-W). All dimensions are mm.
// Set part to "base" or "lid"; render (F6), then File > Export > Export as STL.
part = "base";
$fn = 48;

case_x=62; case_y=31; base_z=12.4; wall=2; floor=2; lid_z=2;
board_width=21; board_clearance=0.4; rail_width=1.1;
usb_width=10; usb_height=5.5; usb_y=case_y/2; usb_z=5.8;
button_x=39; button_y=case_y/2; button_aperture=9;
led_x=49.5; led_y=case_y/2; led_d=3.4;
screw_x=[4,58]; screw_y=[4,27];

module boss(x,y) {
  translate([x,y,floor]) difference() {
    cylinder(h=base_z-floor,d=5.4);
    translate([0,0,-0.1]) cylinder(h=base_z-floor+0.2,d=2.2);
  }
}
module base() {
  union() {
    difference() {
      cube([case_x,case_y,base_z]);
      translate([wall,wall,floor]) cube([case_x-2*wall,case_y-2*wall,base_z-floor+0.1]);
      // Pico 2 Micro-USB-B connector clearance.
      translate([-0.1,usb_y-usb_width/2,usb_z-usb_height/2]) cube([wall+0.2,usb_width,usb_height]);
    }
    // Low edge rails support the 51 x 21 mm board while leaving pads clear.
    translate([4,(case_y-board_width)/2-board_clearance-rail_width,floor]) cube([54,rail_width,1.6]);
    translate([4,(case_y+board_width)/2+board_clearance,floor]) cube([54,rail_width,1.6]);
    for(x=screw_x) for(y=screw_y) boss(x,y);
  }
}
module lid() {
  difference() {
    union() {
      translate([0,0,base_z]) cube([case_x,case_y,lid_z]);
      // Raised square guard protects a small momentary trigger switch.
      translate([button_x-7.2,button_y-7.2,base_z+lid_z]) difference() {
        cube([14.4,14.4,1.8]);
        translate([2.7,2.7,-0.1]) cube([9,9,2]);
      }
    }
    for(x=screw_x) for(y=screw_y) translate([x,y,base_z-0.1]) cylinder(h=lid_z+2.1,d=2.8);
    translate([button_x-button_aperture/2,button_y-button_aperture/2,base_z-0.1]) cube([button_aperture,button_aperture,lid_z+2.1]);
    // Align the light pipe opening to the Pico onboard LED at assembly.
    translate([led_x,led_y,base_z-0.1]) cylinder(h=lid_z+2.1,d=led_d);
  }
}
if(part=="base") base();
if(part=="lid") lid();
