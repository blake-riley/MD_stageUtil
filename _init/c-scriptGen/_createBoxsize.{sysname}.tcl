mol new {sysname}.pdb type pdb
set everyone [atomselect top all]
set minmaxlist [ measure minmax $everyone ]
set min [ lindex $minmaxlist 0 ]
set max [ lindex $minmaxlist 1 ]
set center [ measure center $everyone ]

proc openFile {{ str_outFile }} {{
	if {{ [ catch {{ open $str_outFile w }} file_outFile ] }} then {{
		return -code error "\[createBoxSize\] Error: Could not open {sysname}.boxSize.dat for writing"
	}} else {{
		return $file_outFile
	}}
}}

proc closeFile {{ file_outFile }} {{
	#	Flush, and then close file channel
	flush $file_outFile
	close $file_outFile
}}

#	Calculate the actualsize and actualcentre of the box
set actualsize [ list ]
set actualcentre [ list ] 
for {{ set i 0 }} {{ $i <= 2 }} {{ incr i }} {{
	lappend actualsize [ expr {{ [ lindex $max $i ] - [ lindex $min $i ] }} ]
	lappend actualcentre [ expr {{ [ lindex $center $i ] - [ lindex $min $i ] }} ]
}}

#	Write allsizerows (includes 0.0 where not main diagonal)
set allsizerows [ list ]

for {{ set i 0 }} {{ $i <= 2 }} {{ incr i }} {{
	set currow [ list ]
	for {{ set j 0 }} {{ $j <= 2 }} {{ incr j }} {{
		if {{ $i == $j }} then {{
			lappend currow [ lindex $actualsize $j ]
		}} else {{ 
			lappend currow "0.0"
		}}
	}}
	lappend allsizerows $currow
}}

#	Open the boxsize file, write the boxsize file, close the boxsize file
set file_outFile [ openFile "{sysname}.boxSize.dat" ]

for {{ set i 0 }} {{ $i <= 2 }} {{ incr i }} {{
	set currow [ list ] 
	for {{ set j 0 }} {{ $j <= 2 }} {{ incr j }} {{
		lappend currow [ format "%.1f" [ expr {{ [ expr {{ ceil( [ expr {{ 10 * [ lindex [ lindex $allsizerows $i ] $j ] }} ] ) }} ] / 10 }} ] ]
	}}
	puts $file_outFile "\tcellBasisVector[ expr {{ $i + 1 }} ]\t\t\t\t\t$currow"
}}
for {{ set i 0 }} {{ $i == 0 }} {{ incr i }} {{
	set currow [ list ]
	for {{ set j 0 }} {{ $j <= 2 }} {{ incr j }} {{
		lappend currow [ format "%.1f" [ expr {{ [ expr {{ ceil( [ expr {{ 10 * [ lindex $actualcentre $j ] }} ] ) }} ] / 10 }} ] ]
	}}
	puts $file_outFile "\tcellOrigin\t\t\t\t\t\t\t$currow"
}}

closeFile $file_outFile

quit 
