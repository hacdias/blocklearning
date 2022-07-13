// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract NoScore is Base {
  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForAggregations
  ) { }

  function startRound(address[] memory roundTrainers, address[] memory roundAggregators) public {
    require(msg.sender == owner, "NOWN");
    require(roundPhase == RoundPhase.Stopped, "NS");
    require(roundTrainers.length > 0, "TR");
    require(roundAggregators.length > 0, "VR");
    require(aggregators.length > 0 && trainers.length > 0, "NO_REGISTRATIONS");

    round++;
    selectedTrainers[round] = roundTrainers;
    selectedAggregators[round] = roundAggregators;
    roundPhase = RoundPhase.WaitingForUpdates;
  }
}
