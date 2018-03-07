#!/bin/bash
#PBS -N {sysname}.run1.MD001
#PBS -l nodes=4:ppn=8:mx
#PBS -l walltime=120:00:00
#PBS -m ae
#PBS -M blake.riley@monash.edu

#==============================================================
#                Script  for  Orchard 
#==============================================================

# MD of {sysname}.run1

# Modules and etc
module load openmpi-intel/1.4.4
module load namd-intel/2.9
cd $PBS_O_WORKDIR
echo 
hostname -s
echo 

# -- 0. Create the logfile so that it can be read during the progress of the job.
touch {sysname}.run1.MD001.logout

# -- 1. Create a temporary directory, and link it back to the submission directory.
# mkdir -p /scratch/$USER
# SCRATCHDIR=`mktemp -d /scratch/$USER/$PBS_JOBID.XXXXXX` || exit 1
# ln -sf $PBS_O_WORKDIR/* $SCRATCHDIR

# -- 2. Go to that temp directory.
# cd $SCRATCHDIR

# -- 3. Run job...
echo Create instance of MD.conf
sed -e 's/in_Name/{sysname}.run1.fromEQdensity/' \
-e 's/out_Name/{sysname}.run1.MD001/' \
-e '/	# Box size/r {sysname}.boxSize.dat' \
< MD.NAMD.{sysname}.MD.conf \
> MD.NAMD.{sysname}.MD.now.conf

echo Run MD
mpirun /software/namd/2.9-intel/bin/namd2 MD.NAMD.{sysname}.MD.now.conf > {sysname}.run1.MD001.logout

echo Create .xst with total run
cat {sysname}.run1.MD001.xst > {sysname}.run1.allMD.xst

echo Strip water from .dcd
/home/blake/bin/catdcd -o {sysname}.run1.MD001.nowat.dcd -i {sysname}.nowat.ind {sysname}.run1.MD001.dcd

echo Create allMD.nowat.dcd
cp {sysname}.run1.MD001.nowat.dcd {sysname}.run1.allMD.nowat.dcd

# -- 4. Copy things back, move back home.
# for f in *; do [ ! -h $f ] && cp -r $f $PBS_O_WORKDIR/; done && {{
# 	cd $PBS_O_WORKDIR
# 	echo "Copy back successful. Now removing scratch files."
# 	rm -rf $SCRATCHDIR
# }}
# cd $PBS_O_WORKDIR

# -- 5. Run next job.
echo Run next 50ns
/usr/local/bin/qsub MD.Orchard.{sysname}.run1.MD002.sh

pwd
date
