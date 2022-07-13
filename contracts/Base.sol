// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

abstract contract Base {
   struct Update {
    uint trainingAccuracy;
    uint testingAccuracy;
    uint trainingDataPoints;
    string weights;
  }

  enum RoundPhase {
    Stopped,
    WaitingForUpdates,
    WaitingForScores,
    WaitingForAggregations,
    WaitingForTermination,
    WaitingForBackpropagation
  }

  // Initialization Details
  address public owner;
  string  public model; // IPFS CID for model encoded as h5.
  RoundPhase afterUpdate;

  // Registration Details
  address[]                 aggregators;
  mapping(address => bool)  registeredAggregators;
  address[]                 trainers;
  mapping(address => bool)  registeredTrainers;

  // Round Details
  uint                        public round = 0;
  RoundPhase                  public roundPhase = RoundPhase.Stopped;
  mapping(uint => string)     public weights;                   // Round => Weights CID
  mapping(uint => address[])  selectedTrainers;          // Round => Trainers for the round
  mapping(uint => address[])  selectedAggregators;       // Round => Aggregators for the round

  // Updates Details
  mapping(uint => uint) submissionsCount;                      // Round => Submited Updates
  mapping(uint => mapping(address => bool)) submissionsSubmitted;     // Round => Address => Bool
  mapping(uint => mapping(address => Update)) public submissions; // Round => Address => Update

  // Aggregations Details
  mapping(uint => uint)                     aggregationsCount;        // Round => Submited Aggregations
  mapping(uint => mapping(address => bool)) aggregationsSubmitted;    // Round => Address => Bool
  mapping(uint => string[])                 aggregationsResults;      // Round => []CID
  mapping(uint => mapping(string => uint))  aggregationsResultsCount; // Round => CID => Count

  constructor(string memory _model, string memory _weights, RoundPhase _afterUpdate) {
    owner = msg.sender;
    model = _model;
    weights[0] = _weights;
    afterUpdate = _afterUpdate;
  }

  function registerAggregator() public {
    if (registeredAggregators[msg.sender] == false) {
      aggregators.push(msg.sender);
      registeredAggregators[msg.sender] = true;
    }
  }

  function registerTrainer() public {
    if (registeredTrainers[msg.sender] == false) {
      trainers.push(msg.sender);
      registeredTrainers[msg.sender] = true;
    }
  }

  function getTrainers() public view returns (address[] memory) {
    return trainers;
  }

  function getAggregators() public view returns (address[] memory) {
    return aggregators;
  }

  function isInAddressArray(address[] memory arr, address look) internal pure returns (bool) {
    bool found = false;
    for (uint i = 0; i < arr.length; i++) {
      if (arr[i] == look) {
        found = true;
        break;
      }
    }
    return found;
  }

  function isSelectedAggregator() internal view returns (bool) {
    return isInAddressArray(selectedAggregators[round], msg.sender);
  }

  function isSelectedTrainer() internal view returns (bool) {
    return isInAddressArray(selectedTrainers[round], msg.sender);
  }

  function getRoundForTraining() public view virtual returns (uint, string memory) {
    require(roundPhase == RoundPhase.WaitingForUpdates, "NWFS");
    require(isSelectedTrainer(), "TNP");
    return (round, weights[round - 1]);
  }

  function submitUpdate(Update memory submission) public virtual {
    require(roundPhase == RoundPhase.WaitingForUpdates, "NWFS");
    require(submissionsSubmitted[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    submissions[round][msg.sender] = submission;
    submissionsSubmitted[round][msg.sender] = true;
    submissionsCount[round]++;

    if (submissionsCount[round] == selectedTrainers[round].length) {
      roundPhase = afterUpdate;
    }
  }

  function getUpdatesForAggregation() public view returns (uint, address[] memory, Update[] memory) {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(isSelectedAggregator() == true, "CSNS");

    Update[] memory roundUpdates = new Update[](selectedTrainers[round].length);
    address[] memory roundTrainers = new address[](selectedTrainers[round].length);
    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      address trainer = selectedTrainers[round][i];
      roundTrainers[i] = trainer;
      roundUpdates[i] = submissions[round][trainer];
    }
    return (round, roundTrainers, roundUpdates);
  }

  function _submitAggregation(string memory aweights) internal virtual {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(aggregationsSubmitted[round][msg.sender] == false, "AS");
    require(isSelectedAggregator() == true, "CSNS");

    aggregationsSubmitted[round][msg.sender] = true;
    aggregationsCount[round]++;

    aggregationsResults[round].push(aweights);
    aggregationsResultsCount[round][aweights]++;

    if (aggregationsCount[round] == selectedAggregators[round].length) {
      roundPhase = RoundPhase.WaitingForTermination;
    }
  }


  function submitAggregation(string memory _weights) public virtual {
    _submitAggregation(_weights);
  }

  function terminateRound() public {
    require(roundPhase == RoundPhase.WaitingForTermination, "NWFT");

    uint count;
    uint minQuorum = selectedAggregators[round].length / 2 + 1;
    string memory roundWeights;

    for (uint i = 0; i < aggregationsResults[round].length; i++) {
      string memory w = aggregationsResults[round][i];
      uint c = aggregationsResultsCount[round][w];
      if (c >= minQuorum) {
        if (c > count) {
          roundWeights = w;
          count = c;
        }
      }
    }

    require(count != 0, "CNT");
    weights[round] = roundWeights;
    roundPhase = RoundPhase.Stopped;
  }
}
