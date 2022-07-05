import numpy as np
from diffprivlib.mechanisms import GaussianAnalytic

class Gaussian():
  def __init__(self, epsilon, delta = 1e-6, sensitivity = 1):
    self.mech = GaussianAnalytic(epsilon=epsilon, delta=delta, sensitivity=sensitivity)

  def __call__(self, x, accuracy = 0):
    x = np.array(x)
    o = np.zeros_like(x)
    for i in np.arange(x.shape[0]):
      o[i] = self.mech.randomise(x[i])
    return o

class AdaptiveGaussian():
  def __init__(self, epsilon_start, epsilon_max, delta = 1e-6, sensitivity = 1) -> None:
    self.epsilon_max = epsilon_max
    self.current_epsilon = epsilon_start
    self.delta = delta
    self.sensitivity = sensitivity
    self.last_accuracy = 0

  def __call__(self, x, accuracy = 0):
    self.__update_epsilon(accuracy)
    priv = Gaussian(self.current_epsilon, delta=self.delta, sensitivity=self.sensitivity)
    return priv(x, accuracy)

  def __update_epsilon(self, accuracy):
    if accuracy <= self.last_accuracy:
      self.current_epsilon = min(self.current_epsilon + 1, self.epsilon_max)
    self.last_accuracy = accuracy
