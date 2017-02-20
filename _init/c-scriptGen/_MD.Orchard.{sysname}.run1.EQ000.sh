#!/bin/bash
#PBS -N {sysname}.run1.EQ000
#PBS -l nodes=2:ppn=8:mx
#PBS -l walltime=72:00:00
#PBS -m ae
#PBS -M blake.riley@monash.edu

#==============================================================
#                Script  for  Orchard 
#==============================================================

# EM of {sysname}.run1

# Modules and etc
module load openmpi-intel/1.4.4
module load namd-intel/2.9
cd $PBS_O_WORKDIR
echo 
hostname -s
echo 

# -- 0. Create the logfile so that it can be read during the progress of the job.
touch {sysname}.run1.EQ000.logout

# -- 1. Create a temporary directory, and link it back to the submission directory.
# mkdir -p /scratch/$USER
# SCRATCHDIR=`mktemp -d /scratch/$USER/$PBS_JOBID.XXXXXX` || exit 1
# ln -sf $PBS_O_WORKDIR/* $SCRATCHDIR

# -- 2. Go to that temp directory.
# cd $SCRATCHDIR

# -- 3. Run job...
echo Create instance of EM.conf
sed -e 's/out_Name/{sysname}.run1.fromEM/' \
-e '/	# Box size/r {sysname}.boxSize.dat' \
< MD.NAMD.{sysname}.EM.conf \
> MD.NAMD.{sysname}.EM.now.conf

echo Create instance of EQheat.conf
sed -e 's/in_Name/{sysname}.run1.fromEM/' \
-e 's/out_Name/{sysname}.run1.fromEQheat/' \
-e '/	# Box size/r {sysname}.boxSize.dat' \
< MD.NAMD.{sysname}.EQheat.conf \
> MD.NAMD.{sysname}.EQheat.now.conf

echo Create instance of EQdensity.conf
sed -e 's/in_Name/{sysname}.run1.fromEQheat/' \
-e 's/out_Name/{sysname}.run1.fromEQdensity/' \
-e '/	# Box size/r {sysname}.boxSize.dat' \
< MD.NAMD.{sysname}.EQdensity.conf \
> MD.NAMD.{sysname}.EQdensity.now.conf

echo Run EM - First minimize only the water, there is a restraint imposed on the protein, followed by a minimization of everything.
mpirun /software/namd/2.9-intel/bin/namd2 MD.NAMD.{sysname}.EM.now.conf > {sysname}.run1.EQ000.logout

echo Equilibration - Heating up at constant volume.
mpirun /software/namd/2.9-intel/bin/namd2 MD.NAMD.{sysname}.EQheat.now.conf >> {sysname}.run1.EQ000.logout

echo Equilibrate the system using pressure and temperature control then reduce the PR to zero.
mpirun /software/namd/2.9-intel/bin/namd2 MD.NAMD.{sysname}.EQdensity.now.conf >> {sysname}.run1.EQ000.logout

# -- 4. Copy things back, move back home.
# for f in *; do [ ! -h $f ] && cp -r $f $PBS_O_WORKDIR/; done && {{
# 	cd $PBS_O_WORKDIR
# 	echo "Copy back successful. Now removing scratch files."
# 	rm -rf $SCRATCHDIR
# }}
# cd $PBS_O_WORKDIR

# -- 5. Run next job.
echo Run next 50ns
/usr/local/bin/qsub MD.Orchard.{sysname}.run1.MD001.sh

pwd
date
