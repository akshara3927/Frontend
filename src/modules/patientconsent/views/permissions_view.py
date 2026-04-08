"""
Module 40 – Granular Permissions View
Lets patients control exactly which resource each doctor/researcher can access.
"""
import streamlit as st
import requests

BASE_URL = "http://localhost:8000"
PERMISSION_LEVELS = ["Full", "Limited", "Anonymous", "None"]
RESOURCES = ["medical_records", "lab_results", "imaging", "prescriptions",
             "personal_data", "billing", "research_data"]


def permissions_view():
    email = st.session_state.get("email", "")
    st.header("🔑 Granular Data Permissions")
    st.caption("Control exactly who can access which part of your health data.")

    tabs = st.tabs(["Current Permissions", "Grant Permission"])

    # ── Tab 1: Current Permissions ────────────────────────────────────────────
    with tabs[0]:
        try:
            r = requests.get(f"{BASE_URL}/permissions/{email}", timeout=5)
            perms = r.json() if r.ok else []
        except Exception:
            perms = []

        if not perms:
            st.info("No granular permissions set. Use 'Grant Permission' to add one.")
        else:
            for p in perms:
                with st.expander(f"{p.get('resource','?')} → {p.get('granted_to','?')} [{p.get('level','?')}]"):
                    col1, col2 = st.columns(2)
                    col1.write(f"**Resource:** {p.get('resource')}")
                    col1.write(f"**Granted to:** {p.get('granted_to')}")
                    col2.write(f"**Level:** {p.get('level')}")
                    if col2.button("Revoke", key=f"rperm_{p['id']}"):
                        try:
                            requests.delete(
                                f"{BASE_URL}/permissions/{email}/revoke",
                                params={"resource": p["resource"], "granted_to": p["granted_to"]},
                                timeout=5
                            )
                            st.warning("Permission revoked.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ── Tab 2: Grant Permission ───────────────────────────────────────────────
    with tabs[1]:
        with st.form("grant_perm_form"):
            resource   = st.selectbox("Resource / Data Type", RESOURCES)
            granted_to = st.text_input("Grant to (email or role, e.g. doctor@x.com)")
            level      = st.selectbox("Permission Level", PERMISSION_LEVELS)
            if st.form_submit_button("Grant"):
                if not granted_to:
                    st.warning("Please enter a recipient.")
                else:
                    payload = {
                        "patient_email": email,
                        "resource": resource,
                        "granted_to": granted_to,
                        "level": level
                    }
                    try:
                        r = requests.post(f"{BASE_URL}/permissions", json=payload, timeout=5)
                        if r.ok:
                            st.success(f"'{level}' permission granted on '{resource}' to '{granted_to}'")
                        else:
                            st.error(r.json().get("detail", "Error"))
                    except Exception as e:
                        st.error(str(e))