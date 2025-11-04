const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

  // Deploy IssuerRegistry
  console.log("\n1. Deploying IssuerRegistry...");
  const IssuerRegistry = await ethers.getContractFactory("IssuerRegistry");
  const issuer = await IssuerRegistry.deploy();
  await issuer.waitForDeployment();
  const issuerAddress = await issuer.getAddress();
  console.log("✅ IssuerRegistry deployed to:", issuerAddress);

  // Deploy CredentialRegistry
  console.log("\n2. Deploying CredentialRegistry...");
  const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
  const cred = await CredentialRegistry.deploy();
  await cred.waitForDeployment();
  const credAddress = await cred.getAddress();
  console.log("✅ CredentialRegistry deployed to:", credAddress);

  // Deploy BenefitLedger
  console.log("\n3. Deploying BenefitLedger...");
  const BenefitLedger = await ethers.getContractFactory("BenefitLedger");
  const ledger = await BenefitLedger.deploy();
  await ledger.waitForDeployment();
  const ledgerAddress = await ledger.getAddress();
  console.log("✅ BenefitLedger deployed to:", ledgerAddress);

  // Save addresses to file
  const addresses = {
    network: network.name,
    deployer: deployer.address,
    contracts: {
      IssuerRegistry: issuerAddress,
      CredentialRegistry: credAddress,
      BenefitLedger: ledgerAddress
    },
    timestamp: new Date().toISOString()
  };

  const addressesPath = path.join(__dirname, "..", "deployed_addresses.json");
  fs.writeFileSync(addressesPath, JSON.stringify(addresses, null, 2));
  console.log("\n📝 Contract addresses saved to:", addressesPath);

  console.log("\n" + "=".repeat(60));
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("=".repeat(60));
  console.log("\n📋 Add these to your .env file:");
  console.log(`REGISTRY_CONTRACT_ADDRESS=${credAddress}`);
  console.log(`ISSUER_REGISTRY_ADDRESS=${issuerAddress}`);
  console.log(`BENEFIT_LEDGER_ADDRESS=${ledgerAddress}`);
  console.log("\n" + "=".repeat(60));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
