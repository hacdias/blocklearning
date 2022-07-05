import numpy as np
from .utils import *

class FedAvgMeansAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    means = []
    for t, trainer in enumerate(trainers):
      means.append(np.mean(scores[t]))
    return weighted_fed_avg(submissions, self.model_size, self.weights_loader, means)
