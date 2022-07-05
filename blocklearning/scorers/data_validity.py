from .marginal_gain import MarginalGainScorer

class DataValidityScorer(MarginalGainScorer):
  def __init__(self, log, contract, model, weights_loader, val) -> None:
    super().__init__(log, contract, model, weights_loader, val)

  def score(self, round, trainers, submissions):
    return super().score(round, trainers, submissions)

