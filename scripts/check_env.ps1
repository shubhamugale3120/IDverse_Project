$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projRoot = Split-Path -Parent $scriptDir

Write-Host "Project root: $projRoot`n"

$envFile = Join-Path $projRoot ".env"
if (-Not (Test-Path $envFile)) {
    Write-Host "ERROR: .env not found at project root ($envFile)." -ForegroundColor Red
    exit 1
}

# load .env (simple parser)
$envMap = @{}
Get-Content $envFile | ForEach-Object {
    $_ = $_.Trim()
    if (-not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith('#')) {
        $parts = $_ -split '=',2
        if ($parts.Length -eq 2) {
            $k = $parts[0].Trim()
            $v = $parts[1].Trim()
            $envMap[$k] = $v
        }
    }
}

function GetVal($k, $default="") {
    if ($envMap.ContainsKey($k) -and -not [string]::IsNullOrWhiteSpace($envMap[$k])) { return $envMap[$k] }
    $ev = [System.Environment]::GetEnvironmentVariable($k)
    if ($ev -and -not [string]::IsNullOrWhiteSpace($ev)) { return $ev }
    return $default
}

$errors = @()

# Basic checks
$signMode = GetVal "SIGN_MODE"
if (-not $signMode) { $errors += "SIGN_MODE is not set in .env (recommended: ed25519)." }

$ipfsMode = GetVal "IPFS_MODE" "mock"
if (-not $ipfsMode) { $errors += "IPFS_MODE not set; defaulting to 'mock' — set to 'web3' to use Web3.Storage." }

# Web3 storage token if needed
if ($ipfsMode.ToLower() -in @("web3","web3.storage","w3")) {
    $token = GetVal "WEB3_STORAGE_TOKEN"
    if (-not $token) { $errors += "WEB3_STORAGE_TOKEN missing but IPFS_MODE=$ipfsMode. Add token to .env (no inline comments)." }
    elseif ($token.Length -lt 20) { $errors += "WEB3_STORAGE_TOKEN looks too short — verify token." }
}

# Chain checks
$chainMode = GetVal "CHAIN_MODE" "mock"
if ($chainMode.ToLower() -eq "real") {
    $rpc = GetVal "BLOCKCHAIN_RPC_URL"
    if (-not $rpc) { $errors += "BLOCKCHAIN_RPC_URL missing for CHAIN_MODE=real." }
    $pk = GetVal "BLOCKCHAIN_PRIVATE_KEY"
    if (-not $pk) { $errors += "BLOCKCHAIN_PRIVATE_KEY missing for CHAIN_MODE=real." }
    elseif (-not $pk.StartsWith("0x")) { $errors += "BLOCKCHAIN_PRIVATE_KEY should start with 0x." }

    if ($rpc) {
        Write-Host "Checking BLOCKCHAIN_RPC_URL connectivity ($rpc)..."
        try {
            $body = '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'
            $resp = Invoke-RestMethod -Method Post -Uri $rpc -Body $body -ContentType 'application/json' -TimeoutSec 5
            if ($resp -ne $null) { Write-Host "RPC reachable." -ForegroundColor Green }
        } catch {
            $errors += "Cannot reach BLOCKCHAIN_RPC_URL ($rpc). Start local node or correct URL."
        }
    }
}

# Registry address (if required)
$regAddr = GetVal "REGISTRY_CONTRACT_ADDRESS"
if ($chainMode.ToLower() -eq "real" -and -not $regAddr) { $errors += "REGISTRY_CONTRACT_ADDRESS missing for CHAIN_MODE=real." }

# Issuer keys dir
$keysDir = GetVal "ISSUER_KEYS_DIR" (Join-Path $projRoot "instance\issuer_keys")
if (-not (Test-Path $keysDir)) {
    Write-Host "ISSUER_KEYS_DIR not found. Attempting to create: $keysDir"
    try {
        New-Item -ItemType Directory -Path $keysDir -Force | Out-Null
    } catch {
        $errors += "Failed to create ISSUER_KEYS_DIR ($keysDir). Ensure write permissions."
    }
}
# test write permission
$tmpFile = Join-Path $keysDir ("._env_check_" + [Guid]::NewGuid().ToString() + ".tmp")
try {
    Set-Content -Path $tmpFile -Value "test" -Force
    Remove-Item $tmpFile -Force
    Write-Host "ISSUER_KEYS_DIR writable: $keysDir" -ForegroundColor Green
} catch {
    $errors += "ISSUER_KEYS_DIR ($keysDir) is not writable. Fix permissions or set ISSUER_KEYS_DIR to writable path."
}

# Backend venv
$venvAct = Join-Path $projRoot "backend\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvAct)) {
    Write-Host "Warning: backend venv not found at backend\.venv. Create venv and install requirements." -ForegroundColor Yellow
} else {
    Write-Host "Found backend venv." -ForegroundColor Green
}

# Frontend package.json check
$frontendPkg = Join-Path $projRoot "frontend\ID-Verse\frontend\package.json"
if (-not (Test-Path $frontendPkg)) {
    Write-Host "Warning: frontend package.json not found at frontend\ID-Verse\frontend. Frontend may not run." -ForegroundColor Yellow
} else {
    Write-Host "Found frontend package.json." -ForegroundColor Green
}

if ($ipfsMode.ToLower() -eq "mock") {
    Write-Host "IPFS_MODE=mock — good for demos. To test real uploads set IPFS_MODE=web3 and provide WEB3_STORAGE_TOKEN." -ForegroundColor Cyan
}

if ($errors.Count -gt 0) {
    Write-Host "`nENV CHECK FAILED with the following issues:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    Write-Host "`nFix the above and re-run: .\scripts\check_env.ps1" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`nENV CHECK PASSED: critical variables and paths look OK." -ForegroundColor Green
    exit 0
}