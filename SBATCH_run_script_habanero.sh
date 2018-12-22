#!/bin/sh
#
#SBATCH --account=ocp
#SBATCH --job-name=hdfvszarr
#SBATCH --time=00:05:00
#SBATCH --exclusive
#SBATCH --nodes=1

module add anaconda/3-4.4.0
source activate hdf5_zarr

cd $SLURM_SUBMIT_DIR

mpirun -np 24 python parallel_write.py --output_dir /rigel/ocp/users/ra2697/tmp --nsteps=20
