// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract NoScoring is Base {
  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForAggregations
  ) { }
}
