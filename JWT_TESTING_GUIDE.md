# 🔐 JWT Testing Guide - IDVerse Project

## 📋 **What is JWT?**

**JWT (JSON Web Token)** is a secure way to transmit information between parties. In our IDVerse project:

- **Login** → Server returns JWT token
- **Protected endpoints** → Client sends JWT in `Authorization` header
- **Server** → Validates JWT and extracts user identity

## 🎯 **JWT Token Structure**

```json
{
  "sub": "user@example.com",     // Subject (user email)
  "exp": 1757084510,            // Expiration timestamp
  "iat": 1757083610,            // Issued at timestamp
  "nbf": 1757083610,            // Not before timestamp
  "jti": "c39b2e56-6c60-4c93-962b-31ba6c6c0ccc"  // JWT ID
}
```

## 🚀 **Step-by-Step JWT Testing**

### **Step 1: Start the Server**
```powershell
# Activate virtual environment
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\env\Scripts\Activate.ps1

# Start Flask server
python run.py
```

### **Step 2: Register a User (No JWT Required)**
```powershell
# Create request body
$registerBody = @{
    username = "testuser"
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

# Make registration request
$registerResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/register" -Method POST -Body $registerBody -ContentType "application/json"

# Check response
Write-Host "Registration Status: $($registerResponse.StatusCode)"
Write-Host "Response: $($registerResponse.Content)"
```

**Expected Response:**
```json
{
  "msg": "User registered successfully"
}
```

### **Step 3: Login and Get JWT Token**
```powershell
# Create login request body
$loginBody = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

# Make login request
$loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/login" -Method POST -Body $loginBody -ContentType "application/json"

# Extract JWT token from response
$loginData = $loginResponse.Content | ConvertFrom-Json
$accessToken = $loginData.access_token

# Display token info
Write-Host "Login Status: $($loginResponse.StatusCode)"
Write-Host "JWT Token: $($accessToken.Substring(0, 50))..."
Write-Host "User Info: $($loginData.user | ConvertTo-Json)"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### **Step 4: Test Protected Endpoints with JWT**

#### **4.1 Test VC Request Issue (Protected)**
```powershell
# Create headers with JWT token
$headers = @{
    "Authorization" = "Bearer $accessToken"  # JWT token in Authorization header
    "Content-Type" = "application/json"
}

# Create request body
$vcRequestBody = @{
    type = "GovID"
    claims = @{
        name = "Shubham Ugale"
        age = 22
        address = "Mumbai, India"
    }
} | ConvertTo-Json

# Make protected request
$vcResponse = Invoke-WebRequest -Uri "http://localhost:5000/vc/request-issue" -Method POST -Body $vcRequestBody -Headers $headers

# Check response
Write-Host "VC Request Status: $($vcResponse.StatusCode)"
Write-Host "Response: $($vcResponse.Content)"
```

**Expected Response:**
```json
{
  "request_id": "req-GovID-001",
  "status": "received",
  "next": "/vc/issue"
}
```

#### **4.2 Test VC Issue (Protected)**
```powershell
# Create request body for VC issuance
$vcIssueBody = @{
    type = "StudentCard"
    subject_id = "test@example.com"
    claims = @{
        university = "Mumbai University"
        course = "Computer Science"
        enrollment_year = 2023
    }
} | ConvertTo-Json

# Make protected request
$vcIssueResponse = Invoke-WebRequest -Uri "http://localhost:5000/vc/issue" -Method POST -Body $vcIssueBody -Headers $headers

# Check response
Write-Host "VC Issue Status: $($vcIssueResponse.StatusCode)"
Write-Host "Response: $($vcIssueResponse.Content)"
```

**Expected Response:**
```json
{
  "vc_id": "vc-001",
  "cid": "bafybeigdyrstubcidexample",
  "vc": {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiableCredential", "StudentCard"],
    "issuer": "did:example:issuer",
    "credentialSubject": {
      "id": "did:example:test@example.com",
      "university": "Mumbai University",
      "course": "Computer Science",
      "enrollment_year": 2023
    },
    "proof": {
      "type": "Ed25519Signature2020",
      "created": "now",
      "jws": "stub"
    }
  }
}
```

#### **4.3 Test Benefits Wallet (Protected)**
```powershell
# Make GET request to benefits wallet
$walletResponse = Invoke-WebRequest -Uri "http://localhost:5000/benefits/wallet" -Method GET -Headers $headers

# Check response
Write-Host "Wallet Status: $($walletResponse.StatusCode)"
Write-Host "Response: $($walletResponse.Content)"
```

**Expected Response:**
```json
{
  "owner": "test@example.com",
  "entitlements": [
    {
      "scheme": "PM-Kisan",
      "amount": 2000,
      "status": "active"
    },
    {
      "scheme": "Scholarship",
      "amount": 5000,
      "status": "active"
    }
  ]
}
```

## ❌ **Common JWT Testing Errors**

### **Error 1: Missing Authorization Header**
```powershell
# WRONG: No Authorization header
$response = Invoke-WebRequest -Uri "http://localhost:5000/vc/request-issue" -Method POST -Body $body -ContentType "application/json"
# Result: 401 Unauthorized
```

**Solution:**
```powershell
# CORRECT: Include Authorization header
$headers = @{"Authorization" = "Bearer $accessToken"}
$response = Invoke-WebRequest -Uri "http://localhost:5000/vc/request-issue" -Method POST -Body $body -Headers $headers
```

### **Error 2: Wrong Token Format**
```powershell
# WRONG: Missing "Bearer " prefix
$headers = @{"Authorization" = "$accessToken"}
# Result: 401 Unauthorized
```

**Solution:**
```powershell
# CORRECT: Include "Bearer " prefix
$headers = @{"Authorization" = "Bearer $accessToken"}
```

### **Error 3: Expired Token**
```powershell
# If token is expired, you'll get 401 Unauthorized
# Solution: Login again to get a new token
```

### **Error 4: Invalid Token**
```powershell
# WRONG: Using invalid/malformed token
$headers = @{"Authorization" = "Bearer invalid_token"}
# Result: 401 Unauthorized
```

## 🧪 **Complete Testing Script**

```powershell
# Complete JWT Testing Script
Write-Host "🔐 JWT Testing Script for IDVerse" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Step 1: Register User
Write-Host "`n1️⃣ Registering User..." -ForegroundColor Yellow
$registerBody = @{
    username = "jwt_test_user"
    email = "jwt_test@example.com"
    password = "password123"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "✅ Registration: $($registerResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Registration: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 2: Login and Get JWT
Write-Host "`n2️⃣ Logging In..." -ForegroundColor Yellow
$loginBody = @{
    email = "jwt_test@example.com"
    password = "password123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $accessToken = $loginData.access_token
    Write-Host "✅ Login: $($loginResponse.StatusCode)" -ForegroundColor Green
    Write-Host "JWT Token: $($accessToken.Substring(0, 50))..." -ForegroundColor Cyan
} catch {
    Write-Host "❌ Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Test Protected Endpoints
Write-Host "`n3️⃣ Testing Protected Endpoints..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

# Test VC Request Issue
$vcBody = @{
    type = "GovID"
    claims = @{
        name = "JWT Test User"
        age = 25
    }
} | ConvertTo-Json

try {
    $vcResponse = Invoke-WebRequest -Uri "http://localhost:5000/vc/request-issue" -Method POST -Body $vcBody -Headers $headers
    Write-Host "✅ VC Request: $($vcResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($vcResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ VC Request Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Benefits Wallet
try {
    $walletResponse = Invoke-WebRequest -Uri "http://localhost:5000/benefits/wallet" -Method GET -Headers $headers
    Write-Host "✅ Benefits Wallet: $($walletResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($walletResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Benefits Wallet Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 JWT Testing Complete!" -ForegroundColor Green
```

## 📝 **JWT Best Practices**

### **1. Token Storage**
- **Frontend**: Store in localStorage or sessionStorage
- **Mobile**: Store in secure keychain
- **Never**: Store in plain text or cookies

### **2. Token Security**
- **Expiration**: Set reasonable expiration times (15-60 minutes)
- **Refresh**: Implement refresh token mechanism
- **HTTPS**: Always use HTTPS in production

### **3. Error Handling**
- **401 Unauthorized**: Token missing, invalid, or expired
- **403 Forbidden**: Valid token but insufficient permissions
- **Automatic Refresh**: Implement automatic token refresh

## 🔧 **Troubleshooting**

### **Server Not Running**
```powershell
# Check if server is running
Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET
# If error: Start server with python run.py
```

### **Database Issues**
```powershell
# Check database connection
# Ensure MySQL is running and .env file has correct DATABASE_URL
```

### **Port Conflicts**
```powershell
# If port 5000 is busy, change port in run.py
# app.run(debug=True, port=5001)
```

This guide covers everything you need to test JWT authentication in your IDVerse project! 🚀
