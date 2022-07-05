import web3
import time
import click
import requests
import blocklearning
import blocklearning.scorers as scorers
import blocklearning.aggregators as aggregators
import blocklearning.model_loaders as model_loaders
import blocklearning.weights_loaders as weights_loaders
import blocklearning.utilities as utilities
from blocklearning.contract import RoundPhase

@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS API provider')
@click.option('--abi', default='./build/contracts/NoScoring.json', help='contract abi file')
@click.option('--account', help='ethereum account to use for this computing server', required=True)
@click.option('--passphrase', help='passphrase to unlock account', required=True)
@click.option('--contract', help='contract address', required=True)
@click.option('--log', help='logging file', required=True)
@click.option('--val', help='validation data .npz file', required=True)
@click.option('--scoring', default=None, help='scoring method')
def main(provider, ipfs, abi, account, passphrase, contract, log, val, scoring):
  log = utilities.setup_logger(log, "server")
  contract = blocklearning.Contract(log, provider, abi, account, passphrase, contract)
  weights_loader = weights_loaders.IpfsWeightsLoader(ipfs)
  model_loader = model_loaders.IpfsModelLoader(contract, weights_loader, ipfs_api=ipfs)
  model = model_loader.load()

  aggregator = None
  if scoring == 'marginal-gain':
    aggregator = aggregators.FedAvgMeansAggregator(model.count, weights_loader)
  elif scoring == 'multi-krum':
    aggregator = aggregators.MultiKrumAggregator(model.count, weights_loader)
  elif scoring == 'blockflow':
    aggregator = aggregators.BlockFlowAggregator(model.count, weights_loader)
  elif scoring == 'data-validity':
    aggregator = aggregators.DataValidityAggregator(model.count, weights_loader)
  else:
    aggregator = aggregators.FedAvgAggregator(model.count, weights_loader)

  aggregator = blocklearning.Aggregator(contract, weights_loader, model, aggregator, with_scores=scoring!='none', logger=log)

  scorer = None
  if scoring == 'multi-krum':
    scorer = scorers.MultiKrumScorer(weights_loader)
  elif scoring == 'data-validity':
    scorer = scorers.DataValidityScorer(log, contract, model, weights_loader, val)
  if scorer is not None:
    scorer = blocklearning.Scorer(contract, scorer=scorer, logger=log)

  while True:
    try:
      phase = contract.get_round_phase()
      if phase == RoundPhase.WAITING_FOR_AGGREGATIONS:
        aggregator.aggregate()
      elif phase == RoundPhase.WAITING_FOR_SCORINGS and scorer is not None:
        scorer.score()
    except web3.exceptions.ContractLogicError as err:
      print(err, flush=True)
    except requests.exceptions.ReadTimeout as err:
      print(err, flush=True)

    time.sleep(0.5)

main()
