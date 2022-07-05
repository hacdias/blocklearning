import numpy as np
from .utils import *

class DataValidityAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    selected_submissions = []
    for t, trainer in enumerate(trainers):
      if np.mean(scores[t]) > 0:
        selected_submissions.append(submissions[t])

    samples = [samples for (_, _, samples, _) in selected_submissions]
    return weighted_fed_avg(selected_submissions, self.model_size, self.weights_loader, samples)
