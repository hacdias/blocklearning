const Scoring = artifacts.require("Scoring");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(Scoring, bootstrap.model, bootstrap.weights);
};
