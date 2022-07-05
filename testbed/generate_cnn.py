import tensorflow as tf
import sys

def get_cnn(input_shape):
  model = tf.keras.models.Sequential()
  model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
  model.add(tf.keras.layers.MaxPooling2D((2, 2)))
  model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))
  model.add(tf.keras.layers.MaxPooling2D((2, 2)))
  model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))

  model.add(tf.keras.layers.Flatten())
  model.add(tf.keras.layers.Dense(64, activation='relu'))
  model.add(tf.keras.layers.Dense(10))

  optimizer = 'adam'
  loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
  metrics = ['sparse_categorical_accuracy']

  model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
  return model

def get_mnist_cnn():
  return get_cnn(input_shape=(28,28,1))

def get_cifar10_cnn():
  return get_cnn(input_shape=(32, 32, 3))

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print(f'Usage: python {sys.argv[0]} <dataset> <path>')
    exit(1)
  
  dataset = sys.argv[1]
  path = sys.argv[2]

  model = None
  
  if dataset == 'mnist':
    model = get_mnist_cnn()
  elif dataset == 'cifar10':
    model = get_cifar10_cnn()
  else:
    print('Dataset must be one of: mnist, cifar10')
    exit(1)

  model.save(path, save_format='h5')
