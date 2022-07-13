const NoScore = artifacts.require("NoScore");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(NoScore, bootstrap.model, bootstrap.weights);
};
