import os
import tempfile
import tensorflow as tf
from .model import Model

class IpfsModelLoader():
  def __init__(self, contract, weights_loader, ipfs_api = '/ip4/127.0.0.1/tcp/5001') -> None:
    self.contract = contract
    self.weights_loader = weights_loader
    self.ipfs_api = ipfs_api
    pass

  def __load(self, model_cid, weights_cid = ""):
    with tempfile.TemporaryDirectory() as tempdir:
      model_path = os.path.join(tempdir, 'model.h5')
      os.system(f"ipfs get --api {self.ipfs_api} -o {model_path} {model_cid}")
      model = tf.keras.models.load_model(model_path)

    if weights_cid != "":
      weights = self.weights_loader.load(weights_cid)
      model.set_weights(weights)

    return Model(model)

  def load(self):
    model_cid = self.contract.get_model()
    weights_cid = self.contract.get_weights(0)
    return self.__load(model_cid, weights_cid)

  def load_top(self):
    model_cid = self.contract.get_top_model()
    return self.__load(model_cid)

  def load_bottom(self):
    model_cid = self.contract.get_bottom_model()
    return self.__load(model_cid)
