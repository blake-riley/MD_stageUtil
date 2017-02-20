#!/bin/bash

#SBATCH --job-name={sysname}.run1.MD001
#SBATCH --account=monash006
#SBATCH --mail-user=blake.riley@monash.edu
#SBATCH --mail-type=FAIL
#SBATCH --output="{sysname}.run1.MD001.out"
#SBATCH --error="{sysname}.run1.MD001.err"
# SBATCH --output=CHAP.con.MD001-%j.out
# SBATCH --error=CHAP.con.MD001-%j.err

#SBATCH --ntasks=2
# SBATCH --ntasks-per-node=1
# SBATCH --cpus-per-task=1
# SBATCH --mem-per-cpu=4096
#SBATCH --gres=gpu:m2070:2
# SBATCH --gres=gpu:k20m:1

#SBATCH --time=2-00:00:00
# SBATCH --reservation=reservation_name


#==============================================================
#                Script  for  MASSIVE 
#==============================================================

# MD of {sysname}.run1

source /usr/local/Modules/3.2.10/init/bash
module purge
module load massive/config-20141113 \
            mpc/0.8.1 \
            cuda/6.5 \
            mpich/3.1.4
module -l list

source /home/projects/Monash006/sw/amber14/amber.sh

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
  mkdir -p /scratch/Monash006/${{SLURM_JOB_USER}};
  SCRATCHDIR=`mktemp -d /scratch/Monash006/${{SLURM_JOB_USER}}/${{SLURM_JOB_ID}}.XXXXXX` || exit 1;
  ln -sf ${{SLURM_SUBMIT_DIR}}/* ${{SCRATCHDIR}};
else
  echo "No ${{SLURM_JOB_USER}}. Couldn't make ${{SCRATCHDIR}}." && exit 1;
fi

# -- 2. Go to that temp directory...
cd ${{SCRATCHDIR}}

# -- 3. Run MD protocol:
echo 'Running MD...'
# pmemd.cuda       -O -i MD.Amber.MD.conf \
mpiexec -n 2 \
  pmemd.cuda.MPI -O -i MD.Amber.MD.conf \
                    -o {sysname}.run1.MD001.logout \
                    -p {sysname}.prmtop \
                    -c {sysname}.run1.fromEQ-d-equil.rst \
                    -r {sysname}.run1.MD001.rst \
                    -x {sysname}.run1.MD001.netcdf

echo Strip water from .dcd
/home/projects/Monash006/sw/vmd-1.9.2/plugins/LINUXAMD64/bin/catdcd5.1/catdcd -o {sysname}.run1.MD001.nowat.netcdf -otype netcdf -i {sysname}.nowat.ind -netcdf {sysname}.run1.MD001.netcdf

echo Create allMD.nowat.dcd
cp {sysname}.run1.MD001.nowat.netcdf {sysname}.run1.allMD.nowat.netcdf

# -- 4. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f ${{SLURM_SUBMIT_DIR}}/; done
cd ${{SLURM_SUBMIT_DIR}}
rm -rf ${{SCRATCHDIR}}

# -- 5. Run the next step.
echo Run next 50ns
sbatch MD.Massive.{sysname}.run1.MD002.sh

pwd
date
