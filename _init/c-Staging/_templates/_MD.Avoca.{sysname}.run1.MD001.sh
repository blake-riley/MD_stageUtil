#!/bin/bash
#SBATCH --job-name={sysname}.run1.MD001
#SBATCH --nodes=8
#SBATCH --time=120:00:00
#SBATCH --account=VR0071
#SBATCH --mail-type=FAIL
#SBATCH --output="{sysname}.run1.MD001.log"
#SBATCH --error="{sysname}.run1.MD001.err"

#==============================================================
#                Script  for  avoca 
#==============================================================

# MD of {sysname}.run1

# Modules and etc
module load vlsci
module load namd-xl-pami-smp/2.9

# -- 0. Create the logfiles so that they can be read during the progress of the job.
touch {sysname}.run1.MD001.log
touch {sysname}.run1.MD001.err
touch {sysname}.run1.MD001.logout
# -- 1. Create symbolic links from your working directory to $TMPDIR:
ln -sf $PWD/* $TMPDIR/
# -- 2. Go to that temp directory...
cd $TMPDIR

echo Create instance of MD.conf
sed -e 's/in_Name/{sysname}.run1.fromEQdensity/' \
-e 's/out_Name/{sysname}.run1.MD001/' \
-e '/	# Box size/r {sysname}.boxSize.dat' \
< MD.NAMD.{sysname}.MD.conf \
> MD.NAMD.{sysname}.MD.now.conf

echo Run MD
srun --overcommit --ntasks-per-node=64 /usr/local/namd/2.9-xl-pami-smp/bin/namd2 MD.NAMD.{sysname}.MD.now.conf > {sysname}.run1.MD001.logout

echo Create .xst with total run
cat {sysname}.run1.MD001.xst > {sysname}.run1.allMD.xst

echo Strip water from .dcd
/vlsci/VR0071/briley/bin/catdcd -o {sysname}.run1.MD001.nowat.dcd -i {sysname}.nowat.ind {sysname}.run1.MD001.dcd

echo Create allMD.nowat.dcd
cp {sysname}.run1.MD001.nowat.dcd {sysname}.run1.allMD.nowat.dcd

echo Run next 50ns
/usr/local/slurm/latest/bin/sbatch MD.Avoca.{sysname}.run1.MD002.sh

# -- 3. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f $SLURM_SUBMIT_DIR/; done

pwd
date
