import tensorflow as tf
import numpy as np

class Model():
  def __init__(self, model):
    self.model = model
    self.layers, self.count = self.__get_layer_info(model)

  def __get_layer_info(self, model):
    layers = []
    total = 0
    for layer in model.get_weights():
      shape = layer.shape
      weights = np.prod(shape)
      total += weights
      layers.append((shape, weights))
    return layers, total

  def train(self, x_train, y_train, x_val, y_val):
    history = self.model.fit(
      x_train,
      y_train,
      verbose=0,
      epochs=1,
      validation_data=(x_val, y_val)
    )

    return history.history

  def evaluate(self, x_val, y_val):
    return self.model.evaluate(
      x=x_val,
      y=y_val,
      verbose=0,
      return_dict=True
    )

  def get_weights(self):
    weights = self.model.get_weights()
    serialized = []
    for w in weights:
      serialized.extend(w.flatten().tolist())
    return np.array(serialized)

  def set_weights(self, serialized):
    if len(serialized) != self.count:
      raise Exception(f'Wrong number of serialized weights. Expected ${self.count}, got ${len(serialized)}')

    weights = []
    i = 0

    for (shape, count) in self.layers:
      w = serialized[i:i+count]
      i = i + count
      w = np.array(w)
      w = w.reshape(shape)
      weights.append(w)

    self.model.set_weights(weights)
