import dotenv from "dotenv";
import "@nomicfoundation/hardhat-toolbox";

dotenv.config();

export default {
  solidity: "0.8.19",
  networks: {
    hardhat: {},
    mumbai: {
      url: process.env.ALCHEMY_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  }
};