from mpi4py import MPI
import h5py
import zarr
import numpy as np
import click
import os
import shutil
import time
import uuid

from diagtimer import DiagnosticTimer


@click.command()
@click.option('--nsteps', default=1, help="Number of iterations to perform")
@click.option('--size', default=1000000, help="Length of each row of array")
@click.option('--output_dir', default='./', help="Where to write the data")
@click.option('--compression', default='none', type=click.Choice(['none', 'gzip']))
def main(nsteps, size, output_dir, compression):
    timer = DiagnosticTimer()

    comm = MPI.COMM_WORLD
    nprocs = comm.Get_size()
    rank = comm.Get_rank()

    x = np.arange(size)
    dtype = 'f8'
    shape = (nsteps, nprocs, size)
    # http://docs.h5py.org/en/stable/high/dataset.html#chunked-storage
    # HDF recommends to keep the total size of your chunks between 10 KiB and 1 MiB, larger for larger datasets
    chunks = (1, 1, size)
    chunk_size = np.dtype(dtype).itemsize * size

    # set up compression options
    # perhaps hdf filters can't be used in parallel writes
    # https://forum.hdfgroup.org/t/parallel-i-o-does-not-support-filters-yet/884/6
    # https://forum.hdfgroup.org/t/compressed-parallel-writing-problem/4979
    
    hdf_compression_kw = {}
    hdf_compression_type, hdf_compression_level = None, None
    if compression=='none':
        zarr_compression_kw = {'compressor': None}
        zarr_compression_type, zarr_compression_level = None, None
    elif compression=='gzip':
        zarr_compression_type, zarr_compression_level = 'gzip', 4
        zarr_compression_kw = dict(compressor=zarr.GZip(level=4))


    zarr_log_options = dict(nprocs=nprocs, size_in_bytes=chunk_size, format='zarr',
                            compression=zarr_compression_type,
                            compression_level=zarr_compression_level)
    hdf_log_options = dict(nprocs=nprocs, size_in_bytes=chunk_size, format='hdf',
                            compression=hdf_compression_type,
                            compression_level=hdf_compression_level)

    uid = str(uuid.uuid1())[:8]
    fname_base = f'parallel_test_{uid}'
    ### HDF initialization -- autmatically works in parallel
    hfname = os.path.join(output_dir, f'{fname_base}.hdf5')
    hfile = h5py.File(hfname, 'w', driver='mpio', comm=MPI.COMM_WORLD)
    hdset = hfile.create_dataset('test', shape, dtype=dtype, chunks=chunks,
                                 **hdf_compression_kw)

    ### Zarr initialization -- more manual steps
    # create file in first rank
    fname = os.path.join(output_dir, f'{fname_base}.zarr')
    if rank==0:
        z_array = zarr.open(fname, mode='w', shape=shape,
                            chunks=chunks, dtype=dtype,
                            **zarr_compression_kw)
    # block all processes until this is done
    comm.Barrier()
    # reopen file from all ranks to write
    z_array = zarr.open(fname, mode='r+')

    # emulate a scientific simulation
    for n in range(nsteps):
        # random data, signal plus noise
        data = (np.cos(20 * np.pi * x / size + 2*np.pi*np.random.rand()) +
                0.1 * np.random.rand(size))
        with timer.time(operation='write', **zarr_log_options):
            z_array[n, rank] = data
            # barrier needed at the end of each timestep
            comm.Barrier()
        with timer.time(operation='write', **hdf_log_options):
            hdset[n, rank] = data
            # do we need to close or sync?
            # hfile.flush()
            comm.Barrier()
    hfile.close()

    # now read back the data
    hfile = h5py.File(hfname, 'r', driver='mpio', comm=MPI.COMM_WORLD)
    hdset = hfile['test']
    z_array = zarr.open(fname, mode='r')

    for n in range(nsteps):
        # random data, signal plus noise
        with timer.time(operation='read', **zarr_log_options):
            zdata = z_array[n, rank]
            comm.Barrier()
        with timer.time(operation='read', **hdf_log_options):
            hdata = hdset[n, rank]
            comm.Barrier()
        np.testing.assert_allclose(zdata, hdata)
    hfile.close()

    if rank==0:
        # cleanup temporary files
        shutil.rmtree(fname)
        os.remove(hfname)
        # output results
        df = timer.dataframe()
        df.to_csv('parallel_read_write_%s.csv' % time.strftime('%Y-%m-%d_%H%M.%S'),
                  index=False)

if __name__ == "__main__":
    main()
