import numpy as np
from .utils import Evaluator

class AccuracyScorer():
  def __init__(self, log, contract, model, weights_loader, val) -> None:
    self.evaluator = Evaluator(log, contract, model, weights_loader, val)
    self.weights_loader = weights_loader

  def score(self, round, trainers, submissions):
    accuracies = []

    for submission in submissions:
      (_, _, _, weights_cid) = submission
      weights = self.weights_loader.load(weights_cid)
      accuracy = self.evaluator.eval(round, weights)
      accuracies.append(accuracy)

    return trainers, accuracies
