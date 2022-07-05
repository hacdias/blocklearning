from .utils import *

class FedAvgAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    samples = [samples for (_, _, samples, _) in submissions]
    return weighted_fed_avg(submissions, self.model_size, self.weights_loader, samples)
