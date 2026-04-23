import streamlit as st
from src.modules.patientconsent.database import collection

def signup_page():
    st.title("Create Account")

    role = st.selectbox("Signup as", ["Patient", "Doctor"])
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):

        existing_user = collection.find_one({"email": email})

        if existing_user:
            st.error("User already exists")
        else:
            collection.insert_one({
                "name": name,
                "email": email,
                "password": password,
                "role": role   # ✅ store EXACT same (Patient/Doctor)
            })

            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()