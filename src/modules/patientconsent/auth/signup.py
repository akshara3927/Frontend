import streamlit as st
from database import users

def signup_page():
    st.title("Create Account")

    role = st.selectbox("Signup as", ["Patient", "Doctor"])
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):

        existing_user = users.find_one({"email": email})

        if existing_user:
            st.error("User already exists")
        else:
            users.insert_one({
                "name": name,
                "email": email,
                "password": password,
                "role": role
            })

            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()