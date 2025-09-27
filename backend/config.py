# DB & environment configuration

import os

class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "myjwtsecret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///idverse.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

print(">>> Loaded DATABASE_URL =", os.getenv("DATABASE_URL", "sqlite:///idverse.db"))  # 👈 add this

# theory
# 2. backend/config.py
# Role: Stores all configuration values for your app.
# Uses .env file for secrets. 
# Why: Keeps passwords, DB strings, API keys out of code.
# ✅ Frontend doesn’t touch this (backend-only).