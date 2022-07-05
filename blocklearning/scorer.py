import time
import json

class Scorer():
  def __init__(self, contract, scorer, logger = None):
    self.logger = logger
    self.contract = contract
    self.scorer = scorer
    self.__register()

  def score(self):
    (round, submissions_trainers, submissions) = self.contract.get_submissions_for_scoring()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'score_start', 'submissions': submissions, 'round': round, 'ts': time.time_ns() }))

    scores_trainers, scores = self.scorer.score(round, submissions_trainers, submissions)
    self.contract.submit_scorings(scores_trainers, scores)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'score_end', 'round': round, 'submissions': submissions, 'ts': time.time_ns(), 'submissions_trainers': submissions_trainers, 'scores': scores }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_scorer()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
