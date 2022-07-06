import json
import time
from .utilities import float_to_int

class VerticalTrainer():
  def __init__(self, contract, model, x, datastore, logger = None):
    self.logger = logger
    self.contract = contract
    self.x = x
    self.datastore = datastore
    self.model = model
    self.__register()

  def forward(self):
    (round, _) = self.contract.get_training_round()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'start', 'round': round, 'ts': time.time_ns() }))

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'forward_start', 'round': round,'ts': time.time_ns() }))

    # 2. Bottom Model Forward Propagation
    output = self.model.model(self.x, training=True)

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'forward_end', 'round': round,'ts': time.time_ns() }))

    output = output.numpy()
    output_id = self.datastore.store(output)

    submission = {
      'trainingAccuracy': 0,
      'testingAccuracy': 0,
      'trainingDataPoints': len(self.x_train),
      'weights': output_id
    }

    pass

  def backward(self):
    
    # model, output, output_grads = client_models[i], outputs[i], client_grads[i]

    # expected = tf.Variable(output)
    # model.optimizer.apply_gradients(zip([output_grads], [expected]))

    # with tf.GradientTape(persistent=True) as tape:
    #   prediction = model(X[i], training=False)
    #   loss_value = model.loss(expected, prediction)
    #   losses[i][round] = loss_value.numpy()

    # grads = tape.gradient(loss_value, model.trainable_weights)
    # # print('All zeros?', list(np.all(grad.numpy().flatten() == 0) for grad in grads))
    # model.optimizer.apply_gradients(zip(grads, model.trainable_weights))

    pass

  # Private utilities
  def __register(self):
    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'checking_registration', 'ts': time.time_ns() }))

    self.contract.register_as_trainer()

    if self.logger is not None:
      self.logger.info(json.dumps({ 'event': 'registration_checked', 'ts': time.time_ns() }))
