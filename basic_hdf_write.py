from mpi4py import MPI
import h5py
import numpy as np

rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)

f = h5py.File('parallel_test.hdf5', 'w', driver='mpio', comm=MPI.COMM_WORLD)

dset = f.create_dataset('test', (1, 1000), dtype='i',
                        chunks=(1, 1000), compression="gzip")
with dset.collective:
    dset[rank] = np.full(1000, rank)

f.close()
