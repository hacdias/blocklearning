import numpy as np
from .utils import *
from ..utilities import int_to_float

class BlockFlowAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions, scorers = None, scores = None):
    if len(trainers) != len(scorers):
      raise 'length of trainers must match length of scorers'

    if len(np.intersect1d(trainers, scorers)) != len(trainers):
      raise 'trainers and scorers must be the same'

    N = len(trainers)
    print('N', N, flush=True)

    # Scores need to be between 0.0 and 1.0 so we revert the int transformation.
    # Also s[a][k] is the score given by a to k, so the inverse of scores.
    s = [[int_to_float(scores[k][a]) for k in range(N)] for a in range(N)]

    m = [0 for _ in trainers]
    for k in range(N):
      m[k] = np.median([s[a][k] for a in range(N)])

    m_ = [0 for _ in trainers]
    for k in range(N):
      m_[k] = m[k] / np.max(m)

    t = [[0 for _ in range(N)] for _ in range(N)]
    t_ = [[0 for _ in range(N)] for _ in range(N)]
    for a in range(N):
      for k in range(N):
        t[a][k] = abs(s[a][k] - m[k])
        t_[a][k] = max(0, (0.5 - t[a][k]) / (0.5 + t[a][k]))

    d = [0 for _ in trainers]
    for a in range(N):
      d[a] = min(t_[a][k] for k in range(N))

    d_ = [0 for _ in trainers]
    for a in range(N):
      d_[a] = d[a] / np.max(d)

    p = [0 for _ in trainers]
    for k in range(N):
      p[k] = min(m_[k], d_[k])

    return weighted_fed_avg(submissions, self.model_size, self.weights_loader, p)
