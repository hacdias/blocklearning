const Vertical = artifacts.require("Vertical");
const bootstrap = require('../contracts.json');

module.exports = function (deployer) {
  deployer.deploy(Vertical, bootstrap.model, bootstrap.bottomModel, bootstrap.weights);
};
