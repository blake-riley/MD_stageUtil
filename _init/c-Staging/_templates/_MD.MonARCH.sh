#!/bin/bash

#SBATCH --job-name={systemname}.run{repl_num:02d}.{stage}{segment_num:03d}
# SBATCH --account=wc55
#SBATCH --mail-user={user_email}
#SBATCH --mail-type=FAIL
#SBATCH --output="{systemname}.run{repl_num:02d}.{stage}{segment_num:03d}.out"
#SBATCH --error="{systemname}.run{repl_num:02d}.{stage}{segment_num:03d}.err"

#SBATCH --ntasks=1
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

#SBATCH --time=0-24:00:00


#==============================================================
#                Script  for  MonARCH 
#==============================================================

# {stage}{segment_num:03d} of {systemname}.run{repl_num:02d}

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
{logfiles}

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
