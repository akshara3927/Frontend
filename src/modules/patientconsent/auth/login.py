import streamlit as st
from database import users

def login_page():
    st.title("🏥 MediCare Login")

    role = st.selectbox("Login as", ["Patient", "Doctor", "Admin"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = users.find_one({"email": email})

        if user and user["password"] == password:

            if user["role"] == role:

                st.session_state.logged_in = True
                st.session_state.role = role   
                st.session_state.user = user 
                st.session_state.page = "dashboard"
                st.session_state["email"] = email

                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Selected role does not match your account")

        else:
            st.error("Invalid email or password")

    st.markdown("Don't have an account?")
    if st.button("Signup"):
        st.session_state.page = "signup"
        st.rerun()