import numpy as np
from diffprivlib.mechanisms import GaussianAnalytic

class Gaussian():
  def __init__(self, epsilon, delta = 1e-6, sensitivity = 1):
    self.mech = GaussianAnalytic(epsilon=epsilon, delta=delta, sensitivity=sensitivity)

  def privatize(self, x):
    x = np.array(x)
    o = np.zeros_like(x)
    for i in np.arange(x.shape[0]):
      o[i] = self.mech.randomise(x[i])
    return o
