import json
import time
import tensorflow as tf

class VerticalTrainer():
  def __init__(self, contract, model, x_train, datastore, logger = None):
    self.logger = logger
    self.contract = contract
    self.x_train = x_train
    self.datastore = datastore
    self.model = model
    self.last_output = None
    self.__register()

  def forward(self):
    (round, _) = self.contract.get_training_round()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'forward_start', 'round': round,'ts': time.time_ns() }))

    # 2. Bottom Model Forward Propagation
    output = self.model.model(self.x_train, training=True)

    output = output.numpy()
    output_id = self.datastore.store(output)
    self.last_output = output

    # 3. Transfer Forward Output
    submission = {
      'trainingAccuracy': 0,
      'testingAccuracy': 0,
      'trainingDataPoints': len(self.x_train),
      'weights': output_id # We use the weights for the intermediate output in the vertical case.
    }

    self.contract.submit_submission(submission)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'forward_end', 'round': round, 'weights': output_id, 'ts': time.time_ns(), 'submission': submission }))

  def backward(self):
    # 6. Backward output transmission
    output_grads_id = self.contract.get_gradient()
    output_grads = self.datastore.load(output_grads_id)
    output_grads = tf.Tensor(output_grads)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'backward_start', 'round': round,'ts': time.time_ns() }))

    # 7. Bottom Model Backward Propagation
    expected = tf.Variable(self.last_output)
    self.last_output = None

    self.model.model.optimizer.apply_gradients(zip([output_grads], [expected]))

    with tf.GradientTape(persistent=True) as tape:
      prediction = self.model.model(self.x_train, training=False)
      loss_value = self.model.model.loss(expected, prediction)

    grads = tape.gradient(loss_value, self.model.model.trainable_weights)
    self.model.model.optimizer.apply_gradients(zip(grads, self.model.model.trainable_weights))

    self.contract.confirm_backpropagation()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'backward_end', 'round': round, 'output_grads_id': output_grads_id, 'ts': time.time_ns() }))

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_trainer()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
