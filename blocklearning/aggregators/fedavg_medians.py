import numpy as np
from .utils import *

class FedAvgMediansAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    medians = []
    for t, trainer in enumerate(trainers):
      medians.append(np.median(scores[t]))
    return weighted_fed_avg(submissions, self.model_size, self.weights_loader, medians)
