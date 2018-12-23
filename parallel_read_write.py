from mpi4py import MPI
#import h5py
import zarr
import numpy as np
import click
import os
import shutil
import time

from diagtimer import DiagnosticTimer


@click.command()
@click.option('--nsteps', default=1, help="Number of iterations to perform")
@click.option('--size', default=1000000, help="Length of each row of array")
@click.option('--output_dir', default='./', help="Where to write the data")
def main(nsteps, size, output_dir):
    timer = DiagnosticTimer()

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
        total_bytes = nprocs*data.nbytes
        with timer.time(operation='write', nprocs=nprocs, size_in_bytes=total_bytes, format='zarr'):
            z_array[n, rank] = data
            # barrier needed at the end of each timestep
            comm.Barrier()

    # now read back the data
    z_array = zarr.open(fname, mode='r')
    for n in range(nsteps):
        # random data, signal plus noise
        with timer.time(operation='read', nprocs=nprocs, size_in_bytes=total_bytes, format='zarr'):
            _ = z_array[n, rank]
            comm.Barrier()

    if rank==0:
        # cleanup temporary files
        shutil.rmtree(fname)
        # output results
        df = timer.dataframe()
        df.to_csv('parallel_read_write_%s.csv' % time.strftime('%Y-%m-%d_%H%M.%S'),
                  index=False)

if __name__ == "__main__":
    main()
