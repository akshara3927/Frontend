"""
Module 40 – Research Studies View
Patients can browse open studies, enroll (with consent check), and withdraw.
Researchers/Admins can create new studies.
"""
import streamlit as st
import requests

BASE_URL = "http://localhost:8000"


def _fetch_studies(status=None):
    try:
        params = {"status": status} if status else {}
        r = requests.get(f"{BASE_URL}/research-studies", params=params, timeout=5)
        return r.json() if r.ok else []
    except Exception:
        return []


def research_studies_view():
    email = st.session_state.get("email", "")
    role = st.session_state.get("role", "Patient")

    st.header("🔬 Research Studies")

    # 🔴 IMPORTANT: ensure user logged in
    if not email:
        st.error("❌ Please login first")
        st.stop()

    # ───────────── CREATE STUDY (Doctor/Admin) ─────────────
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
                    payload = {
                        "title": title,
                        "description": description,
                        "researcher_email": email,
                        "data_types_required": data_types,
                        "status": status
                    }
                    try:
                        r = requests.post(f"{BASE_URL}/research-studies", json=payload, timeout=5)
                        if r.ok:
                            st.success("Study created!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(str(e))

    # ───────────── MY PARTICIPATIONS ─────────────
    if role == "Patient":
        with st.expander("📋 My Research Participations"):
            try:
                r = requests.get(
                    f"{BASE_URL}/research-studies/participations/{email}",
                    timeout=5
                )
                parts = r.json() if r.ok else []
            except Exception:
                parts = []

            if not parts:
                st.info("You are not enrolled in any studies.")

            for p in parts:
                status_icon = "🟢" if p.get("status") == "active" else "🔴"

                st.write(
                    f"{status_icon} Study ID: `{p.get('study_id')}` | "
                    f"Anonymized: {p.get('anonymized')} | Status: {p.get('status')}"
                )

                # Withdraw button
                if p.get("status") == "active":
                    if st.button("Withdraw", key=f"wd_{p['id']}"):
                        try:
                            requests.post(
                                f"{BASE_URL}/research-studies/withdraw",
                                json={
                                    "patient_email": email,
                                    "study_id": p["study_id"],
                                    "anonymized": True
                                },
                                timeout=5
                            )
                            st.warning("Withdrawn.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ───────────── OPEN STUDIES ─────────────
    st.subheader("Open Studies")

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Recruiting", "Active", "Closed"]
    )

    studies = _fetch_studies(None if status_filter == "All" else status_filter)

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

            # 🔥 ENROLL BUTTON (MAIN FIX)
            if role == "Patient":

                anonymized = st.checkbox(
                    "Participate anonymously (recommended)",
                    value=True,
                    key=f"anon_{study['id']}"
                )

                if st.button("Enroll in Study", key=f"enroll_{study['id']}"):

                    payload = {
                        "patient_email": email,
                        "study_id": study["id"],
                        "anonymized": anonymized
                    }

                    try:
                        r = requests.post(
                            f"{BASE_URL}/research-studies/enroll",
                            json=payload,
                            timeout=5
                        )

                        if r.ok:
                            st.success("✅ Enrolled successfully!")
                            st.rerun()   # 🔥 IMPORTANT
                        else:
                            st.error(r.text)

                    except Exception as e:
                        st.error(str(e))