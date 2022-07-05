import json
import time
from ..utilities import numpy_load, float_to_int

class Evaluator():
  def __init__(self, log, contract, model, weights_loader, val) -> None:
    self.log = log
    self.contract = contract
    self.model = model
    self.weights_loader = weights_loader
    x_val, y_val = numpy_load(val)
    self.val = (x_val, y_val)

  def eval_round(self, round):
    if round == 0:
      return float_to_int(0)
    weights_cid = self.contract.get_weights(round)
    weights = self.weights_loader.load(weights_cid)
    return self.eval(round, weights)

  def eval(self, round, weights):
    self.model.set_weights(weights)
    self.log.info(json.dumps({ 'event': 'eval_start', 'round': round,'ts': time.time_ns() }))
    metrics = self.model.evaluate(self.val[0], self.val[1])
    accuracy = float_to_int(metrics['sparse_categorical_accuracy'])
    self.log.info(json.dumps({ 'event': 'eval_end', 'round': round,'ts': time.time_ns() }))
    return accuracy
