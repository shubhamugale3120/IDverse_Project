# 🧪 IDVerse Complete Testing Guide

## 🚀 **Quick Start Testing**

### **1. Health Check (Basic Test)**
```bash
# Test if server is running
curl http://localhost:5000/health
# Expected: {"status": "ok"}
```

### **2. User Registration & Login Flow**
```bash
# Step 1: Register new user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123"
  }'

# Expected: {"message": "User registered successfully", "user": {...}}

# Step 2: Login to get JWT token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Expected: {"access_token": "eyJ...", "user": {...}}
# SAVE THE access_token for protected routes!
```

### **3. VC (Verifiable Credential) Lifecycle Testing**

#### **Step 1: Request VC Issue**
```bash
# Replace YOUR_JWT_TOKEN with actual token from login
curl -X POST http://localhost:5000/vc/request-issue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "type": "GovID",
    "claims": {
      "name": "Shubham Ugale",
      "age": 25,
      "address": "Mumbai, India"
    }
  }'

# Expected: {"request_id": "req-GovID-abc123", "status": "pending", ...}
```

#### **Step 2: Issue VC (Authority Action)**
```bash
curl -X POST http://localhost:5000/vc/issue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "request_id": "req-GovID-abc123"
  }'

# Expected: {"vc_id": "vc-123", "status": "issued", "cid": "bafybeig...", ...}
```

#### **Step 3: Check VC Status**
```bash
curl -X GET http://localhost:5000/vc/status/vc-123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: {"vc_id": "vc-123", "status": "issued", "verifiable": true, ...}
```

#### **Step 4: Present VC (Verification)**
```bash
curl -X POST http://localhost:5000/vc/present \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "vc_id": "vc-123",
    "verifier_did": "did:example:verifier"
  }'

# Expected: {"presentation": {...}, "verified": true, ...}
```

### **4. Benefits System Testing**

#### **Step 1: Apply for Benefit**
```bash
curl -X POST http://localhost:5000/benefits/apply \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "scheme_id": "scheme-001",
    "scheme_name": "PM Kisan Yojana",
    "required_credentials": ["GovID"],
    "application_data": {
      "land_holding": "2 acres",
      "bank_account": "1234567890"
    }
  }'

# Expected: {"application_id": "app-123", "status": "pending", ...}
```

#### **Step 2: Approve Benefit (Authority)**
```bash
curl -X POST http://localhost:5000/benefits/approve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "application_id": "app-123",
    "approved": true,
    "amount": 6000,
    "validity_period": 365
  }'

# Expected: {"application_id": "app-123", "status": "approved", ...}
```

#### **Step 3: View Wallet**
```bash
curl -X GET http://localhost:5000/benefits/wallet \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: {"wallet_items": [...], "total_entitlements": 1, ...}
```

### **5. OTP System Testing**
```bash
# Request OTP
curl -X POST http://localhost:5000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "purpose": "verification"
  }'

# Expected: {"otp_id": "otp-123", "message": "OTP sent"}

# Verify OTP
curl -X POST http://localhost:5000/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "otp_id": "otp-123",
    "otp_code": "123456"
  }'

# Expected: {"verified": true, "message": "OTP verified"}
```

### **6. Scheme Engine Testing**
```bash
curl -X GET http://localhost:5000/schemes/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: {"schemes": [...], "total": 5, ...}
```

## 🔧 **Postman Collection Setup**

### **Environment Variables in Postman:**
1. `base_url`: `http://localhost:5000`
2. `jwt_token`: (set after login)

### **Headers for All Requests:**
- `Content-Type`: `application/json`
- `Authorization`: `Bearer {{jwt_token}}` (for protected routes)

## 🐛 **Error Testing**

### **Test Invalid JWT:**
```bash
curl -X GET http://localhost:5000/benefits/wallet \
  -H "Authorization: Bearer invalid_token"

# Expected: 401 Unauthorized
```

### **Test Missing Required Fields:**
```bash
curl -X POST http://localhost:5000/vc/request-issue \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{}'

# Expected: 400 Bad Request with error message
```

### **Test Duplicate Registration:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Expected: 400 Bad Request - "Email already registered"
```

## 📊 **Complete Workflow Test**

### **End-to-End Scenario:**
1. **Register** → Get user account
2. **Login** → Get JWT token
3. **Request VC** → Create credential request
4. **Issue VC** → Authority issues credential
5. **Apply Benefit** → Citizen applies for scheme
6. **Approve Benefit** → Authority approves
7. **View Wallet** → See entitlements
8. **Present VC** → Verify credential

## 🎯 **Expected Results Summary**

| Endpoint | Status | Response |
|----------|--------|----------|
| `/health` | 200 | `{"status": "ok"}` |
| `/auth/register` | 201 | User created |
| `/auth/login` | 200 | JWT token |
| `/vc/request-issue` | 202 | Request ID |
| `/vc/issue` | 201 | VC ID + CID |
| `/vc/status/{id}` | 200 | VC status |
| `/vc/present` | 200 | Verification result |
| `/benefits/apply` | 201 | Application ID |
| `/benefits/approve` | 200 | Approval status |
| `/benefits/wallet` | 200 | Wallet items |

## 🚨 **Troubleshooting**

### **Common Issues:**
1. **500 Error**: Check server logs, database connection
2. **401 Unauthorized**: Invalid/missing JWT token
3. **404 Not Found**: Wrong endpoint URL
4. **400 Bad Request**: Missing required fields

### **Debug Commands:**
```bash
# Check all routes
curl http://localhost:5000/_debug/routes

# Check server health
curl http://localhost:5000/health
```

## 🎉 **Success Criteria**
- ✅ All endpoints return expected status codes
- ✅ JWT authentication works for protected routes
- ✅ Database operations complete successfully
- ✅ Mock services return realistic data
- ✅ Error handling works properly
- ✅ Complete user journey from registration to benefit approval

---

**Ready to test! Start with health check, then follow the workflow step by step.**
