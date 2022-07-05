# Hack path so we can load 'blocklearning'
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
import time
import random
import json
import utilities as utilities
import blocklearning
import blocklearning.model_loaders as model_loaders
import blocklearning.weights_loaders as weights_loaders
import blocklearning.utilities as butilities

# Setup Log
log_file = '../experiment/results/CURRENT/logs/manager.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
if os.path.exists(log_file):
  print('a log already exists, please make sure to save the previous logs')
  exit(1)

logging.basicConfig(level="INFO", handlers=[
  logging.StreamHandler(),
  logging.FileHandler(filename=log_file, encoding='utf-8', mode='a+')
])
log = logging.getLogger("manager")

def get_owner_account(data_dir):
  accounts = utilities.read_json(os.path.join(data_dir, 'accounts.json'))
  account_address = list(accounts['owner'].keys())[0]
  account_password = accounts['owner'][account_address]
  return account_address, account_password

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data-dir', type=str, help='ethereum data directory path', default=utilities.default_datadir)
  parser.add_argument('--provider', type=str, help='ethereum API provider', default='http://127.0.0.1:8545')
  parser.add_argument('--rounds', type=int, help='how many rounds to run', default=1)
  parser.add_argument('--contract', type=str, help='contract address', required=True)
  parser.add_argument('--abi', type=str, help='abi path', default='../build/contracts/NoScoring.json')
  parser.add_argument('--trainers', type=str, help='trainers selection mode', default='random')
  parser.add_argument('--aggregators', type=str, help='aggregators selection mod', default='all')
  parser.add_argument('--scoring', type=str, help='scoring mechanism', default='none')
  parser.add_argument('--val', type=str, help='validation data', default='./datasets/mnist/5/owner_val.npz')
  args = parser.parse_args()

  account_address, account_password = get_owner_account(args.data_dir)

  contract = blocklearning.Contract(log, args.provider, args.abi, account_address, account_password, args.contract)
  weights_loader = weights_loaders.IpfsWeightsLoader()
  model_loader = model_loaders.IpfsModelLoader(contract, weights_loader)
  model = model_loader.load()

  weights_count = len(model.get_weights())
  x_val, y_val = butilities.numpy_load(args.val)

  aggregator_index = -1

  def choose_participants():
    trainers = contract.get_trainers()
    aggregators = contract.get_aggregators()
    scorers = [] if args.scoring == 'none' else contract.get_scorers()

    global aggregator_index

    round_trainers = None
    round_aggregators = None
    round_scorers = None

    if args.trainers == 'random':
      n = random.randint(len(trainers) // 2, len(trainers))
      round_trainers = random.sample(trainers, n)
    elif args.trainers == 'fcfs':
      round_trainers = random.randint(len(trainers) // 2, len(trainers))
    elif args.trainers == 'all':
      round_trainers = trainers

    if args.aggregators == 'all':
      round_aggregators = aggregators
    elif args.aggregators == 'rr':
      aggregator_index = (aggregator_index + 1) % len(aggregators)
      round_aggregators = [aggregators[aggregator_index]]

    if args.scoring == 'multi-krum' or args.scoring=='data-validity':
      round_scorers = round_aggregators
    elif args.scoring == 'blockflow' or args.scoring == 'marginal-gain':
      round_scorers = round_trainers

    return round_trainers, round_aggregators, round_scorers

  def eval_model(weights):
    log.info(json.dumps({ 'event': 'eval_start', 'ts': time.time_ns(), 'round': round }))
    model.set_weights(weights_loader.load(weights))
    metrics = model.evaluate(x_val, y_val)
    accuracy = metrics['sparse_categorical_accuracy']
    log.info(json.dumps({ 'event': 'eval_end', 'ts': time.time_ns(), 'round': round }))
    return accuracy

  for i in range(0, args.rounds):
    trainers, aggregators, scorers = choose_participants()
    log.info(json.dumps({ 'event': 'start', 'trainers': trainers, 'aggregators': aggregators, 'scorers': scorers, 'ts': time.time_ns() }))

    if args.trainers == 'fcfs':
      contract.start_quorum_round(trainers, aggregators)
    elif args.scoring != 'none':
      contract.start_round_with_scoring(trainers, aggregators, scorers)
    else:
      contract.start_round(trainers, aggregators)

    round = contract.get_round()

    while contract.get_round_phase() != blocklearning.RoundPhase.WAITING_FOR_TERMINATION:
      time.sleep(0.25)

    contract.terminate_round()
    weights = contract.get_weights(round)
    accuracy = eval_model(weights)

    log.info(json.dumps({ 'event': 'end', 'ts': time.time_ns(), 'round': round, 'weights': weights, 'accuracy': butilities.float_to_int(accuracy) }))
