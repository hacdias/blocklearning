import numpy as np
from ..utilities import floats_to_ints

class MultiKrumScorer():
  def __init__(self, weights_loader) -> None:
    self.weights_loader = weights_loader

  def score(self, round, trainers, submissions):
    R = len(submissions)
    f = R // 3 - 1
    closest_updates = R - f - 2

    weights_cids = [cid for (_, _, _, cid) in submissions]
    weights = [self.weights_loader.load(cid) for cid in weights_cids]

    scores = []

    for i in range(len(weights)):
      dists = []

      for j in range(len(weights)):
        if i == j:
          continue
        dists.append(np.linalg.norm(weights[j] - weights[i]))

      dists_sorted = np.argsort(dists)[:closest_updates]
      score = np.array([dists[i] for i in dists_sorted]).sum()
      scores.append(score)

    scores = floats_to_ints(scores)
    return trainers, scores
