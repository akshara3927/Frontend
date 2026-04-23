"""
Module 40 – Research Studies View (Streamlit + MongoDB)
"""
import streamlit as st
from datetime import datetime
from database import research

def research_studies_view():
    email = st.session_state.get("email", "")
    role = st.session_state.get("role", "Patient")

    st.header("🔬 Research Studies")

    if not email:
        st.error("❌ Please login first")
        st.stop()

    # ───────────── CREATE STUDY ─────────────
    if role in ("Doctor", "Admin"):
        with st.expander("➕ Create New Research Study"):
            with st.form("create_study_form"):
                title = st.text_input("Study Title")
                description = st.text_area("Description")
                data_types = st.multiselect(
                    "Data Types Required",
                    ["medical_records", "lab_results", "imaging",
                     "prescriptions", "research_data"]
                )
                status = st.selectbox("Status", ["Recruiting", "Active", "Closed"])

                if st.form_submit_button("Create Study"):
                    research.insert_one({
                        "title": title,
                        "description": description,
                        "researcher_email": email,
                        "data_types_required": data_types,
                        "status": status,
                        "participants": [],
                        "created_at": datetime.now()
                    })
                    st.success("Study created!")
                    st.rerun()

    # ───────────── MY PARTICIPATIONS ─────────────
    if role == "Patient":
        with st.expander("📋 My Research Participations"):

            my_studies = list(research.find({
                "participants": {"$elemMatch": {"patient_email": email}}
            }))

            if not my_studies:
                st.info("You are not enrolled in any studies.")

            for study in my_studies:
                st.write(f"📘 {study['title']} ({study['status']})")

                if st.button("Withdraw", key=f"wd_{study['_id']}"):
                    research.update_one(
                        {"_id": study["_id"]},
                        {"$pull": {"participants": {"patient_email": email}}}
                    )
                    st.warning("Withdrawn.")
                    st.rerun()

    # ───────────── OPEN STUDIES ─────────────
    st.subheader("Open Studies")

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Recruiting", "Active", "Closed"]
    )

    query = {} if status_filter == "All" else {"status": status_filter}
    studies = list(research.find(query))

    if not studies:
        st.info("No studies found.")

    for study in studies:
        with st.expander(
            f"📘 {study.get('title','Untitled')} [{study.get('status','?')}]"
        ):
            st.write(study.get("description", ""))

            st.write(
                f"**Data Required:** "
                f"{', '.join(study.get('data_types_required', []))}"
            )

            st.write(
                f"**Researcher:** {study.get('researcher_email','—')}"
            )

            if role == "Patient":

                anonymized = st.checkbox(
                    "Participate anonymously",
                    value=True,
                    key=f"anon_{study['_id']}"
                )

                if st.button("Enroll in Study", key=f"enroll_{study['_id']}"):

                    research.update_one(
                        {"_id": study["_id"]},
                        {"$push": {
                            "participants": {
                                "patient_email": email,
                                "anonymized": anonymized,
                                "joined_at": datetime.now()
                            }
                        }}
                    )

                    st.success("✅ Enrolled successfully!")
                    st.rerun()