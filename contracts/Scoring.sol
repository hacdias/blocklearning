// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract Score is Base {
  // Registration Details
  address[]                scorers;
  mapping(address => bool) registeredScorers;

  // Round Details
  mapping(uint => address[]) selectedScorers; // Round => Scorers for the round

  // Score Details
  mapping(uint => uint) scoresCount;                                    // Round => Submited Scores
  mapping(uint => mapping(address => bool)) scoresSubmitted;            // Round => Scorer => Bool
  mapping(uint => mapping(address => mapping(address => int))) public scores;  // Round => Trainer => Scorer => Uint

  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForScores
  ) { }

  function registerScorer() public {
    if (registeredScorers[msg.sender] == false) {
      scorers.push(msg.sender);
      registeredScorers[msg.sender] = true;
    }
  }

  function getScorers() public view returns (address[] memory) {
    return scorers;
  }

  function isSelectedScorer() internal view returns (bool) {
    return isInAddressArray(selectedScorers[round], msg.sender);
  }

  function startRound(address[] memory roundTrainers, address[] memory roundAggregators, address[] memory roundScorers) public {
    require(msg.sender == owner, "NOWN");
    require(roundPhase == RoundPhase.Stopped, "NS");
    require(roundTrainers.length > 0, "TR");
    require(roundAggregators.length > 0, "VR");
    require(roundScorers.length > 0, "VS");
    require(aggregators.length > 0 && trainers.length > 0 && scorers.length > 0, "NO_REGISTRATIONS");

    round++;
    selectedTrainers[round] = roundTrainers;
    selectedAggregators[round] = roundAggregators;
    selectedScorers[round] = roundScorers;
    roundPhase = RoundPhase.WaitingForUpdates;
  }

  function getUpdatesForScore() public view returns (uint, address[] memory, Update[] memory) {
    require(roundPhase == RoundPhase.WaitingForScores, "NWFS");
    require(isSelectedScorer(), "CSNS");

    Update[] memory roundUpdates = new Update[](selectedTrainers[round].length);
    address[] memory roundTrainers = new address[](selectedTrainers[round].length);

    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      address trainer = selectedTrainers[round][i];
      roundTrainers[i] = trainer;
      roundUpdates[i] = submissions[round][trainer];
    }

    return (round, roundTrainers, roundUpdates);
  }

  function submitScores(address[] memory scoreTrainers, int[] memory roundScores) public {
    require(roundPhase == RoundPhase.WaitingForScores, "NWFS");
    require(isSelectedScorer(), "CSNS");
    require(scoreTrainers.length == roundScores.length, "NES");
    require(scoresSubmitted[round][msg.sender] == false, "AS");

    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      require(isInAddressArray(scoreTrainers, selectedTrainers[round][i]), "SM");
    }

    scoresSubmitted[round][msg.sender] = true;
    scoresCount[round]++;

    for (uint i = 0; i < scoreTrainers.length; i++) {
      scores[round][scoreTrainers[i]][msg.sender] = roundScores[i];
    }

    if (scoresCount[round] == selectedScorers[round].length) {
      roundPhase = RoundPhase.WaitingForAggregations;
    }
  }

  function getScores() public view returns (address[] memory, address[] memory, int[][] memory) {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(isSelectedAggregator(), "CSNS");

    address[] memory roundScorers = selectedScorers[round];
    address[] memory roundTrainers = selectedTrainers[round];
    int[][] memory roundScores = new int[][](selectedTrainers[round].length);

    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      roundScores[i] = new int[](selectedScorers[round].length);

      for (uint j = 0; j < selectedScorers[round].length; j++) {
        roundScores[i][j] = scores[round][roundTrainers[i]][roundScorers[j]];
      }
    }

    return (roundTrainers, roundScorers, roundScores);
  }
}
