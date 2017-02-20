#!/bin/bash

#SBATCH --job-name={sysname}.run1.EQ000
# SBATCH --account=wc55
#SBATCH --mail-user=blake.riley@monash.edu
#SBATCH --mail-type=FAIL
#SBATCH --output="{sysname}.run1.EQ000.out"
#SBATCH --error="{sysname}.run1.EQ000.err"
# SBATCH --output={sysname}.MD001-%j.out
# SBATCH --error={sysname}.MD001-%j.err

#SBATCH --ntasks=2
# SBATCH --ntasks-per-node=2
# SBATCH --cpus-per-task=1
# SBATCH --mem-per-cpu=4096
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2

#SBATCH --time=0-24:00:00
#SBATCH --reservation=buckle_lab


#==============================================================
#                Script  for  MonARCH 
#==============================================================

# EM of {sysname}.run1

source /usr/share/Modules/init/bash
module purge

module use /mnt/lustre/projects/wc55/sw/modulefiles

module load intel/2015.0.090 \
            python/3.5.2-intel \
            cuda/7.5 \
            openmpi/1.10.2noib-intel \
            amber/16

module -l list

echo '---Machine information---'
echo "NVIDIA-SMI"
nvidia-smi
echo ""
echo "DEVICEQUERY"
deviceQuery
echo ""
echo "HOSTNAME="
hostname -s
echo ""
echo "SLURM_NODEID="
echo "${{SLURM_NODEID}}"
echo ""
echo "SLURM_NODELIST="
echo "${{SLURM_NODELIST}}"
echo ""
echo '-------------------------'


# -- 0. Create the logfiles so that they can be read during the progress of the job.
touch {sysname}.run1.EQ000.out
touch {sysname}.run1.EQ000.err
touch {sysname}.run1.EQ000-a.logout
touch {sysname}.run1.EQ000-b.logout
touch {sysname}.run1.EQ000-c.logout
touch {sysname}.run1.EQ000-d.logout

# -- 1. Create a temporary directory, and link it back to the submission directory.
if [[ -n ${{SLURM_JOB_USER}} ]]; then
  mkdir -p /mnt/lustre/scratch/${{SLURM_JOB_USER}};
  SCRATCHDIR=`mktemp -d /mnt/lustre/scratch/${{SLURM_JOB_USER}}/${{SLURM_JOB_ID}}.XXXXXX` || exit 1;
  ln -sf ${{SLURM_SUBMIT_DIR}}/* ${{SCRATCHDIR}};
else
  echo "No ${{SLURM_JOB_USER}}. Couldn't make ${{SCRATCHDIR}}." && exit 1;
fi

# -- 2. Go to that temp directory...
cd ${{SCRATCHDIR}}

# -- 3. Run MD protocol:
echo 'Running stage 1: Energy minimization...'
pmemd.cuda -O -i MD.Amber.EQ-a-min.conf \
              -o {sysname}.run1.EQ000-a.logout \
              -p {sysname}.prmtop \
              -c {sysname}.prmcrd \
              -ref {sysname}.prmcrd \
              -r {sysname}.run1.fromEQ-a-min.rst \
              -x {sysname}.run1.EQ000-a.netcdf

echo 'Running stage 2: Heat...'
# pmemd.cuda       -O -i MD.Amber.EQ-b-heat.conf \
mpiexec -n 2 \
  pmemd.cuda.MPI -O -i MD.Amber.EQ-b-heat.conf \
                    -o {sysname}.run1.EQ000-b.logout \
                    -p {sysname}.prmtop \
                    -c {sysname}.run1.fromEQ-a-min.rst \
                    -ref {sysname}.run1.fromEQ-a-min.rst \
                    -r {sysname}.run1.fromEQ-b-heat.rst \
                    -x {sysname}.run1.EQ000-b.netcdf

echo 'Running stage 3: Density...'
# pmemd.cuda       -O -i MD.Amber.EQ-c-density.conf \
mpiexec -n 2 \
  pmemd.cuda.MPI -O -i MD.Amber.EQ-c-density.conf \
                    -o {sysname}.run1.EQ000-c.logout \
                    -p {sysname}.prmtop \
                    -c {sysname}.run1.fromEQ-b-heat.rst \
                    -ref {sysname}.run1.fromEQ-b-heat.rst \
                    -r {sysname}.run1.fromEQ-c-density.rst \
                    -x {sysname}.run1.EQ000-c.netcdf

echo 'Running stage 4: Equilibration...'
# pmemd.cuda       -O -i MD.Amber.EQ-d-equil.conf \
mpiexec -n 2 \
  pmemd.cuda.MPI -O -i MD.Amber.EQ-d-equil.conf \
                    -o {sysname}.run1.EQ000-d.logout \
                    -p {sysname}.prmtop \
                    -c {sysname}.run1.fromEQ-c-density.rst \
                    -ref {sysname}.run1.fromEQ-c-density.rst \
                    -r {sysname}.run1.fromEQ-d-equil.rst \
                    -x {sysname}.run1.EQ000-d.netcdf

# -- 4. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f ${{SLURM_SUBMIT_DIR}}/; done
cd ${{SLURM_SUBMIT_DIR}}
rm -rf ${{SCRATCHDIR}}

# -- 5. Run the next step.
echo Run next 50ns
sbatch MD.MonARCH.{sysname}.run1.MD001.sh

pwd
date
