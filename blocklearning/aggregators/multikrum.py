import numpy as np
from .utils import *

class MultiKrumAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    medians = []
    for t, trainer in enumerate(trainers):
      medians.append(np.median(scores[t]))
    print('medians', medians)

    R = len(submissions)
    f = R // 3 - 1

    sorted_idxs = np.argsort(medians)
    lowest_idxs = sorted_idxs[:R-f]
    selected_submissions = [submissions[i] for i in lowest_idxs]
    selected_weights = [samples for (_, _, samples, _) in selected_submissions]

    return weighted_fed_avg(selected_submissions, self.model_size, self.weights_loader, selected_weights)
