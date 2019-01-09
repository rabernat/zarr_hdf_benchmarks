import pandas as pd
from glob import glob
dframes = [pd.read_csv(f) for f in glob('*.csv')]
df = pd.concat(dframes)
df['bandwidth'] = df.size_in_bytes * df.nprocs / df.runtime
res = df.groupby(['operation', 'nprocs', 'format']).bandwidth.aggregate(['mean', 'std'])/1e6
print(res)
