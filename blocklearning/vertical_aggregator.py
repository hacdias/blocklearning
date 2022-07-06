import tensorflow as tf
import time
import json

class VerticalAggregator():
  def __init__(self, contract, weights_loader, model, labels, logger = None):
    self.logger = logger
    self.weights_loader = weights_loader
    self.contract = contract
    self.model = model
    self.labels = labels
    self.__register()

  def aggregate(self):
    (round, trainers, submissions) = self.contract.get_submissions_for_aggregation()

    weights_id = self.contract.get_weights(round)
    weights = self.weights_loader.load(weights_id)
    self.model.set_weights(weights  - 1)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'start', 'submissions': submissions, 'round': round, 'ts': time.time_ns() }))

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_start', 'round': round, 'ts': time.time_ns() }))

    outputs = [self.weights_loader.load(output_id) for (_, _, _, output_id) in submissions]
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

    # y_true = tf.convert_to_tensor(self.labels)
    # y_pred = logits

    # server_model.compiled_metrics.update_state(y_true, y_pred)
    # print(round, {m.name: m.result().numpy() for m in server_model.metrics})

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'fedavg_end', 'round': round,'ts': time.time_ns() }))

    new_weights = self.model.get_weights()
    weights_id = self.weights_loader.store(new_weights)

    client_grads = [grad.numpy() for grad in client_grads]
    client_grads_ids = [self.weights_loader.store(grad) for grad in client_grads]

    # TODO: self.contract.submit_aggregation(weights_cid, client_grads_cids)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'end', 'round': round, 'submissions': submissions, 'ts': time.time_ns(), 'new_weights': weights_id }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_aggregator()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
