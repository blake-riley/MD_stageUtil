# mol new {sysname}.pdb type pdb
mol new {sysname}.prmtop type parm7
mol addfile {sysname}.prmcrd type rst7

proc openFile {{ str_outFile }} {{
	if {{ [ catch {{ open $str_outFile w }} file_outFile ] }} then {{
		return -code error "\[createBoxSize\] Error: Could not open {sysname}.extraBonds.dat for writing"
	}} else {{
		return $file_outFile
	}}
}}

proc closeFile {{ file_outFile }} {{
	#	Flush, and then close file channel
	flush $file_outFile
	close $file_outFile
}}

proc tieMetals {{ metals file_outFile }} {{
	foreach metal [$metals get index] {{
		set coord [atomselect top "(exwithin 3.5 of index $metal) and not (element H OR C)"]
		foreach atom [$coord get index] {{
			if [expr [ lsearch -exact {{"WAT"}} [[atomselect top "index $atom"] get resname] ] >= 0 ] {{
				continue
				#	puts $file_outFile "# WAT"
				#	puts $file_outFile "bond $metal $atom k ref \n"
			}} elseif [expr [ lsearch -exact {{"HIS" "HID" "HIE" "HIP"}} [[atomselect top "index $atom"] get resname] ] >= 0 ] {{
				puts $file_outFile "# HIS"
				puts $file_outFile "bond $metal $atom    66.11   2.041 \n"
			}} elseif [expr [ lsearch -exact {{"GLU" "GLH" "ASP" "ASH"}} [[atomselect top "index $atom"] get resname] ] >= 0 ] {{
				puts $file_outFile "# GLU/ASP"
				puts $file_outFile "bond $metal $atom   170.00   2.007 \n"
			}} else {{
				continue
			}}
		}}
	}}
}}


set file_outFile [ openFile "{sysname}.extraBonds.dat" ]

# Tie nickels
set nickels [atomselect top "resname NI"]
tieMetals $nickels $file_outFile

# Tie zincs
set zincs [atomselect top "resname ZN"]
tieMetals $zincs $file_outFile

# Tie calciums
set calciums [atomselect top "resname CA"]
tieMetals $calciums $file_outFile

closeFile $file_outFile

quit 
