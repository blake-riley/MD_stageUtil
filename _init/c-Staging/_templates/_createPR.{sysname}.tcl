mol new {sysname}.pdb type pdb
set everyone [atomselect top all]
$everyone set beta 0.0
set heavy [atomselect top "protein and noh"]
$heavy set beta 1.0
$everyone writepdb {sysname}.PR.pdb
$everyone set beta 0.0
set heavy [atomselect top "backbone and noh"]
$heavy set beta 1.0
$everyone writepdb {sysname}.PR-bb.pdb
quit
