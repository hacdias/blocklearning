import web3
import time
import click
import requests
import blocklearning
import blocklearning.model_loaders as model_loaders
import blocklearning.weights_loaders as weights_loaders
import blocklearning.utilities as utilities
from blocklearning.contract import RoundPhase

@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS API provider')
@click.option('--abi', default='./build/contracts/NoScore.json', help='contract abi file')
@click.option('--account', help='ethereum account to use for this computing server', required=True)
@click.option('--passphrase', help='passphrase to unlock account', required=True)
@click.option('--contract', help='contract address', required=True)
@click.option('--log', help='logging file', required=True)
@click.option('--train', help='training data .npz file', required=True)
def main(provider, ipfs, abi, account, passphrase, contract, log, train):
  log = utilities.setup_logger(log, "client")
  datastore = weights_loaders.IpfsWeightsLoader(ipfs)

  # Load Training Data
  x_train, _ = utilities.numpy_load(train)

  # Get Contract and Register as Trainer
  contract = blocklearning.Contract(log, provider, abi, account, passphrase, contract)

  # Load Model
  model_loader = model_loaders.IpfsModelLoader(contract, datastore, ipfs_api=ipfs)
  model = model_loader.load_bottom()

  trainer = blocklearning.VerticalTrainer(contract, model, x_train, datastore, logger=log)

  while True:
    try:
      phase = contract.get_round_phase()
      if phase == RoundPhase.WAITING_FOR_UPDATES:
        trainer.forward()
      elif phase == RoundPhase.WAITING_FOR_BACKPROPAGATION:
        trainer.backward()
    except web3.exceptions.ContractLogicError as err:
      print(err, flush=True)
    except requests.exceptions.ReadTimeout as err:
      print(err, flush=True)

    time.sleep(0.5)

main()
