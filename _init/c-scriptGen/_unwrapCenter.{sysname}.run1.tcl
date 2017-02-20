package require pbctools

mol new {sysname}.nowat.psf

mol addfile {sysname}.run1.allMD.nowat.dcd type dcd waitfor all
pbc readxst {sysname}.run1.allMD.xst
pbc box
pbc unwrap -first first -last last -sel protein

set outfile [open {sysname}.run1.allMD.rmsd.dat w]
set nf [molinfo top get numframes]
set frame0 [atomselect top "protein and backbone" frame 0]
set sel [atomselect top "protein and backbone"]
set all [atomselect top all]
for {{ set i 1 }} {{ $i <= $nf }} {{ incr i }} {{
	$sel frame $i
	$all frame $i
	set rotmtrx [measure fit $sel $frame0]
	$all move $rotmtrx
	puts $outfile "$rotmtrx"
	if {{ $i%10 == 0 }} {{ 
		set progress [ expr {{ $i * 100 / $nf }} ]
		puts "$progress% complete ... (Frame $i/$nf aligned)"
	}}
}}
flush $outfile
close $outfile

animate write dcd {sysname}.run1.allMD.nowat.unwrap.centre.dcd waitfor all

quit
