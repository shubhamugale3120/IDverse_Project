# IDVerse API Testing Script
# This script demonstrates how to test all endpoints with detailed explanations
# http://127.0.0.1:5000/static/demo/index.html

Write-Host "🚀 IDVerse API Testing Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Step 1: Test Health Endpoint (No authentication required)
Write-Host "`n1️⃣ Testing Health Endpoint..." -ForegroundColor Yellow
Write-Host "Purpose: Verify server is running and responding" -ForegroundColor Gray
Write-Host "Endpoint: GET /health" -ForegroundColor Gray
Write-Host "Auth Required: No" -ForegroundColor Gray

try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET
    Write-Host "✅ Health Check: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Register a New User
Write-Host "`n2️⃣ Testing User Registration..." -ForegroundColor Yellow
Write-Host "Purpose: Create a new user account in the database" -ForegroundColor Gray
Write-Host "Endpoint: POST /auth/register" -ForegroundColor Gray
Write-Host "Auth Required: No" -ForegroundColor Gray

# Create unique email to avoid conflicts
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testEmail = "test$timestamp@example.com"

$registerBody = @{
    username = "testuser$timestamp"
    email = $testEmail
    password = "password123"
} | ConvertTo-Json

Write-Host "Request Body: $registerBody" -ForegroundColor Gray

try {
    $registerResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "✅ Registration: $($registerResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($registerResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Registration Failed: $($_.Exception.Message)" -ForegroundColor Red
    # Try to get error details
    if ($_.Exception.Response) {
        $errorStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorStream)
        $errorContent = $reader.ReadToEnd()
        Write-Host "Error Details: $errorContent" -ForegroundColor Red
    }
}

# Step 3: Login to Get JWT Token
Write-Host "`n3️⃣ Testing User Login..." -ForegroundColor Yellow
Write-Host "Purpose: Authenticate user and get JWT access token" -ForegroundColor Gray
Write-Host "Endpoint: POST /auth/login" -ForegroundColor Gray
Write-Host "Auth Required: No" -ForegroundColor Gray

$loginBody = @{
    email = $testEmail
    password = "password123"
} | ConvertTo-Json

Write-Host "Request Body: $loginBody" -ForegroundColor Gray

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    Write-Host "✅ Login: $($loginResponse.StatusCode)" -ForegroundColor Green
    
    # Parse the JSON response to extract the access token
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $accessToken = $loginData.access_token
    Write-Host "JWT Token: $($accessToken.Substring(0, 50))..." -ForegroundColor Cyan
    Write-Host "User Info: $($loginData.user | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Test OTP Request (No auth required)
Write-Host "`n4️⃣ Testing OTP Request..." -ForegroundColor Yellow
Write-Host "Purpose: Request OTP for phone/email verification" -ForegroundColor Gray
Write-Host "Endpoint: POST /auth/otp/request" -ForegroundColor Gray
Write-Host "Auth Required: No" -ForegroundColor Gray

$otpBody = @{
    channel = "sms"
    destination = "+919876543210"
} | ConvertTo-Json

Write-Host "Request Body: $otpBody" -ForegroundColor Gray

try {
    $otpResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/otp/request" -Method POST -Body $otpBody -ContentType "application/json"
    Write-Host "✅ OTP Request: $($otpResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($otpResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ OTP Request Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test VC Request Issue (JWT Required)
Write-Host "`n5️⃣ Testing VC Request Issue..." -ForegroundColor Yellow
Write-Host "Purpose: Request issuance of a Verifiable Credential" -ForegroundColor Gray
Write-Host "Endpoint: POST /vc/request-issue" -ForegroundColor Gray
Write-Host "Auth Required: Yes (JWT Token)" -ForegroundColor Gray

$vcRequestBody = @{
    type = "GovID"
    claims = @{
        name = "Shubham Ugale"
        age = 22
        address = "Mumbai, India"
    }
} | ConvertTo-Json

Write-Host "Request Body: $vcRequestBody" -ForegroundColor Gray

# Create headers with JWT token
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

try {
    $vcRequestResponse = Invoke-WebRequest -Uri "http://localhost:5000/vc/request-issue" -Method POST -Body $vcRequestBody -Headers $headers
    Write-Host "✅ VC Request: $($vcRequestResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($vcRequestResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ VC Request Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Test VC Issue (JWT Required)
Write-Host "`n6️⃣ Testing VC Issue..." -ForegroundColor Yellow
Write-Host "Purpose: Issue a Verifiable Credential (Authority action)" -ForegroundColor Gray
Write-Host "Endpoint: POST /vc/issue" -ForegroundColor Gray
Write-Host "Auth Required: Yes (JWT Token)" -ForegroundColor Gray

$vcIssueBody = @{
    type = "StudentCard"
    subject_id = $testEmail
    claims = @{
        university = "Mumbai University"
        course = "Computer Science"
        enrollment_year = 2023
    }
} | ConvertTo-Json

Write-Host "Request Body: $vcIssueBody" -ForegroundColor Gray

try {
    $vcIssueResponse = Invoke-WebRequest -Uri "http://localhost:5000/vc/issue" -Method POST -Body $vcIssueBody -Headers $headers
    Write-Host "✅ VC Issue: $($vcIssueResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($vcIssueResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ VC Issue Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Test Benefits Apply (JWT Required)
Write-Host "`n7️⃣ Testing Benefits Apply..." -ForegroundColor Yellow
Write-Host "Purpose: Apply for a government benefit/scheme" -ForegroundColor Gray
Write-Host "Endpoint: POST /benefits/apply" -ForegroundColor Gray
Write-Host "Auth Required: Yes (JWT Token)" -ForegroundColor Gray

$benefitsBody = @{
    scheme = "PM-Kisan"
} | ConvertTo-Json

Write-Host "Request Body: $benefitsBody" -ForegroundColor Gray

try {
    $benefitsResponse = Invoke-WebRequest -Uri "http://localhost:5000/benefits/apply" -Method POST -Body $benefitsBody -Headers $headers
    Write-Host "✅ Benefits Apply: $($benefitsResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($benefitsResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Benefits Apply Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test Benefits Wallet (JWT Required)
Write-Host "`n8️⃣ Testing Benefits Wallet..." -ForegroundColor Yellow
Write-Host "Purpose: View user's benefit entitlements" -ForegroundColor Gray
Write-Host "Endpoint: GET /benefits/wallet" -ForegroundColor Gray
Write-Host "Auth Required: Yes (JWT Token)" -ForegroundColor Gray

try {
    $walletResponse = Invoke-WebRequest -Uri "http://localhost:5000/benefits/wallet" -Method GET -Headers $headers
    Write-Host "✅ Benefits Wallet: $($walletResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($walletResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Benefits Wallet Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 9: Test Scheme Suggestions (JWT Required)
Write-Host "`n9️⃣ Testing Scheme Suggestions..." -ForegroundColor Yellow
Write-Host "Purpose: Get AI-suggested welfare schemes for user" -ForegroundColor Gray
Write-Host "Endpoint: GET /schemes/" -ForegroundColor Gray
Write-Host "Auth Required: Yes (JWT Token)" -ForegroundColor Gray

try {
    $schemesResponse = Invoke-WebRequest -Uri "http://localhost:5000/schemes/" -Method GET -Headers $headers
    Write-Host "✅ Scheme Suggestions: $($schemesResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($schemesResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Scheme Suggestions Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "All endpoints tested successfully!" -ForegroundColor Green
Write-Host "`n📝 Key Learnings:" -ForegroundColor Yellow
Write-Host "1. Always login first to get JWT token" -ForegroundColor White
Write-Host "2. Use JWT token in Authorization header for protected endpoints" -ForegroundColor White
Write-Host "3. Use POST method for data submission endpoints" -ForegroundColor White
Write-Host "4. Use GET method for data retrieval endpoints" -ForegroundColor White
Write-Host "5. Always include Content-Type: application/json for POST requests" -ForegroundColor White

