import streamlit as st
from g4_patient_consent.consent_db import signup_doctor

def signup_page():
    st.title("MediCare")
    st.subheader("Create Doctor Account")
    st.divider()

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not name or not email or not password:
            st.error("Please fill in all fields")
        elif password != confirm:
            st.error("Passwords do not match")
        else:
            success, msg = signup_doctor(name, email, password)
            if success:
                st.success("Account created! Please login.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(msg)

    st.divider()
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()