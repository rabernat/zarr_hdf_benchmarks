import sys
import pandas as pd
from glob import glob
import os

df = pd.read_csv('ranks.log')

df['node'] = df['rank'] // 36
res = df.groupby(['operation', 'nprocs', 'node', 'format']).runtime.aggregate(['mean', 'std'])
print(res)
