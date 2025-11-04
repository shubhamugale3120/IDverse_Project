require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {
      chainId: 1337
    },
    // Polygon Amoy Testnet (recommended)
    amoy: {
      url: process.env.BLOCKCHAIN_RPC_URL || "https://polygon-amoy.g.alchemy.com/v2/33qWagnvaRrQEdneC8XVJ",
      // Private keys MUST be strings (with quotes)
      accounts: process.env.BLOCKCHAIN_PRIVATE_KEY 
        ? [process.env.BLOCKCHAIN_PRIVATE_KEY] 
        : ["0x9e38eaa70f288fceb4f05d4799ca43885ba1fc0afa6842a99f79a0d96e4513b1"],
      chainId: 80002
    },
    // Mumbai Testnet (alternative)
    mumbai: {
      url: process.env.BLOCKCHAIN_RPC_URL || "",
      accounts: process.env.BLOCKCHAIN_PRIVATE_KEY 
        ? [process.env.BLOCKCHAIN_PRIVATE_KEY] 
        : ["0x9e38eaa70f288fceb4f05d4799ca43885ba1fc0afa6842a99f79a0d96e4513b1"],
      chainId: 80001
    },
    // Local Hardhat network
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337
    }
  }
};
