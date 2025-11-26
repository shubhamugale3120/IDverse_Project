# IDVerse — Project summary & runbook

Short overview
- IDVerse = Flask backend + Next.js frontend + Solidity contracts.
- Purpose: issue / present / verify JSON‑LD Verifiable Credentials, record benefits on-chain, IPFS storage.
- Main stacks: Python (Flask, SQLAlchemy, web3.py, pyld/jsonschema, nacl), Node/Next.js, Solidity/Hardhat, IPFS (Web3.Storage / local).

Quick start (Windows)
1. Clone repo; open project root.
2. Backend:
   - Create & activate venv:
     ```
     py -3 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r backend/requirements.txt
     ```
   - Ensure `.env` exists and set:
     ```
     IPFS_MODE=mock|web3|real
     WEB3_STORAGE_TOKEN=...
     BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
     BENEFIT_LEDGER_ADDRESS=0x...
     ```
   - Run:
     ```
     python run.py
     ```
3. Frontend:
   ```
   cd frontend\ID-Verse\frontend
   npm install
   npm run dev
   ```
4. Contracts (local dev with Hardhat):
   ```
   cd frontend\ID-Verse\contracts
   npm init -y
   npm i --save-dev hardhat @nomiclabs/hardhat-ethers ethers
   npx hardhat node
   npx hardhat run --network localhost scripts/deploy.js
   ```
5. Test VC issuance (Postman / curl): POST /vc/issue (JWT required). For dev set IPFS_MODE=mock.

Key files & responsibilities
- run.py — entry point (prints routes).
- backend/__init__.py — Flask app factory, register blueprints.
- backend/model.py — SQLAlchemy models (User, VerifiableCredential, BenefitApplication, TokenBlocklist).
- backend/auth/routes.py — register/login/logout (ensure duplicate checks and rollback on IntegrityError).
- backend/routes/vc.py — VC issue/verify/present endpoints (uses signing + ipfs services).
- backend/services/ipfs_service.py — Mock / ipfshttpclient / Web3.Storage implementations (get_ipfs_service()).
- backend/services/ed25519_signing.py — issuer signing and key persistence.
- backend/services/contract_service.py — web3.py wrappers, read ABI from backend/contracts.
- frontend/ID-Verse/frontend — Next.js app, QR presenter, verifier flows.
- frontend/ID-Verse/contracts — Solidity contracts (BenefitLedger.sol). Save ABIs to backend/contracts after deploy.

Integration overview
- Frontend authenticates → receives JWT → calls protected backend endpoints.
- /vc/issue: backend builds VC, signs (Ed25519), uploads to IPFS, persists DB, optionally call CredentialRegistry.
- /vc/verify: backend fetches VC (IPFS), verifies signature, checks on‑chain revocation/registry, validates schema and nonce.
- Contracts: BenefitLedger.grantBenefit emits events; backend can call contract or subscribe and persist.

Dev tips & common fixes
- If IPFS fails: check WEB3_STORAGE_TOKEN, set IPFS_MODE=mock for local dev.
- Missing npm packages: run npm install in frontend folder.
- Ensure "use client" at top of client components for Next App Router pages using hooks or window APIs.
- Remove inline comments from .env token values.

Next actions I can generate for you:
- startup script to start backend + frontend + hardhat node
- delete_user.py (DB utility)
- sync_events.py (basic BenefitLedger event listener)
