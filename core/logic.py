"""
The "smart" rules of CivicLens: duplicate merging, severity score and escalation.
"""
import math
from datetime import datetime

import config
from core import db


def distance_metres(lat1, lon1, lat2, lon2):
    """Distance between two GPS points (haversine formula)."""
    r = 6_371_000  # Earth's radius in metres
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_duplicate(category, lat, lon):
    """Return an OPEN issue of the same category within the duplicate radius, or None."""
    for issue in db.all_issues():
        if issue["status"] == "Resolved" or issue["category"] != category:
            continue
        if distance_metres(lat, lon, issue["latitude"], issue["longitude"]) <= config.DUPLICATE_RADIUS_METRES:
            return issue
    return None


def nearest_sensitive_place(lat, lon):
    """Return the name of a school/hospital nearby, or None."""
    for name, plat, plon in config.SENSITIVE_PLACES:
        if distance_metres(lat, lon, plat, plon) <= config.SENSITIVE_RADIUS_METRES:
            return name
    return None


def hours_open(issue):
    created = datetime.fromisoformat(issue["created_at"])
    return (datetime.now() - created).total_seconds() / 3600


def severity_score(category, report_count, lat, lon, age_hours=0):
    """
    Severity out of 100:
      base by problem type (up to 40)
      + 5 per extra report (up to 25)
      + 20 if near a school/hospital
      + up to 15 for how long it has been open
    """
    score = config.CATEGORIES[category]["base"]
    score += min((report_count - 1) * 5, 25)
    if nearest_sensitive_place(lat, lon):
        score += 20
    score += min(age_hours / 24 * 5, 15)
    return int(min(score, 100))


def refresh_all():
    """
    Recalculate severity and check escalation for every open issue.
    Called each time a page loads.
    """
    for issue in db.all_issues():
        if issue["status"] == "Resolved":
            continue
        age = hours_open(issue)
        new_sev = severity_score(issue["category"], issue["report_count"],
                                 issue["latitude"], issue["longitude"], age)
        limit = config.CATEGORIES[issue["category"]]["limit_hours"]
        # In demo mode the limit is in minutes, so you can show escalation at the expo
        limit_in_hours = limit / 60 if config.DEMO_FAST_ESCALATION else limit
        escalate = 1 if age > limit_in_hours else issue["escalated"]
        db.update_issue(issue["id"], severity=new_sev, escalated=escalate)
