"""
Department staff page: log in, see issues sorted by priority, update status, upload after-photo.
"""
import io

import streamlit as st
from PIL import Image

import config
from core import db, logic

st.set_page_config(page_title="Department Portal", page_icon="🏛️", layout="wide")
db.init_db()
logic.refresh_all()

st.title("🏛️ Department Portal")

# ---------- Simple login ----------
if not st.session_state.get("logged_in"):
    pw = st.text_input("Department password", type="password")
    if st.button("Log in"):
        # Online, the password comes from the app's private "Secrets" settings,
        # so it isn't visible in your public code. On your laptop, config.py is used.
        try:
            real_pw = st.secrets["DEPARTMENT_PASSWORD"]
        except Exception:
            real_pw = config.DEPARTMENT_PASSWORD
        if pw == real_pw:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

departments = sorted({c["dept"] for c in config.CATEGORIES.values()})
dept = st.selectbox("Your department", ["All departments"] + departments)
show_resolved = st.checkbox("Show resolved issues too")

issues = db.all_issues()
if dept != "All departments":
    issues = [i for i in issues if i["department"] == dept]
if not show_resolved:
    issues = [i for i in issues if i["status"] != "Resolved"]
issues.sort(key=lambda i: (-i["escalated"], -i["severity"]))   # escalated + most urgent first

st.write(f"**{len(issues)} issue(s)**, most urgent first")

for issue in issues:
    flag = "⚠️ ESCALATED · " if issue["escalated"] and issue["status"] != "Resolved" else ""
    title = (f"{flag}#{issue['id']} {issue['category']} · severity {issue['severity']} · "
             f"{issue['report_count']} report(s) · {issue['status']}")
    with st.expander(title):
        c1, c2 = st.columns([1, 2])
        c1.image(issue["photo"], width=250)
        with c2:
            st.write(f"Reported: {issue['created_at'].replace('T', ' ')}")
            st.write(f"Location: {issue['latitude']:.5f}, {issue['longitude']:.5f}")
            if issue["description"]:
                st.write(f"Note: {issue['description']}")
            place = logic.nearest_sensitive_place(issue["latitude"], issue["longitude"])
            if place:
                st.write(f"Near: **{place}**")

            if issue["status"] != "Resolved":
                if issue["status"] == "Open" and st.button("Mark In progress", key=f"prog{issue['id']}"):
                    db.update_issue(issue["id"], status="In progress")
                    st.rerun()
                after = st.file_uploader("Upload 'after' photo to resolve", type=["jpg", "jpeg", "png", "webp"],
                                         key=f"after{issue['id']}")
                if after and st.button("Mark Resolved", key=f"res{issue['id']}", type="primary"):
                    img = Image.open(io.BytesIO(after.getvalue())).convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=90)
                    path = db.save_photo(buf.getvalue(), prefix="after")
                    db.update_issue(issue["id"], status="Resolved", after_photo=path, resolved_at=db.now())
                    st.success("Resolved! The citizen can now see the after-photo.")
                    st.rerun()
            elif issue["after_photo"]:
                st.image(issue["after_photo"], caption="After", width=250)
