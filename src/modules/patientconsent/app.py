
# ── Streamlit Entry Point ───────────────────────────────────────────────────

import streamlit as st
from modules.patientconsent.auth.login import login_page
from modules.patientconsent.auth.signup import signup_page
from modules.patientconsent.dashboards.patient_dashboard import patient_dashboard
from modules.patientconsent.dashboards.doctor_dashboard import doctor_dashboard
from modules.patientconsent.dashboards.admin_dashboard import admin_dashboard

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MediCare", layout="wide")

# ---------------- SESSION STATE INIT ----------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("page", "login")
st.session_state.setdefault("role", None)

# ---------------- HARD REDIRECT AFTER LOGIN ----------------
if st.session_state.logged_in:
    if st.session_state.role == "Patient":
        patient_dashboard()
        st.stop()
    elif st.session_state.role == "Doctor":
        doctor_dashboard()
        st.stop()
    elif st.session_state.role == "Admin":
        admin_dashboard()
        st.stop()

# ---------------- AUTH ROUTING ----------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()