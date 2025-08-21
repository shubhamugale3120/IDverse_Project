from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


# theory
# 3. backend/extensions.py
# Role: Central place to initialize Flask extensions.
# db = SQLAlchemy()
# jwt = JWTManager()
# Why: Keeps app factory (__init__.py) clean and organized.
# ✅ Frontend doesn’t touch this.

