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
  string  public model;     // IPFS CID for model encoded as h5.
  RoundPhase afterUpdate;   // Which phase is executed after WaitingForUpdates.

  // Registration Details
  address[]                 aggregators;
  mapping(address => bool)  registeredAggregators;
  address[]                 trainers;
  mapping(address => bool)  registeredTrainers;

  // Round Details
  uint                        public round = 0;
  RoundPhase                  public roundPhase = RoundPhase.Stopped;
  mapping(uint => string)     public weights;             // Round => Weights ID
  mapping(uint => address[])  public selectedTrainers;    // Round => Trainers for the round
  mapping(uint => address[])  public selectedAggregators; // Round => Aggregators for the round

  // Updates Details
  mapping(uint => uint) updatesCount;                           // Round => Submited Updates
  mapping(uint => mapping(address => bool)) updatesSubmitted;   // Round => Address => Bool
  mapping(uint => mapping(address => Update)) public updates;   // Round => Address => Update

  // Aggregations Details
  mapping(uint => uint)                       aggregationsCount;        // Round => Submited Aggregations
  mapping(uint => mapping(address => bool))   aggregationsSubmitted;    // Round => Address => Bool
  mapping(uint => mapping(address => string)) public aggregations;      // Round => Address => Weights ID
  mapping(uint => mapping(string => uint))    aggregationsResultsCount; // Round => Weights ID => Count

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
    require(updatesSubmitted[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    updates[round][msg.sender] = submission;
    updatesSubmitted[round][msg.sender] = true;
    updatesCount[round]++;

    if (updatesCount[round] == selectedTrainers[round].length) {
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
      roundUpdates[i] = updates[round][trainer];
    }
    return (round, roundTrainers, roundUpdates);
  }

  function _submitAggregation(string memory aggregation) internal virtual {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(aggregationsSubmitted[round][msg.sender] == false, "AS");
    require(isSelectedAggregator() == true, "CSNS");

    aggregations[round][msg.sender] = aggregation;
    aggregationsSubmitted[round][msg.sender] = true;
    aggregationsCount[round]++;
    aggregationsResultsCount[round][aggregation]++;

    if (aggregationsCount[round] == selectedAggregators[round].length) {
      roundPhase = RoundPhase.WaitingForTermination;
    }
  }


  function submitAggregation(string memory _weights) public virtual {
    _submitAggregation(_weights);
  }

  function terminateRound() public {
    require(roundPhase == RoundPhase.WaitingForTermination, "NWFT");

    uint minQuorum = selectedAggregators[round].length * 50 / 100 + 1;
    uint count;
    string memory roundWeights;

    for (uint i = 0; i < selectedAggregators[round].length; i++) {
      address aggregator = selectedAggregators[round][i];
      string memory w = aggregations[round][aggregator];
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
