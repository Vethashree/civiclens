"""
CivicLens settings. Beginners: this is the main file you edit to customise the app.
"""

# ---------- Map ----------
# Centre of the map when the app opens. Change this to your college's location.
# (Open Google Maps, right-click your college, and copy the two numbers shown.)
MAP_CENTER = (13.0827, 80.2707)   # Chennai, as an example
MAP_ZOOM = 15

# ---------- Problem categories ----------
# For each category: which department fixes it, which SDG it supports,
# its base severity (0-40), and how many HOURS the department has before escalation.
CATEGORIES = {
    "Garbage dump":       {"dept": "Sanitation",   "sdg": "SDG 12", "base": 35, "limit_hours": 48},
    "Pothole":            {"dept": "Roads",        "sdg": "SDG 9",  "base": 25, "limit_hours": 72},
    "Water leak":         {"dept": "Water Supply", "sdg": "SDG 6",  "base": 30, "limit_hours": 24},
    "Drain overflow":     {"dept": "Sanitation",   "sdg": "SDG 6",  "base": 40, "limit_hours": 24},
    "Broken streetlight": {"dept": "Electrical",   "sdg": "SDG 7",  "base": 20, "limit_hours": 48},
    "Stagnant water":     {"dept": "Health",       "sdg": "SDG 3",  "base": 40, "limit_hours": 24},
    "Dark / unsafe spot": {"dept": "Electrical",   "sdg": "SDG 5",  "base": 35, "limit_hours": 48},
}

# Sentences the AI compares each photo against (one per category).
# "Dark / unsafe spot" is chosen by the user, not the AI, so it is not listed here.
AI_PROMPTS = {
    "Garbage dump":       "a photo of a pile of garbage and trash dumped on the street",
    "Pothole":            "a photo of a pothole on a road",
    "Water leak":         "a photo of water leaking from a broken pipe",
    "Drain overflow":     "a photo of an overflowing drain or sewage on the road",
    "Broken streetlight": "a photo of a street light pole",
    "Stagnant water":     "a photo of a large stagnant puddle of dirty water",
}

# ---------- Duplicate merging ----------
DUPLICATE_RADIUS_METRES = 50   # same category within this distance = same issue

# ---------- Sensitive places (raise severity if a problem is near them) ----------
# Add schools, hospitals, bus stands near your demo area: (name, latitude, longitude)
SENSITIVE_PLACES = [
    ("Example School",   13.0840, 80.2720),
    ("Example Hospital", 13.0810, 80.2690),
]
SENSITIVE_RADIUS_METRES = 200

# ---------- Demo settings ----------
# For the expo, set this to True so escalation happens after MINUTES instead of hours.
DEMO_FAST_ESCALATION = True

# Simple password for the department portal (change it!)
DEPARTMENT_PASSWORD = "admin123"
