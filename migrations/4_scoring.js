const Score = artifacts.require("Score");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(Score, bootstrap.model, bootstrap.weights);
};
