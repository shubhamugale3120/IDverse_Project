# Theory
# 6. backend/scheme_engine/engine.py
# Role: Suggests government welfare schemes based on user data.
# This would later be exposed as /schemes API.
# ✅ Frontend integrates here:
# Dashboard → fetches suggested schemes for logged-in user.


# backend/scheme_engine/engine.py
def suggest_schemes(user):
    """
    Replace this stub with your real rules/ML later.
    For now return a few items so frontend can integrate.
    """
    recs = [{"id": 1, "name": "General Citizen Benefit", "score": 0.6}]
    if user.email.endswith("@student.com"):
        recs.append({"id": 2, "name": "Student Scholarship", "score": 0.9})
    if user.username.lower() == "shubham":
        recs.append({"id": 3, "name": "Founder Special Scheme", "score": 0.8})
    return recs
