  # DB & environment configuration

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")



# theory
# 2. backend/config.py
# Role: Stores all configuration values for your app.
# Uses .env file for secrets. 
# Why: Keeps passwords, DB strings, API keys out of code.
# ✅ Frontend doesn’t touch this (backend-only).