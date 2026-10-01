// Print this small fit coupon before the full case if your printer is uncalibrated.
// Three through-slots check 21.4, 21.8, and 22.2 mm clear widths for the Pico's 21 mm PCB.
slot_widths=[21.4,21.8,22.2];
coupon_x=54; coupon_y=27; coupon_z=3; slot_x=16;
difference() {
  cube([coupon_x,coupon_y,coupon_z]);
  for(i=[0:2]) {
    x0=2+i*18;
    w=slot_widths[i];
    translate([x0,(coupon_y-w)/2,-0.1]) cube([slot_x,w,coupon_z+0.2]);
  }
}
