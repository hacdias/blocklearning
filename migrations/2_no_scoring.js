const NoScoring = artifacts.require("NoScoring");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(NoScoring, bootstrap.model, bootstrap.weights);
};
