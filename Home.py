"""
CivicLens home page. Run the whole app with:   streamlit run Home.py
"""
import streamlit as st

from core import db, logic

st.set_page_config(page_title="CivicLens", page_icon="📸", layout="wide")
db.init_db()
logic.refresh_all()

st.title("📸 CivicLens")
st.subheader("Snap it. Report it. See it fixed.")

st.write(
    "CivicLens lets anyone report a civic problem with **one photo**. "
    "AI identifies the problem, merges duplicate reports, scores how urgent it is, "
    "and sends it to the right department. Everyone can see what gets fixed."
)

issues = db.all_issues()
open_count = sum(i["status"] != "Resolved" for i in issues)
resolved = sum(i["status"] == "Resolved" for i in issues)
c1, c2, c3 = st.columns(3)
c1.metric("Issues reported", len(issues))
c2.metric("Open", open_count)
c3.metric("Resolved", resolved)

st.divider()
st.markdown("""
### Use the menu on the left
- **Report Problem** – citizens take a photo and report a problem
- **Department Portal** – staff see their issues by priority and mark them fixed
- **Public Dashboard** – live map, hotspots and SDG impact for everyone
""")
st.caption("Supports SDG 3, 5, 6, 7, 9, 11 and 12.")
