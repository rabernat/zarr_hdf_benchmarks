#!/bin/bash
#PBS -N hdfzarr
#PBS -q regular
#PBS -A UCLB0005 
# Pangeo
# #PBS -A UCLB0022
#PBS -l select=8:ncpus=36:mpiprocs=9
#PBS -l walltime=04:00:00
#PBS -j oe
#PBS -m abe

# Setup Environment
#source /glade/work/$USER/zarr_hdf_venv/bin/activate
module purge
export PATH="/glade/u/home/rpa/miniconda3/bin:$PATH"
source activate hdf5_zarr 

# nead NCAR's openmpi for this to work on more than one node
module load intel/18.0.1 openmpi/3.1.0

cd $PBS_O_WORKDIR

SCRATCH=/glade/scratch/rpa 
NSTEPS=100
NLOOP=10

script="python -u -W ignore parallel_read_write.py"

for cs in 500000 1000000 2000000; do
	opts="--output_dir $SCRATCH --size $cs --nsteps=$NSTEPS"
	for n in 9 18 36 72; do
		for i in `seq 1 $NLOOP`; do
			mpirun -np $n $script $opts --nested > /dev/null
			mpirun -np $n $script $opts > /dev/null
		done
	done
done
