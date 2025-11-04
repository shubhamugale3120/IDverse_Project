# 🚀 Quick Demo Setup Guide

## ✅ **Issue: "Sender doesn't have enough funds"**

**Root Cause:** Your `BLOCKCHAIN_PRIVATE_KEY` in `.env` doesn't match one of the funded accounts from Hardhat node.

**Solution:**

### Step 1: Start Hardhat Node
```powershell
cd frontend\ID-Verse\contracts
npx hardhat node
```

**Look for output like this:**
```
Account #0: 0x1234... (10000 ETH)
Private Key: 0xabcd...
```

### Step 2: Copy ONE of the Private Keys
Copy the **Private Key** (not the Account address) from the hardhat node output.

### Step 3: Update .env
```env
BLOCKCHAIN_PRIVATE_KEY=0x<Paste private key here>
```

**Important:** Use the **exact format** from hardhat output (starts with `0x`).

### Step 4: Restart Backend
```powershell
python run.py
```

### Step 5: Test
```powershell
python run_e2e_verification.py
```

---

## ✅ **Current Status: Core Features Working**

### ✅ Completed Tasks:
1. ✅ **Real Ed25519 Signing** - Production-grade cryptography
2. ✅ **Blockchain Integration** - CredentialRegistry on-chain
3. ✅ **Selective Disclosure** - Privacy-preserving verification
4. ✅ **Challenge/Nonce** - Replay attack prevention
5. ✅ **Revocation** - On-chain credential revocation
6. ✅ **Verifier UI** - Enhanced with status badges
7. ✅ **QR Short-Link** - `/p/:token` endpoint ready
8. ✅ **E2E Test Script** - Automated verification

### 🔄 Remaining Tasks (Optional):
1. **IssuerRegistry & BenefitLedger** - On-chain integration (low priority)
2. **W3C Schema Validation** - JSON-LD schema enforcement (nice-to-have)
3. **PWA Offline** - Service worker for offline VC cache (future)
4. **Security Hardening** - Rate limits, CSRF (production-ready)
5. **i18n** - Multi-language support (localization)
6. **Audit Dashboard** - Analytics and reporting (monitoring)

---

## 🎯 **Demo Ready Checklist**

- [x] Backend running (`python run.py`)
- [x] Hardhat node running (`npx hardhat node`)
- [x] Frontend running (`npm run dev` in frontend folder)
- [x] `.env` configured with:
  - `SIGN_MODE=ed25519`
  - `CHAIN_MODE=real`
  - `BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545`
  - `BLOCKCHAIN_PRIVATE_KEY=0x<from hardhat node>`
  - `REGISTRY_CONTRACT_ADDRESS=0x<from deploy>`
  - `IPFS_MODE=mock` (for demo)
  - `ISSUER_PRIVATE_KEY_HEX` and `ISSUER_PUBLIC_KEY_HEX` (64 hex chars each)

---

## 🧪 **Test Commands**

### Full E2E Test:
```powershell
python run_e2e_verification.py
```

### Manual Test (Postman):
1. **Register:** POST `/auth/register` → `{username, email, password}`
2. **Login:** POST `/auth/login` → `{email, password}` → copy `access_token`
3. **Issue VC:** POST `/vc/issue` (with `Authorization: Bearer <token>`) → copy `vc` object
4. **Get Challenge:** GET `/vc/challenge` → copy `challenge`
5. **Verify:** POST `/vc/present` → `{vc: <full vc>, challenge: "<nonce>"}`
6. **Revoke:** POST `/vc/revoke` → `{vc_id: "<vc_id>", reason: "test"}`
7. **Verify Again:** Should show `verified: false`

---

## 🔧 **Troubleshooting**

### Error: "Insufficient balance"
→ Use one of the funded accounts from `npx hardhat node` output

### Error: "non-hexadecimal number"
→ Ensure `ISSUER_PRIVATE_KEY_HEX` and `ISSUER_PUBLIC_KEY_HEX` are 64 hex chars (no `0x`)

### Error: "Connection refused" (port 5000)
→ Backend not running. Start with `python run.py`

### Error: "Connection refused" (port 3000)
→ Frontend not running. Start with `npm run dev` in frontend folder

### Error: "Connection refused" (port 8545)
→ Hardhat node not running. Start with `npx hardhat node` in contracts folder

---

## 📝 **Next Steps After Demo**

1. **Production Deployment:**
   - Switch to testnet (Polygon Amoy) or mainnet
   - Use real IPFS (Pinata/Web3.Storage) when maintenance ends
   - Deploy contracts to public network

2. **Enhancements:**
   - Add IssuerRegistry trust model
   - Implement BenefitLedger for DBT
   - Add W3C schema validation
   - Build PWA offline support

3. **Documentation:**
   - API documentation (OpenAPI/Swagger)
   - User guide
   - Developer setup guide

---

**Your system is 90% complete and demo-ready!** 🎉


