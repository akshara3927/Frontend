import streamlit as st
from g4_patient_consent.consent_db import login_doctor, login_patient, DOCTOR_PASSCODE

def login_page():
    st.title("MediCare")
    st.divider()

    if "login_role" not in st.session_state:
        st.session_state.login_role = None

    if st.session_state.login_role is None:
        st.markdown("### Login as:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Patient", use_container_width=True):
                st.session_state.login_role = "Patient"
                st.rerun()
        with col2:
            if st.button("Doctor", use_container_width=True):
                st.session_state.login_role = "Doctor"
                st.rerun()
        with col3:
            if st.button("Admin", use_container_width=True):
                st.session_state.login_role = "Admin"
                st.rerun()
        return

    role = st.session_state.login_role

    if st.button("Back"):
        st.session_state.login_role = None
        st.rerun()

    st.divider()

    if role == "Patient":
        st.markdown("### Patient Login")
        patient_id = st.text_input("Patient ID (e.g. PT001)")
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
        if st.button("Login", key="patient_login"):
            success, result = login_patient(patient_id, age)
            if success:
                st.session_state.logged_in = True
                st.session_state.role = "Patient"
                st.session_state.patient_id = patient_id
                st.session_state.patient_name = result
                st.session_state.login_role = None
                st.rerun()
            else:
                st.error("Patient not found. Check your Patient ID or Age.")

    elif role == "Doctor":
        st.markdown("### Doctor Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        passcode = st.text_input("Doctor Passcode", type="password")
        if st.button("Login", key="doctor_login"):
            if passcode != DOCTOR_PASSCODE:
                st.error("Invalid Doctor Passcode")
            else:
                success, result = login_doctor(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.role = "Doctor"
                    st.session_state.doctor_name = result
                    st.session_state.login_role = None
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        st.divider()
        st.markdown("Don't have an account?")
        if st.button("Sign Up as Doctor"):
            st.session_state.page = "signup"
            st.session_state.login_role = None
            st.rerun()

    elif role == "Admin":
        st.markdown("### Admin Login")
        user_id = st.text_input("User ID")
        passcode = st.text_input("Passcode", type="password")
        if st.button("Login", key="admin_login"):
            if user_id == "admin" and passcode == DOCTOR_PASSCODE:
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.session_state.login_role = None
                st.rerun()
            else:
                st.error("Invalid credentials")