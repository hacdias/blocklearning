const FirstComeFirstServed = artifacts.require("FirstComeFirstServed");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(FirstComeFirstServed, bootstrap.model, bootstrap.weights);
};
