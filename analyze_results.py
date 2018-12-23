import pandas as pd
from glob import glob
dframes = [pd.read_csv(f) for f in glob('*.csv')]
df = pd.concat(dframes)
df['bandwidth'] = df.size_in_bytes / df.runtime
df.groupby(['nprocs', 'operation']).bandwidth.aggregate(['mean', 'std'])/1e6
