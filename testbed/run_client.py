import web3
import time
import click
import requests
import blocklearning
import blocklearning.scorers as scorers
import blocklearning.model_loaders as model_loaders
import blocklearning.weights_loaders as weights_loaders
import blocklearning.utilities as utilities
import blocklearning.diffpriv as diffpriv
from blocklearning.contract import RoundPhase

@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS API provider')
@click.option('--abi', default='./build/contracts/NoScoring.json', help='contract abi file')
@click.option('--account', help='ethereum account to use for this computing server', required=True)
@click.option('--passphrase', help='passphrase to unlock account', required=True)
@click.option('--contract', help='contract address', required=True)
@click.option('--log', help='logging file', required=True)
@click.option('--train', help='training data .npz file', required=True)
@click.option('--test', help='training data .npz file', required=True)
@click.option('--scoring', default=None, help='scoring method')
def main(provider, ipfs, abi, account, passphrase, contract, log, train, test, scoring):
  log = utilities.setup_logger(log, "client")
  weights_loader = weights_loaders.IpfsWeightsLoader(ipfs)

  # Load Training and Testing Data
  x_train, y_train = utilities.numpy_load(train)
  x_test, y_test = utilities.numpy_load(test)

  # Get Contract and Register as Trainer
  contract = blocklearning.Contract(log, provider, abi, account, passphrase, contract)

  # Load Model
  model_loader = model_loaders.IpfsModelLoader(contract, weights_loader, ipfs_api=ipfs)
  model = model_loader.load()

  # Set Gaussian Differential Privacy
  priv = None
  # priv = diffpriv.Gaussian(epsilon=5, sensitivity=1e-1/3)
  # priv = diffpriv.Gaussian(epsilon=1, sensitivity=1e-1/2)

  trainer = blocklearning.Trainer(contract, weights_loader, model, (x_train, y_train, x_test, y_test), logger=log, priv=priv)

  # Setup the scorer for the clients. Only Marginal Gain and BlockFlow run on the client
  # device and use the client's testing dataset as the validation dataset for the scores.
  scorer = None
  if scoring == 'marginal-gain':
    scorer = scorers.MarginalGainScorer(log, contract, model, weights_loader, test)
  elif scoring == 'blockflow':
    scorer = scorers.AccuracyScorer(log, contract, model, weights_loader, test)
  if scorer is not None:
    scorer = blocklearning.Scorer(contract, scorer=scorer, logger=log)

  while True:
    try:
      phase = contract.get_round_phase()
      if phase == RoundPhase.WAITING_FOR_SUBMISSIONS:
        trainer.train()
      elif phase == RoundPhase.WAITING_FOR_SCORINGS and scorer is not None:
        scorer.score()
    except web3.exceptions.ContractLogicError as err:
      print(err, flush=True)
    except requests.exceptions.ReadTimeout as err:
      print(err, flush=True)

    time.sleep(0.5)

main()
