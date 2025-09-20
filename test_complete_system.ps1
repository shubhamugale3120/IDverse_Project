# IDVerse Complete System Test Script
# Tests all endpoints with proper JWT authentication

Write-Host "🧪 IDVerse Complete System Testing" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$baseUrl = "http://localhost:5000"
$jwtToken = ""

# Function to make HTTP requests
function Invoke-ApiRequest {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method $Method -Headers $Headers -Body $Body -ContentType "application/json"
        return $response
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
$health = Invoke-ApiRequest -Method "GET" -Url "$baseUrl/health"
if ($health) {
    Write-Host "✅ Health Check: $($health.status)" -ForegroundColor Green
} else {
    Write-Host "❌ Health Check Failed" -ForegroundColor Red
    exit 1
}

# Test 2: User Registration
Write-Host "`n2. Testing User Registration..." -ForegroundColor Yellow
$registerData = @{
    username = "testuser_$(Get-Date -Format 'yyyyMMddHHmmss')"
    email = "test_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
    password = "password123"
} | ConvertTo-Json

$registerResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/auth/register" -Body $registerData
if ($registerResponse) {
    Write-Host "✅ Registration: $($registerResponse.message)" -ForegroundColor Green
} else {
    Write-Host "❌ Registration Failed" -ForegroundColor Red
}

# Test 3: User Login
Write-Host "`n3. Testing User Login..." -ForegroundColor Yellow
$loginData = @{
    email = ($registerData | ConvertFrom-Json).email
    password = "password123"
} | ConvertTo-Json

$loginResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/auth/login" -Body $loginData
if ($loginResponse -and $loginResponse.access_token) {
    $jwtToken = $loginResponse.access_token
    Write-Host "✅ Login: JWT token received" -ForegroundColor Green
    Write-Host "   User: $($loginResponse.user.username)" -ForegroundColor Cyan
} else {
    Write-Host "❌ Login Failed" -ForegroundColor Red
    exit 1
}

# Set up headers with JWT token
$authHeaders = @{
    "Authorization" = "Bearer $jwtToken"
    "Content-Type" = "application/json"
}

# Test 4: VC Request Issue
Write-Host "`n4. Testing VC Request Issue..." -ForegroundColor Yellow
$vcRequestData = @{
    type = "GovID"
    claims = @{
        name = "Shubham Ugale"
        age = 25
        address = "Mumbai, India"
        aadhaar = "123456789012"
    }
} | ConvertTo-Json

$vcRequestResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/vc/request-issue" -Headers $authHeaders -Body $vcRequestData
if ($vcRequestResponse) {
    Write-Host "✅ VC Request: $($vcRequestResponse.request_id)" -ForegroundColor Green
    $requestId = $vcRequestResponse.request_id
} else {
    Write-Host "❌ VC Request Failed" -ForegroundColor Red
}

# Test 5: VC Issue
Write-Host "`n5. Testing VC Issue..." -ForegroundColor Yellow
$vcIssueData = @{
    request_id = $requestId
} | ConvertTo-Json

$vcIssueResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/vc/issue" -Headers $authHeaders -Body $vcIssueData
if ($vcIssueResponse) {
    Write-Host "✅ VC Issue: $($vcIssueResponse.vc_id)" -ForegroundColor Green
    Write-Host "   CID: $($vcIssueResponse.cid)" -ForegroundColor Cyan
    $vcId = $vcIssueResponse.vc_id
} else {
    Write-Host "❌ VC Issue Failed" -ForegroundColor Red
}

# Test 6: VC Status Check
Write-Host "`n6. Testing VC Status..." -ForegroundColor Yellow
$vcStatusResponse = Invoke-ApiRequest -Method "GET" -Url "$baseUrl/vc/status/$vcId" -Headers $authHeaders
if ($vcStatusResponse) {
    Write-Host "✅ VC Status: $($vcStatusResponse.status)" -ForegroundColor Green
    Write-Host "   Verifiable: $($vcStatusResponse.verifiable)" -ForegroundColor Cyan
} else {
    Write-Host "❌ VC Status Check Failed" -ForegroundColor Red
}

# Test 7: VC Present
Write-Host "`n7. Testing VC Present..." -ForegroundColor Yellow
$vcPresentData = @{
    vc_id = $vcId
    verifier_did = "did:example:verifier"
} | ConvertTo-Json

$vcPresentResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/vc/present" -Headers $authHeaders -Body $vcPresentData
if ($vcPresentResponse) {
    Write-Host "✅ VC Present: $($vcPresentResponse.verified)" -ForegroundColor Green
} else {
    Write-Host "❌ VC Present Failed" -ForegroundColor Red
}

# Test 8: Benefits Apply
Write-Host "`n8. Testing Benefits Apply..." -ForegroundColor Yellow
$benefitApplyData = @{
    scheme_id = "scheme-001"
    scheme_name = "PM Kisan Yojana"
    required_credentials = @("GovID")
    application_data = @{
        land_holding = "2 acres"
        bank_account = "1234567890"
        farmer_id = "FARM123456"
    }
} | ConvertTo-Json

$benefitApplyResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/benefits/apply" -Headers $authHeaders -Body $benefitApplyData
if ($benefitApplyResponse) {
    Write-Host "✅ Benefits Apply: $($benefitApplyResponse.application_id)" -ForegroundColor Green
    $applicationId = $benefitApplyResponse.application_id
} else {
    Write-Host "❌ Benefits Apply Failed" -ForegroundColor Red
}

# Test 9: Benefits Approve
Write-Host "`n9. Testing Benefits Approve..." -ForegroundColor Yellow
$benefitApproveData = @{
    application_id = $applicationId
    approved = $true
    amount = 6000
    validity_period = 365
    notes = "Approved based on land records"
} | ConvertTo-Json

$benefitApproveResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/benefits/approve" -Headers $authHeaders -Body $benefitApproveData
if ($benefitApproveResponse) {
    Write-Host "✅ Benefits Approve: $($benefitApproveResponse.status)" -ForegroundColor Green
} else {
    Write-Host "❌ Benefits Approve Failed" -ForegroundColor Red
}

# Test 10: Benefits Wallet
Write-Host "`n10. Testing Benefits Wallet..." -ForegroundColor Yellow
$walletResponse = Invoke-ApiRequest -Method "GET" -Url "$baseUrl/benefits/wallet" -Headers $authHeaders
if ($walletResponse) {
    Write-Host "✅ Benefits Wallet: $($walletResponse.total_entitlements) items" -ForegroundColor Green
    if ($walletResponse.wallet_items) {
        foreach ($item in $walletResponse.wallet_items) {
            Write-Host "   - $($item.scheme_name): ₹$($item.amount)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "❌ Benefits Wallet Failed" -ForegroundColor Red
}

# Test 11: Schemes List
Write-Host "`n11. Testing Schemes List..." -ForegroundColor Yellow
$schemesResponse = Invoke-ApiRequest -Method "GET" -Url "$baseUrl/schemes/" -Headers $authHeaders
if ($schemesResponse) {
    Write-Host "✅ Schemes: $($schemesResponse.total) available" -ForegroundColor Green
} else {
    Write-Host "❌ Schemes List Failed" -ForegroundColor Red
}

# Test 12: OTP Request
Write-Host "`n12. Testing OTP Request..." -ForegroundColor Yellow
$otpRequestData = @{
    phone = "+919876543210"
    purpose = "verification"
} | ConvertTo-Json

$otpRequestResponse = Invoke-ApiRequest -Method "POST" -Url "$baseUrl/auth/otp/request" -Body $otpRequestData
if ($otpRequestResponse) {
    Write-Host "✅ OTP Request: $($otpRequestResponse.otp_id)" -ForegroundColor Green
} else {
    Write-Host "❌ OTP Request Failed" -ForegroundColor Red
}

# Test 13: Error Handling - Invalid JWT
Write-Host "`n13. Testing Error Handling (Invalid JWT)..." -ForegroundColor Yellow
$invalidHeaders = @{
    "Authorization" = "Bearer invalid_token"
    "Content-Type" = "application/json"
}

$errorResponse = Invoke-ApiRequest -Method "GET" -Url "$baseUrl/benefits/wallet" -Headers $invalidHeaders
if (-not $errorResponse) {
    Write-Host "✅ Error Handling: Correctly rejected invalid JWT" -ForegroundColor Green
} else {
    Write-Host "❌ Error Handling: Should have rejected invalid JWT" -ForegroundColor Red
}

Write-Host "`n🎉 Testing Complete!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "All major endpoints tested successfully!" -ForegroundColor Green
Write-Host "Check the results above for any failures." -ForegroundColor Yellow
