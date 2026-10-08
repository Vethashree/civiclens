"""
Citizen page: take a photo -> AI identifies the problem -> pick location -> submit.
"""
import io

import folium
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium

import config
from core import ai, db, logic

st.set_page_config(page_title="Report Problem", page_icon="📸", layout="wide")
db.init_db()
logic.refresh_all()

st.title("📸 Report a Problem")

# ---------- Step 1: photo ----------
st.header("1. Take or upload a photo")
source = st.radio("How do you want to add the photo?", ["Upload a photo", "Use camera"], horizontal=True)
if source == "Use camera":
    st.caption("Allow camera access if your browser asks. Then click **Take Photo** below the camera view. "
               "To turn the camera off, choose **Upload a photo** above.")
    photo = st.camera_input("Point the camera at the problem")
else:
    photo = st.file_uploader("Upload a photo (JPG, PNG or WEBP)", type=["jpg", "jpeg", "png", "webp"])


def to_jpeg(raw):
    """Convert any photo format (e.g. WEBP or PNG) to JPEG so every part of the app can use it."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue()


category = None
confidence = 0.0
if photo:
    try:
        image_bytes = to_jpeg(photo.getvalue())
    except Exception:
        st.error("Sorry, that file couldn't be opened as a photo. Please try a JPG or PNG.")
        st.stop()
    st.image(image_bytes, width=300)

    # ---------- Step 2: AI identifies the problem ----------
    st.header("2. AI result")
    ai_category, confidence, scores = ai.classify(image_bytes)
    names = list(config.CATEGORIES)

    if ai_category:
        st.success(f"AI thinks this is: **{ai_category}** ({confidence:.0%} sure) "
                   f"→ goes to **{config.CATEGORIES[ai_category]['dept']}** department")
        with st.expander("See all AI scores"):
            for name, s in sorted(scores.items(), key=lambda x: -x[1]):
                st.progress(s, text=f"{name}: {s:.0%}")
        default = names.index(ai_category)
    else:
        st.warning("AI model is not available right now, so please choose the category yourself.")
        if st.session_state.get("ai_error"):
            st.code("Reason: " + st.session_state["ai_error"], language=None)
        default = 0

    category = st.selectbox("Category (change it if the AI got it wrong)", names, index=default)
    if st.checkbox("This is a dark or unsafe spot (women's safety report)"):
        category = "Dark / unsafe spot"

    # ---------- Step 3: location ----------
    st.header("3. Tap the map where the problem is")
    if "pin" not in st.session_state:
        st.session_state.pin = config.MAP_CENTER
    m = folium.Map(location=st.session_state.pin, zoom_start=config.MAP_ZOOM)
    folium.Marker(st.session_state.pin, tooltip="Problem location").add_to(m)
    clicked = st_folium(m, height=350, width=700, key="report_map")
    if clicked and clicked.get("last_clicked"):
        new_pin = (clicked["last_clicked"]["lat"], clicked["last_clicked"]["lng"])
        if new_pin != st.session_state.pin:
            st.session_state.pin = new_pin
            st.rerun()
    lat, lon = st.session_state.pin
    st.caption(f"Location: {lat:.5f}, {lon:.5f}")

    description = st.text_input("Short description (optional)", placeholder="e.g. Near the main gate")

    # ---------- Step 4: submit ----------
    if st.button("Submit report", type="primary"):
        saved = db.save_photo(image_bytes)
        dup = logic.find_duplicate(category, lat, lon)
        if dup:
            db.add_duplicate_report(dup["id"], saved)
            logic.refresh_all()
            st.info(f"This problem was already reported nearby. Your report was **merged** into "
                    f"issue **#{dup['id']}**, which now has **{dup['report_count'] + 1} reports** "
                    f"and a higher priority.")
            issue_id = dup["id"]
        else:
            dept = config.CATEGORIES[category]["dept"]
            sev = logic.severity_score(category, 1, lat, lon)
            issue_id = db.add_issue(category, dept, lat, lon, description, saved, sev, confidence)
            place = logic.nearest_sensitive_place(lat, lon)
            st.success(f"Reported! Your tracking ID is **#{issue_id}**. Sent to **{dept}** department. "
                       f"Severity score: **{sev}/100**" + (f" (near {place})" if place else ""))
        st.balloons()

# ---------- Track a report ----------
st.divider()
st.header("🔎 Track your report")
track_id = st.number_input("Enter your tracking ID", min_value=1, step=1, value=None)
if track_id:
    issue = db.get_issue(int(track_id))
    if not issue:
        st.error("No report found with that ID.")
    else:
        st.write(f"**{issue['category']}** – {issue['department']} department")
        st.write(f"Status: **{issue['status']}** · Reports: {issue['report_count']} · "
                 f"Severity: {issue['severity']}/100" + (" · ⚠️ Escalated" if issue["escalated"] else ""))
        cols = st.columns(2)
        cols[0].image(issue["photo"], caption="Before", width=250)
        if issue["after_photo"]:
            cols[1].image(issue["after_photo"], caption="After (fixed)", width=250)
