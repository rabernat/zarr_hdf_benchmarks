# Zarr and HDF5 Benchmarks

Scripts for benchmarking performance of Zarr and HDF5 in different contexts.

## The Main Script

**`parallel_read_write.py`** is a command line tool for reading and writing data in parallel using MPI, HDF5, and zarr.

    Usage: parallel_read_write.py [OPTIONS]

    Options:
    --nsteps INTEGER           Number of iterations to perform
    --size INTEGER             Length of each row of array
    --output_dir TEXT          Where to write the data
    --compression [none|gzip]
    --nested                   whether to use zarr NestedDirectoryStore
    --help                     Show this message and exit.

## The Environment

I suspect that the results are quite sensitive the the MPI configuration.
The conda environment is specified in `environment.yaml`.
I am using all mpi libraries, hd5 libraries, etc installed from conda-forge.
This might not be optimal.

## Data

The data is output from the scripts in CSV format and committed directly to this repo.
The scripts can be run over and over, producing more results, which can just be added incrementally.
You should never have to delete data.

## PBS Scripts for Cheyenne

The following scripts can be run on Cheyenne in batch mode.
There are a few module tricks to make things work right.
Again, these could be affecting performance.

- `PBS_run_script_cheyenne_singlenode.sh` - profile read and write on a single node as function of MPI procs. Results stored in `data_cheyenne_singlenode`.
- `PBS_run_script_cheyenne_multinode.sh` - profile read and write on on multiple nodes using 9 mpiprocs per node. Results stored in `data_cheyenne_mpiprocs09`.

## Results Analysis

- `analyze_results.py <DATA_DIR>` - dump a bunch of results to the terminal in text form.
- `plot_all_results.ipynb` - notebook for plotting up the results.
