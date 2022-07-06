// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

abstract contract Base {
   struct Submission {
    uint trainingAccuracy;
    uint testingAccuracy;
    uint trainingDataPoints;
    string weights;
  }

  enum RoundPhase {
    Stopped,
    WaitingForSubmissions,
    WaitingForScorings,
    WaitingForAggregations,
    WaitingForTermination,
    WaitingForBackpropagation
  }

  // Initialization Details
  address public owner;
  string  public model; // IPFS CID for model encoded as h5.
  RoundPhase afterSubmission;

  // Registration Details
  address[]                 public aggregators;
  mapping(address => bool)  public registeredAggregators;
  address[]                 public trainers;
  mapping(address => bool)  public registeredTrainers;

  // Round Details
  uint                        public round = 0;
  RoundPhase                  public roundPhase = RoundPhase.Stopped;
  mapping(uint => string)     public weights;                   // Round => Weights CID
  mapping(uint => address[])  public selectedTrainers;          // Round => Trainers for the round
  mapping(uint => address[])  public selectedAggregators;       // Round => Aggregators for the round

  // Submissions Details
  mapping(uint => uint) public submissionsCount;                      // Round => Submited Submissions
  mapping(uint => mapping(address => bool)) submissionsSubmitted;     // Round => Address => Bool
  mapping(uint => mapping(address => Submission)) public submissions; // Round => Address => Submission

  // Aggregations Details
  mapping(uint => uint) aggregationsCount;                           // Round => Submited Aggregations
  mapping(uint => mapping(address => bool)) aggregationsSubmitted;   // Round => Address => Bool
  mapping(uint => string[]) aggregationsResults;                     // Round => []CID
  mapping(uint => mapping(string => uint)) aggregationsResultsCount; // Round => CID => Count

  constructor(string memory _model, string memory _weights, RoundPhase _afterSubmission) {
    owner = msg.sender;
    model = _model;
    weights[0] = _weights;
    afterSubmission = _afterSubmission;
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
    require(roundPhase == RoundPhase.WaitingForSubmissions, "NWFS");
    require(isSelectedTrainer(), "TNP");
    return (round, weights[round - 1]);
  }

  function submitSubmission(Submission memory submission) public virtual {
    require(roundPhase == RoundPhase.WaitingForSubmissions, "NWFS");
    require(submissionsSubmitted[round][msg.sender] == false, "AS");
    require(isSelectedTrainer(), "TNP");

    submissions[round][msg.sender] = submission;
    submissionsSubmitted[round][msg.sender] = true;
    submissionsCount[round]++;

    if (submissionsCount[round] == selectedTrainers[round].length) {
      roundPhase = afterSubmission;
    }
  }

  function getSubmissionsForAggregation() public view returns (uint, address[] memory, Submission[] memory) {
    require(roundPhase == RoundPhase.WaitingForAggregations, "NWFA");
    require(isSelectedAggregator() == true, "CSNS");

    Submission[] memory roundSubmissions = new Submission[](selectedTrainers[round].length);
    address[] memory roundTrainers = new address[](selectedTrainers[round].length);
    for (uint i = 0; i < selectedTrainers[round].length; i++) {
      address trainer = selectedTrainers[round][i];
      roundTrainers[i] = trainer;
      roundSubmissions[i] = submissions[round][trainer];
    }
    return (round, roundTrainers, roundSubmissions);
  }

  function submitAggregation(string memory aweights) public virtual {
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
