from .utils import Evaluator

class MarginalGainScorer():
  def __init__(self, log, contract, model, weights_loader, val) -> None:
    self.evaluator = Evaluator(log, contract, model, weights_loader, val)
    self.weights_loader = weights_loader
    self.c = {}

  def score(self, round, trainers, submissions):
    last_accuracy = self.evaluator.eval_round(round - 1)

    for i, submission in enumerate(submissions):
      trainer = trainers[i]
      if trainer not in self.c:
        self.c[trainer] = 0

      (_, _, _, weights_cid) = submission
      weights = self.weights_loader.load(weights_cid)
      accuracy = self.evaluator.eval(round, weights)
      self.c[trainer] += accuracy - last_accuracy

    scores = [0 if self.c[trainer] < 0 else self.c[trainer] for trainer in trainers]
    return trainers, scores
