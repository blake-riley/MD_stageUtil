#!/bin/bash

#SBATCH --job-name={systemname}.run{repl_num:02d}.{stage}{segment_num:03d}
#SBATCH --account=monash006
#SBATCH --mail-user={user_email}
#SBATCH --mail-type=FAIL
#SBATCH --output="{systemname}.run{repl_num:02d}.{stage}{segment_num:03d}.out"
#SBATCH --error="{systemname}.run{repl_num:02d}.{stage}{segment_num:03d}.err"

#SBATCH --ntasks=2
#SBATCH --gres=gpu:m2070:2

#SBATCH --time=0-24:00:00


#==============================================================
#                Script  for  MASSIVE 
#==============================================================

# {stage}{segment_num:03d} of {systemname}.run{repl_num:02d}

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
{logfiles}

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
{md_commands}

# -- 4. Copy things back.
for f in *; do [ ! -h $f ] && cp -r $f ${{SLURM_SUBMIT_DIR}}/; done
cd ${{SLURM_SUBMIT_DIR}}
rm -rf ${{SCRATCHDIR}}

# -- 5. Run the next step.
echo Run next segment
sbatch {next_script_file}

pwd
date
