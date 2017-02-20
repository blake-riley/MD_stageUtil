#!/bin/bash
#SBATCH --job-name={sysname}.run1.EQ000
#SBATCH --nodes=8
#SBATCH --time=96:00:00
#SBATCH --account=VR0071
#SBATCH --mail-type=FAIL
#SBATCH --output="{sysname}.run1.EQ000.log"
#SBATCH --error="{sysname}.run1.EQ000.err"

#==============================================================
#                Script  for  avoca 
#==============================================================

# EM of {sysname}.run1

# Modules and etc
module load vlsci
module load namd-xl-pami-smp/2.9

# -- 0. Create the logfiles so that they can be read during the progress of the job.
touch {sysname}.run1.EQ000.log
touch {sysname}.run1.EQ000.err
# -- 1. Create symbolic links from your working directory to $TMPDIR:
ln -sf $PWD/* $TMPDIR/
# -- 2. Go to that temp directory...
cd $TMPDIR

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
srun --overcommit --ntasks-per-node=64 /usr/local/namd/2.9-xl-pami-smp/bin/namd2 MD.NAMD.{sysname}.EM.now.conf 

echo Equilibration - Heating up at constant volume.
srun --overcommit --ntasks-per-node=64 /usr/local/namd/2.9-xl-pami-smp/bin/namd2 MD.NAMD.{sysname}.EQheat.now.conf

echo Equilibrate the system using pressure and temperature control then reduce the PR to zero.
srun --overcommit --ntasks-per-node=64 /usr/local/namd/2.9-xl-pami-smp/bin/namd2 MD.NAMD.{sysname}.EQdensity.now.conf

echo Run next 50ns
/usr/local/slurm/latest/bin/sbatch MD.Avoca.{sysname}.run1.MD001.sh

# -- 3. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f $SLURM_SUBMIT_DIR/; done

pwd
date
