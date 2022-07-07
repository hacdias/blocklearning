# Hack path so we can load 'blocklearning'
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import logging
import time
import json
import utilities as utilities
import blocklearning

# Setup Log
log_file = '../../blocklearning-results/results/CURRENT/logs/manager.log'
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

@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--abi', default='../build/contracts/Vertical.json', help='contract abi file')
@click.option('--contract', required=True, help='contract address')
@click.option('--data-dir', default=utilities.default_datadir, help='ethereum data directory path')
@click.option('--rounds', default=1, type=click.INT, help='number of rounds')
def main(provider, abi, contract, data_dir, rounds):
  account_address, account_password = get_owner_account(data_dir)
  contract = blocklearning.Contract(log, provider, abi, account_address, account_password, contract)

  for i in range(0, rounds):
    log.info(json.dumps({ 'event': 'start', 'ts': time.time_ns() }))

    contract.start_round()
    round = contract.get_round()

    while contract.get_round_phase() != blocklearning.RoundPhase.WAITING_FOR_TERMINATION:
      time.sleep(0.25)

    contract.terminate_round()
    weights = contract.get_weights(round)

    log.info(json.dumps({ 'event': 'end', 'ts': time.time_ns(), 'round': round, 'weights': weights }))

main()
