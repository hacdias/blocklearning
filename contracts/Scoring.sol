// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './Base.sol';

contract Scoring is Base {
  // Registration Details
  address[]                 public scorers;
  mapping(address => bool)  public registeredScorers;

  // Round Details
  mapping(uint => address[])  public selectedScorers; // Round => Scorers for the round

  // Scoring Details
  mapping(uint => uint) scoresCount;                                    // Round => Submited Scores
  mapping(uint => mapping(address => bool)) scoresSubmitted;            // Round => Scorer => Bool
  mapping(uint => mapping(address => mapping(address => int))) scores;  // Round => Trainer => Scorer => Uint

  constructor(string memory _model, string memory _weights) Base(
    _model,
    _weights,
    RoundPhase.WaitingForScorings
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

  function startRoundWithScoring(address[] memory roundTrainers, address[] memory roundAggregators, address[] memory roundScorers) public {
    require(roundScorers.length > 0, "VS");
    require(scorers.length > 0, "NO_REGISTRATIONS_SCORERS");

    selectedScorers[round+1] = roundScorers;
    startRound(roundTrainers, roundAggregators);
  }

  function getSubmissionsForScoring() public view returns (uint, address[] memory, Submission[] memory) {
    require(roundPhase == RoundPhase.WaitingForScorings, "NWFS");
    require(isSelectedScorer(), "CSNS");

    Submission[] memory roundSubmissions = new Submission[](selectedTrainers[round].length);
    address[] memory roundTrainers = new address[](selectedTrainers[round].length);

    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      address trainer = selectedTrainers[round][i];
      roundTrainers[i] = trainer;
      roundSubmissions[i] = submissions[round][trainer];
    }

    return (round, roundTrainers, roundSubmissions);
  }

  function submitScorings(address[] memory scoreTrainers, int[] memory roundScores) public {
    require(roundPhase == RoundPhase.WaitingForScorings, "NWFS");
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

  function getScorings() public view returns (address[] memory, address[] memory, int[][] memory) {
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
