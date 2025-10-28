async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const IssuerRegistry = await ethers.getContractFactory("IssuerRegistry");
  const issuer = await IssuerRegistry.deploy();
  await issuer.waitForDeployment();
  console.log("IssuerRegistry:", await issuer.getAddress());

  const CredentialRegistry = await ethers.getContractFactory("CredentialRegistry");
  const cred = await CredentialRegistry.deploy();
  await cred.waitForDeployment();
  console.log("CredentialRegistry:", await cred.getAddress());

  const BenefitLedger = await ethers.getContractFactory("BenefitLedger");
  const ledger = await BenefitLedger.deploy();
  await ledger.waitForDeployment();
  console.log("BenefitLedger:", await ledger.getAddress());
}

main().catch((err) => { console.error(err); process.exitCode = 1; });