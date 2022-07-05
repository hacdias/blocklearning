import time
import json

class Aggregator():
  def __init__(self, contract, weights_loader, model, aggregator, with_scores = False, logger = None):
    self.logger = logger
    self.with_scores = with_scores
    self.weights_loader = weights_loader
    self.contract = contract
    self.aggregator = aggregator
    self.model = model
    self.__register()

  def aggregate(self):
    (round, trainers, submissions) = self.contract.get_submissions_for_aggregation()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'start', 'submissions': submissions, 'round': round, 'ts': time.time_ns() }))

    scorers = None
    scores = None

    if self.with_scores:
      (s_trainers, s_scorers, s_scores) = self.contract.get_scorings()
      scorers = s_scorers
      scores = s_scores

      if trainers != s_trainers:
        # If this ever happens, we must ensure that the order is the same for both.
        raise 'trainers must be in the same order as s_trainers'

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_start', 'round': round, 'ts': time.time_ns() }))

    new_weights = self.aggregator.aggregate(trainers, submissions, scorers, scores)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_end', 'round': round,'ts': time.time_ns() }))

    weights_cid = self.weights_loader.store(new_weights)
    self.contract.submit_aggregation(weights_cid)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'end', 'round': round, 'submissions': submissions, 'ts': time.time_ns(), 'new_weights': weights_cid }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_aggregator()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
