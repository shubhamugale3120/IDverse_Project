# Theory
# Role: Entry point. Runs the Flask app.
# Frontend doesn’t touch this.9. 
# 
# # .env
# Role: Stores secrets like database URI, JWT secret.

# FLASK_ENV=development
# SECRET_KEY=super-secret-key
# JWT_SECRET_KEY=super-jwt-secret
# SQLALCHEMY_DATABASE_URI=sqlite:///idverse.db
# ✅ Frontend doesn’t touch this.

# whole work
# Backend ↔ Frontend Integration Points
# Backend File / API	            What it does	     Which frontend page uses it
# /auth/register (auth/routes.py)-->	Register new user	  -->        Registration Page
# /auth/login (auth/routes.py)-->	Login + JWT token	   -->          Login Page
# /schemes (scheme_engine/engine.py)-->	Suggest welfare schemes	  -->    Dashboard
# /user/<uid> (model.py + blockchain.py)-->	Fetch user profile + digital ID	-->Profile Page
# /wallet (future)-->	Show benefits wallet	-->Wallet Page
# /health	Debug only	None (backend check)-->