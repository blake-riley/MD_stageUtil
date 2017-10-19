#!/bin/bash

#SBATCH --job-name={sysname}.run1.MD001
#SBATCH --mail-user=blake.riley@monash.edu
#SBATCH --mail-type=FAIL
#SBATCH --output="{sysname}.run1.MD001.out"
#SBATCH --error="{sysname}.run1.MD001.err"

#SBATCH --ntasks=1
#SBATCH --gres=gpu:1

#SBATCH --time=2-00:00:00


#==============================================================
#                Script  for  Kronos
#             (WARNING: CURRENTLY IN ALPHA) 
#==============================================================

# MD of {sysname}.run1

source /usr/share/Modules/init/bash
module purge

module load gcc/5.4.0 \
            python/3.6.1-gcc5.4 \
            cuda/8.0 \
            openmpi/2.1.0-gcc5.4 \
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
touch {sysname}.run1.MD001.out
touch {sysname}.run1.MD001.err
touch {sysname}.run1.MD001.logout

# -- 1. Create a temporary directory, and link it back to the submission directory.
if [[ -n ${{SLURM_JOB_USER}} ]]; then
  mkdir -p ${{HOME}}/scratch/${{SLURM_JOB_USER}};
  SCRATCHDIR=`mktemp -d ${{HOME}}/scratch/${{SLURM_JOB_USER}}/${{SLURM_JOB_ID}}.XXXXXX` || exit 1;
  ln -sf ${{SLURM_SUBMIT_DIR}}/* ${{SCRATCHDIR}};
else
  echo "No ${{SLURM_JOB_USER}}. Couldn't make ${{SCRATCHDIR}}." ; # && exit 1;
fi

# -- 2. Go to that temp directory...
cd ${{SCRATCHDIR}}

# -- 3. Run MD protocol:
echo 'Running MD...'
pmemd.cuda       -O -i MD.Amber.MD.conf \
# mpiexec -n 2 \
#   pmemd.cuda.MPI -O -i MD.Amber.MD.conf \
                    -o {sysname}.run1.MD001.logout \
                    -p {sysname}.prmtop \
                    -c {sysname}.run1.fromEQ-d-equil.rst \
                    -r {sysname}.run1.MD001.rst \
                    -x {sysname}.run1.MD001.netcdf

echo Strip water from .netcdf
# ${{HOME}}/projects/wc55/sw/vmd-1.9.2/plugins/LINUXAMD64/bin/catdcd5.1/catdcd -o {sysname}.run1.MD001.nowat.netcdf -otype netcdf -i {sysname}.nowat.ind -netcdf {sysname}.run1.MD001.netcdf
# /home/briley/.local/bin/mdconvert -o {sysname}.run1.MD001.nowat.netcdf -a {sysname}.nowat.ind {sysname}.run1.MD001.netcdf

echo Create allMD.nowat.netcdf
# cp {sysname}.run1.MD001.nowat.netcdf {sysname}.run1.allMD.nowat.netcdf

# -- 4. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f ${{SLURM_SUBMIT_DIR}}/; done
cd ${{SLURM_SUBMIT_DIR}}
rm -rf ${{SCRATCHDIR}}

# -- 5. Run the next step.
echo Run next 50ns
sbatch MD.Kronos.{sysname}.run1.MD002.sh

pwd
date
