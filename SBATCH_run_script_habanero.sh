#!/bin/sh
#
#SBATCH --account=ocp
#SBATCH --job-name=hdfvszarr
#SBATCH --time=01:00:00
#SBATCH --exclusive
# #SBATCH --nodes=4
#SBATCH --nodes=16

module add anaconda/3-4.4.0
source activate hdf5_zarr

cd $SLURM_SUBMIT_DIR

script="python parallel_read_write.py --output_dir /rigel/ocp/users/ra2697/tmp --nsteps=40"

#for n in 1 3 6 12 24 48 96; do
#for n in `seq 24 24 384`; do
for n in `seq 96 96 384`; do
	echo Running with $n procs
	mpirun -np $n $script
done
