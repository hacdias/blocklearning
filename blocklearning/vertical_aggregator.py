import tensorflow as tf
import time
import json
from .utilities import float_to_int

class VerticalAggregator():
  def __init__(self, contract, datastore, model, labels, logger = None):
    self.logger = logger
    self.datastore = datastore
    self.contract = contract
    self.model = model
    self.labels = labels
    self.__register()

  def aggregate(self):
    (round, trainers, submissions) = self.contract.get_submissions_for_aggregation()

    weights_id = self.contract.get_weights(round)
    weights = self.datastore.load(weights_id)
    self.model.set_weights(weights  - 1)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'start', 'submissions': submissions, 'round': round, 'ts': time.time_ns() }))

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_start', 'round': round, 'ts': time.time_ns() }))

    outputs = [self.datastore.load(output_id) for (_, _, _, output_id) in submissions]
    outputs = [tf.Variable(o) for o in outputs]

    # 4. Top Model Forward Propagation (Server)
    with tf.GradientTape(persistent=True) as tape:
      tape.watch(outputs)
      logits = self.model.model(inputs=outputs, training=True)
      loss_value = self.model.model.loss(self.labels, logits)
      # server_losses[round] = loss_value.numpy()

    # 5. Top Model Backward Propagation (Server)
    server_grads = tape.gradient(loss_value, self.model.model.trainable_weights)
    client_grads = tape.gradient(loss_value, outputs)

    self.model.model.optimizer.apply_gradients(zip(server_grads, self.model.model.trainable_weights))

    y_true = tf.convert_to_tensor(self.labels)
    y_pred = logits

    self.model.model.compiled_metrics.update_state(y_true, y_pred)
    accuracy = self.model.model.metrics[0].result().numpy()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_end', 'round': round,'ts': time.time_ns() }))

    new_weights = self.model.get_weights()
    weights_id = self.datastore.store(new_weights)

    client_grads = [grad.numpy() for grad in client_grads]
    client_grads_ids = [self.datastore.store(grad) for grad in client_grads]

    self.contract.submit_aggregation_with_gradients(weights_id, trainers, client_grads_ids)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'end', 'round': round, 'submissions': submissions, 'ts': time.time_ns(), 'new_weights': weights_id, 'client_grads': client_grads_ids, 'accuracy': float_to_int(accuracy) }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_aggregator()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
