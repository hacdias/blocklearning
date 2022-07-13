import json
import time
from enum import Enum
from web3 import Web3
from web3.middleware import geth_poa_middleware

def get_web3(provider, abi_file, account, passphrase, contract):
  provider = Web3.HTTPProvider(provider)
  abi = get_abi(abi_file)

  web3 = Web3(provider)
  web3.middleware_onion.inject(geth_poa_middleware, layer=0)
  web3.geth.personal.unlock_account(account, passphrase, 600)

  contract = web3.eth.contract(address=contract, abi=abi)
  defaultOpts = { 'from': account }

  return (web3, contract, defaultOpts)

def get_abi(filename):
  with open(filename) as file:
    contract_json = json.load(file)
  return contract_json['abi']

class RoundPhase(Enum):
  STOPPED = 0
  WAITING_FOR_SUBMISSIONS = 1
  WAITING_FOR_SCORINGS = 2
  WAITING_FOR_AGGREGATIONS = 3
  WAITING_FOR_TERMINATION = 4
  WAITING_FOR_BACKPROPAGATION = 5

class Contract():
  def __init__(self, log, provider, abi_file, account, passphrase, contract_address):
    self.log = log
    self.account = account
    self.passphrase = passphrase
    (web3, contract, default_opts) = get_web3(provider, abi_file, account, passphrase, contract_address)
    self.web3 = web3
    self.contract = contract
    self.default_opts = default_opts

  def get_model(self):
    return self.contract.functions.model().call(self.default_opts)

  def get_top_model(self):
    return self.get_model()

  def get_bottom_model(self):
    return self.contract.functions.bottomModel().call(self.default_opts)

  def get_weights(self, round):
    return self.contract.functions.weights(round).call(self.default_opts)

  def get_round(self):
    return self.contract.functions.round().call(self.default_opts)

  def get_round_phase(self):
    return RoundPhase(self.contract.functions.roundPhase().call(self.default_opts))

  def get_trainers(self):
    return self.contract.functions.getTrainers().call(self.default_opts)

  def get_aggregators(self):
    return self.contract.functions.getAggregators().call(self.default_opts)

  def get_scorers(self):
    return self.contract.functions.getScorers().call(self.default_opts)

  def get_training_round(self):
    [round, weights_cid] = self.contract.functions.getRoundForTraining().call(self.default_opts)
    return (round, weights_cid)

  def get_submissions_for_scoring(self):
    [round, trainers, submissions] = self.contract.functions.getUpdatesForScore().call(self.default_opts)
    return (round, trainers, submissions)

  def get_submissions_for_aggregation(self):
    [round, trainers, submissions] = self.contract.functions.getUpdatesForAggregation().call(self.default_opts)
    return (round, trainers, submissions)

  def get_scorings(self):
    [trainers, scorers, scores] = self.contract.functions.getScores().call(self.default_opts)
    return (trainers, scorers, scores)

  def get_gradient(self):
    return self.contract.functions.getGradient().call(self.default_opts)

  def register_as_trainer(self):
    self.__unlock_account()
    if not self.contract.functions.registeredTrainers(self.account).call(self.default_opts):
      tx = self.contract.functions.registerTrainer().transact(self.default_opts)
      return tx, self.__wait_tx(tx)

  def register_as_scorer(self):
    self.__unlock_account()
    if not self.contract.functions.registeredScorers(self.account).call(self.default_opts):
      tx = self.contract.functions.registerScorer().transact(self.default_opts)
      return tx, self.__wait_tx(tx)

  def register_as_aggregator(self):
    self.__unlock_account()
    if not self.contract.functions.registeredAggregators(self.account).call(self.default_opts):
      tx = self.contract.functions.registerAggregator().transact(self.default_opts)
      return tx, self.__wait_tx(tx)

  def submit_submission(self, submission):
    self.__unlock_account()
    tx = self.contract.functions.submitUpdate(submission).transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def submit_scorings(self, trainers, scores):
    self.__unlock_account()
    tx = self.contract.functions.submitScores(trainers, scores).transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def submit_aggregation(self, weights_id):
    self.__unlock_account()
    tx = self.contract.functions.submitAggregation(weights_id).transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def submit_aggregation_with_gradients(self, weights_id, trainers, gradients_ids):
    self.__unlock_account()
    tx = self.contract.functions.submitAggregationWithGradients(weights_id, trainers, gradients_ids).transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def confirm_backpropagation(self):
    self.__unlock_account()
    tx = self.contract.functions.confirmBackpropagation().transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def start_round(self, *args):
    self.__unlock_account()
    tx = self.contract.functions.startRound(*args).transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def terminate_round(self):
    self.__unlock_account()
    tx = self.contract.functions.terminateRound().transact(self.default_opts)
    return tx, self.__wait_tx(tx)

  def __wait_tx(self, tx):
    self.log.info(json.dumps({ 'event': 'tx_start', 'tx': tx.hex(), 'ts': time.time_ns() }))
    receipt = self.web3.eth.wait_for_transaction_receipt(tx)
    self.log.info(json.dumps({ 'event': 'tx_end', 'tx': tx.hex(), 'gas': receipt.gasUsed, 'ts': time.time_ns() }))
    return receipt

  def __unlock_account(self):
    self.web3.geth.personal.unlock_account(self.account, self.passphrase, 600)
