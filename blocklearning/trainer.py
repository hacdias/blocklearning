import json
import time
from .utilities import float_to_int

class Trainer():
  def __init__(self, contract, weights_loader, model, data, logger = None, priv = None):
    self.logger = logger
    self.priv = priv
    self.weights_loader = weights_loader
    self.contract = contract
    (self.x_train, self.y_train, self.x_test, self.y_test) = data
    self.model = model
    self.__register()

  def train(self):
    (round, weights_id) = self.contract.get_training_round()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'start', 'round': round, 'weights': weights_id, 'ts': time.time_ns() }))

    if weights_id != '':
      weights = self.weights_loader.load(weights_id)
      self.model.set_weights(weights)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'train_start', 'round': round,'ts': time.time_ns() }))

    history = self.model.train(self.x_train, self.y_train, self.x_test, self.y_test)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'train_end', 'round': round,'ts': time.time_ns() }))

    trainingAccuracy = float_to_int(history['sparse_categorical_accuracy'][0])
    validationAccuracy = float_to_int(history['val_sparse_categorical_accuracy'][0])

    weights = self.model.get_weights()
    if self.priv is not None:
      weights = self.priv(weights, validationAccuracy)

    weights_id = self.weights_loader.store(weights)

    submission = {
      'trainingAccuracy': trainingAccuracy,
      'testingAccuracy': validationAccuracy,
      'trainingDataPoints': len(self.x_train),
      'weights': weights_id
    }
    self.contract.submit_submission(submission)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'end', 'round': round, 'weights': weights_id, 'ts': time.time_ns(), 'submission': submission }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_trainer()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
