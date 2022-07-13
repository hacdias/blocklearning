// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract Vertical is Base {
  uint    public currentAggregator;
  string  public bottomModel; // IPFS CID for model encoded as h5.

  mapping(uint => uint) public backpropagationsCount;                       // Round => Confirmed Backpropagations
  mapping(uint => mapping(address => bool)) backpropagationsConfirmed;      // Round => Address => Bool
  mapping(uint => mapping(address => mapping(address => string))) grads;    // Round => Trainer => Aggregator => String

  constructor(string memory _topModel, string memory _bottomModel, string memory _weights) Base(
    _topModel,
    _weights,
    RoundPhase.WaitingForAggregations
  ) {
    bottomModel = _bottomModel;
  }

  function startRound() public {
    require(msg.sender == owner, "NOWN");
    require(roundPhase == RoundPhase.Stopped, "NS");
    require(aggregators.length > 0 && trainers.length > 0, "NO_REGISTRATIONS");

    round++;
    currentAggregator = (currentAggregator + 1) % aggregators.length;
    selectedTrainers[round] = trainers;
    selectedAggregators[round] = [aggregators[currentAggregator]];
    roundPhase = RoundPhase.WaitingForUpdates;
  }

  function submitAggregation(string memory _weights) public pure override {
    revert("Direct Call");
  }

  function submitAggregationWithGradients(string memory aweights, address[] memory gradTrainers, string[] memory roundGrads) public {
    require(gradTrainers.length == roundGrads.length, "NES");
    super._submitAggregation(aweights);

    for (uint i = 0; i < gradTrainers.length; i++) {
      grads[round][gradTrainers[i]][msg.sender] = roundGrads[i];
    }

    if (aggregationsCount[round] == selectedAggregators[round].length) {
      roundPhase = RoundPhase.WaitingForBackpropagation;
    }
  }

  function getGradient() public view returns (string memory) {
    require(roundPhase == RoundPhase.WaitingForBackpropagation, "NWFB");
    require(backpropagationsConfirmed[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    address roundAggregator = aggregators[currentAggregator];
    return grads[round][msg.sender][roundAggregator];
  }

  function confirmBackpropagation() public {
    require(roundPhase == RoundPhase.WaitingForBackpropagation, "NWFB");
    require(backpropagationsConfirmed[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    backpropagationsConfirmed[round][msg.sender] = true;
    backpropagationsCount[round]++;

    if (backpropagationsCount[round] == selectedTrainers[round].length) {
      roundPhase = RoundPhase.WaitingForTermination;
    }
  }
}
