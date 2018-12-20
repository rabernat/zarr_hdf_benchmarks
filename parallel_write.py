from mpi4py import MPI
#import h5py
import zarr
import numpy as np
from time import time
import click
import os


@click.command()
@click.option('--nsteps', default=1, help="Number of iterations to perform")
@click.option('--size', default=1000000, help="Length of each row of array")
@click.option('--output_dir', default='./', help="Where to write the data")
def main(nsteps, size, output_dir):
    comm = MPI.COMM_WORLD
    nprocs = comm.Get_size()
    rank = comm.Get_rank()

    x = np.arange(size)
    shape = (nsteps, nprocs, size)
    zarr_chunks = (1, 1, size)

    # HDF code
    #f = h5py.File('parallel_test.hdf5', 'w', driver='mpio', comm=MPI.COMM_WORLD)
    #dset = f.create_dataset('test', (4,), dtype='i')

    # create file in first rank
    fname = os.path.join(output_dir, 'parallel_test.zarr')
    if rank==0:
        z_array = zarr.open(fname, mode='w', shape=shape,
                            chunks=zarr_chunks, dtype='f8')
    # block all processes until this is done
    comm.Barrier()

    # reopen file from all ranks to write
    z_array = zarr.open(fname, mode='r+')
    # emulate a scientific simulation
    for n in range(nsteps):
        # random data, signal plus noise
        data = np.cos(20 * np.pi * x / size) + 0.1 * np.random.rand(size)
        z_array[n, rank] = data
        # barrier needed at the end of each timestep
        comm.Barrier()

if __name__ == "__main__":
    main()
