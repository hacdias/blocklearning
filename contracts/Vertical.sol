// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract Vertical is Base {
  uint public currentAggregator;

  mapping(uint => uint) public backpropagationsCount;                       // Round => Confirmed Backpropagations
  mapping(uint => mapping(address => bool)) backpropagationsConfirmed;      // Round => Address => Bool
  mapping(uint => mapping(address => mapping(address => string))) grads;    // Round => Trainer => Aggregator => String

  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForAggregations
  ) { }

  function startRound(address[] memory roundTrainers, address[] memory roundAggregators) public override {
    require(false, "VERTICAL");
  }

  function startVerticalRound() public {
    require(msg.sender == owner, "NOWN");
    require(roundPhase == RoundPhase.Stopped, "NS");
    require(aggregators.length > 0 && trainers.length > 0, "NO_REGISTRATIONS");

    round++;
    currentAggregator = (currentAggregator + 1) % aggregators.length;
    selectedTrainers[round] = trainers;
    selectedAggregators[round] = [aggregators[currentAggregator]];
    roundPhase = RoundPhase.WaitingForSubmissions;
  }

  function submitAggregation(string memory aweights) public override {
    require(false, "VERTICAL");
  }

  function submitAggregationWithGradients(string memory aweights, address[] memory gradTrainers, string[] memory roundGrads) public {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(aggregationsSubmitted[round][msg.sender] == false, "AS");
    require(gradTrainers.length == roundGrads.length, "NES");
    require(isSelectedAggregator() == true, "CSNS");

    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      require(isInAddressArray(gradTrainers, selectedTrainers[round][i]), "SM");
    }

    aggregationsSubmitted[round][msg.sender] = true;
    aggregationsCount[round]++;

    aggregationsResults[round].push(aweights);
    aggregationsResultsCount[round][aweights]++;

    for (uint i = 0; i < gradTrainers.length; i++) {
      grads[round][gradTrainers[i]][msg.sender] = roundGrads[i];
    }

    if (aggregationsCount[round] == selectedAggregators[round].length) {
      roundPhase = RoundPhase.WaitingForBackpropagation;
    }
  }

  function confirmBackpropagation() public {
    require(roundPhase == RoundPhase.WaitingForBackpropagation, "NWFS");
    require(backpropagationsConfirmed[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    backpropagationsConfirmed[round][msg.sender] = true;
    backpropagationsCount[round]++;

    if (backpropagationsCount[round] == selectedTrainers[round].length) {
      roundPhase = RoundPhase.WaitingForTermination;
    }
  }
}
