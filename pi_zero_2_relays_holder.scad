$fn = 120;
//garage door mount measurements
garage_door_hole_dist = 3*25.4;
garage_door_hole_dia = 7;
garage_door_mount_thick = 4;
garage_door_mount_wide = 35;

//relay holder measurements
relay_thick = 20;
relay_board_thick = 1.6;
relay_board_wide = 45.6;
relay_holder_tall = 30;
relay_block_wide = 35;
pin_clearance = 3;
holder_thick = 2;

//pi holder measurements
pi_hole_dia = 2;
standoff_height = 4;
standoff_dia = 7;
pi_hole_dist_long = 58;
pi_hole_dist_short = 23;
pi_square_thick = 2;

//camera mount dimensions
ball_dia = 12;
cylinder_dia = 6;
cylinder_length = 20;

//garage door mount
translate([0,garage_door_mount_thick,0])
rotate([90,0,0])
difference(){
    cube([garage_door_mount_wide,garage_door_hole_dist+garage_door_hole_dia*3,garage_door_mount_thick]);
    union(){
        translate([garage_door_mount_wide/2,garage_door_hole_dia*1.5,-1])
        cylinder(d=garage_door_hole_dia,h=garage_door_mount_thick+2);
        translate([garage_door_mount_wide/2,garage_door_hole_dia*1.5+garage_door_hole_dist,-1])
        cylinder(d=garage_door_hole_dia,h=garage_door_mount_thick+2);
    }
}

//relay holders
translate([6,-(relay_board_wide+holder_thick*2)+holder_thick,20])
relay_hold();
translate([6+relay_thick+pin_clearance+relay_board_thick,-(relay_board_wide+holder_thick*2)+holder_thick,20])
relay_hold();

//pi holder
translate([6+relay_thick+pin_clearance+relay_board_thick,-(relay_board_wide+holder_thick*2)+holder_thick*2,20])
rotate([90,0,0])
difference(){
    union(){
        cube([pi_hole_dist_short+standoff_dia,pi_hole_dist_long+standoff_dia,pi_square_thick]);
        translate([standoff_dia/2,standoff_dia/2,pi_square_thick])
        cylinder(d=standoff_dia,h=standoff_height);
        translate([standoff_dia/2+pi_hole_dist_short,standoff_dia/2,pi_square_thick])
        cylinder(d=standoff_dia,h=standoff_height);
        translate([standoff_dia/2,standoff_dia/2+pi_hole_dist_long,pi_square_thick])
        cylinder(d=standoff_dia,h=standoff_height);
        translate([standoff_dia/2+pi_hole_dist_short,standoff_dia/2+pi_hole_dist_long,pi_square_thick])
        cylinder(d=standoff_dia,h=standoff_height);
    }
    union(){
        translate([standoff_dia/2,standoff_dia/2,pi_square_thick])
        cylinder(d=pi_hole_dia,h=standoff_height*3, center=true);
        translate([standoff_dia/2+pi_hole_dist_short,standoff_dia/2,pi_square_thick])
        cylinder(d=pi_hole_dia,h=standoff_height*3, center=true);
        translate([standoff_dia/2,standoff_dia/2+pi_hole_dist_long,pi_square_thick])
        cylinder(d=pi_hole_dia,h=standoff_height*3, center=true);
        translate([standoff_dia/2+pi_hole_dist_short,standoff_dia/2+pi_hole_dist_long,pi_square_thick])
        cylinder(d=pi_hole_dia,h=standoff_height*3, center=true);
    }
}

//camera holder sphere
translate([6+(relay_thick+pin_clearance+relay_board_thick)*2+ball_dia/2+cylinder_length/2,-(relay_board_wide+holder_thick*2)+holder_thick*2+cylinder_dia/2,20])
rotate([0,-90,0])
union(){
    sphere(d=ball_dia);
    cylinder(d=cylinder_dia, h=cylinder_length);
}


module relay_hold(){
difference(){
    cube([relay_thick+pin_clearance+relay_board_thick,relay_board_wide+holder_thick*2,relay_holder_tall+holder_thick]);
    union(){
        translate([-1,holder_thick*2,holder_thick*2])
        cube([relay_thick*2,relay_board_wide-holder_thick*2,relay_holder_tall*2]);
        translate([pin_clearance,holder_thick,holder_thick])
        cube([relay_board_thick,relay_board_wide,relay_holder_tall*2]);
    }
}
}