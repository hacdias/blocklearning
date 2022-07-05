const accounts = require('../thesis/testbed/ethereum/datadir/accounts.json')

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      from: Object.keys(accounts.owner)[0]
    }
  },
  compilers: {
    solc: {
      version: "0.8.11"
    }
  },
};
