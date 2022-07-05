import logging

def setup_logger(filename, name):
  logging.basicConfig(level="INFO", handlers=[
    logging.StreamHandler(),
    logging.FileHandler(filename=filename, encoding='utf-8', mode='a+')
  ])
  return logging.getLogger(name)
