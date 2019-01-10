import sys
import pandas as pd
from glob import glob
import os

if len(sys.argv)>1:
    glob_dir = sys.argv[1]
else:
    glob_dir = './'

dframes = [pd.read_csv(f) for f in glob(os.path.join(glob_dir, '*.csv'))]
df = pd.concat(dframes)
# MB/s
df['bandwidth'] = df.size_in_bytes * df.nprocs / df.runtime / 1e6
res = (df.groupby(['operation', 'nprocs', 'size_in_bytes', 'format'])
         .bandwidth
         .aggregate(['count', 'mean', 'std']))
print(res)

