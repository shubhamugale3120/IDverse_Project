# 🚀 Contract Deployment Guide

## Prerequisites

1. **Node.js and npm installed**
2. **Test wallet with testnet tokens** (get from faucet)
3. **RPC URL** (from Alchemy, Infura, or Polygon)

## Step 1: Install Dependencies

```bash
cd frontend/ID-Verse/contracts
npm install
```

## Step 2: Create `.env` file in contracts folder (optional)

Create `frontend/ID-Verse/contracts/.env`:

```env
BLOCKCHAIN_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_API_KEY
BLOCKCHAIN_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_WITHOUT_ANGLE_BRACKETS
```

**⚠️ IMPORTANT:**
- Remove `0x<` and `>` from your private key - it should be just `0x...`
- Private key should start with `0x` followed by 64 hex characters
- Example: `0x1234567890abcdef...` (64 chars after 0x)

## Step 3: Deploy Contracts

### For Polygon Amoy Testnet:
```bash
npx hardhat run scripts/deploy.js --network amoy
```

### For Mumbai Testnet:
```bash
npx hardhat run scripts/deploy.js --network mumbai
```

### For Local Hardhat Network:
```bash
# Terminal 1: Start local node
npx hardhat node

# Terminal 2: Deploy
npx hardhat run scripts/deploy.js --network localhost
```

## Step 4: Get Contract Addresses

After deployment, you'll see:
- ✅ Contract addresses printed in console
- 📝 Addresses saved to `deployed_addresses.json`

**Copy the `CredentialRegistry` address** - this is what you need for `REGISTRY_CONTRACT_ADDRESS` in your main `.env` file.

## Step 5: Add to Main Project `.env`

In your project root (`IDverse_Project/.env`), add:

```env
REGISTRY_CONTRACT_ADDRESS=0x... (from deployment output)
ISSUER_REGISTRY_ADDRESS=0x... (optional)
BENEFIT_LEDGER_ADDRESS=0x... (optional)
```

## Troubleshooting

### Error: "insufficient funds"
- Get testnet tokens from faucet:
  - Polygon Amoy: https://faucet.polygon.technology/
  - Mumbai: https://mumbaifaucet.com/

### Error: "nonce too high"
- Clear your wallet nonce or wait a moment

### Error: "network name not found"
- Check `hardhat.config.js` has the network defined
- Verify network name matches (e.g., `amoy`, `mumbai`, `localhost`)

### Error: "invalid private key"
- Ensure private key starts with `0x` and has 64 hex characters
- No angle brackets `<>` in the key
- Remove any spaces or newlines

## Example Output

```
Deploying contracts with account: 0x1234...
Account balance: 1000000000000000000

1. Deploying IssuerRegistry...
✅ IssuerRegistry deployed to: 0xABC...

2. Deploying CredentialRegistry...
✅ CredentialRegistry deployed to: 0xDEF...  ← COPY THIS!

3. Deploying BenefitLedger...
✅ BenefitLedger deployed to: 0xGHI...

📝 Contract addresses saved to: deployed_addresses.json

🎉 DEPLOYMENT COMPLETE!
============================================================
📋 Add these to your .env file:
REGISTRY_CONTRACT_ADDRESS=0xDEF...
============================================================
```


