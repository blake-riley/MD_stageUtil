# mol new {sysname}.pdb type pdb
mol new {sysname}.prmtop type parm7
mol addfile {sysname}.prmcrd type rst7

set notwat [atomselect top "not water"]
set indices [$notwat get index]
set file [open {sysname}.nowat.ind w]
foreach i $indices {{
  puts $file $i
}}
flush $file
close $file
$notwat writepdb {sysname}.nowat.pdb
$notwat writepsf {sysname}.nowat.psf
exit
