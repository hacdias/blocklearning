import numpy as np

def numpy_load(file):
  with np.load(file, allow_pickle=True) as data:
    data = data['data'].tolist()
    return data['x'], data['y']

def numpy_normalize(data):
  if len(data) == 1:
    return data
  return (data - np.min(data)) / (np.max(data) - np.min(data))
