// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract FirstComeFirstServed is Base {
  mapping(uint => uint) public trainersQuorum; // Round => #Trainers for the round

  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForAggregations
  ) {}

  function startRound(uint roundTrainers, address[] memory roundAggregators) public {
    require(msg.sender == owner, "NOWN");
    require(roundPhase == RoundPhase.Stopped, "NS");
    require(roundTrainers > 0, "TR");
    require(roundAggregators.length > 0, "VR");
    require(aggregators.length > 0 && trainers.length > 0, "NO_REGISTRATIONS");

    round++;
    trainersQuorum[round] = roundTrainers;
    selectedAggregators[round] = roundAggregators;
    roundPhase = RoundPhase.WaitingForUpdates;
  }

  function getRoundForTraining() public view override returns (uint, string memory) {
    require(roundPhase == RoundPhase.WaitingForUpdates, "NWFS");
    return (round, weights[round - 1]);
  }

  function submitUpdate(Update memory submission) public override {
    require(updatesCount[round] < trainersQuorum[round], "QR");

    if (!isSelectedTrainer()) {
      selectedTrainers[round].push(msg.sender);
    }

    super.submitUpdate(submission);

    if (updatesCount[round] < trainersQuorum[round]) {
      roundPhase = RoundPhase.WaitingForUpdates;
    } else {
      roundPhase = afterUpdate;
    }
  }
}
