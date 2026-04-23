"""
Module 40 – Consent Management View (Streamlit + MongoDB)
"""
import streamlit as st
from datetime import datetime, timedelta
from src.modules.patientconsent.database import consents

CONSENT_TYPES = ["Treatment", "Research", "Sharing", "Marketing"]
PERMISSION_LEVELS = ["Full", "Limited", "Anonymous", "None"]
DATA_TYPES = [
    "medical_records", "lab_results", "imaging",
    "prescriptions", "research", "personal_data", "billing"
]


def _status_badge(status):
    colors = {"active": "🟢", "revoked": "🔴", "expired": "🟡"}
    return colors.get(status, "⚪") + f" {status.capitalize()}"


def consent_management_view():
    email = st.session_state.get("email", "")

    st.header("🔐 Consent Management")
    st.write(f"Logged in as: {email}")

    tabs = st.tabs(["My Consents", "Grant New Consent", "Compliance Report"])

    # ───────────── TAB 1: VIEW CONSENTS ─────────────
    with tabs[0]:
        st.subheader("Active & Past Consents")

        consents_list = list(consents.find({"patient_email": email}))

        if not consents_list:
            st.info("No consents found.")

        for c in consents_list:
            status = c.get("status", "active")

            with st.expander(
                f"{c.get('consent_type','?')} › {c.get('data_type','?')} — {_status_badge(status)}"
            ):
                col1, col2 = st.columns(2)

                col1.write(f"**Permission Level:** {c.get('permission_level','—')}")
                col2.write(f"**Granted:** {str(c.get('timestamp','—'))[:16]}")

                if c.get("expiry_date"):
                    st.write(f"**Expires:** {str(c['expiry_date'])[:16]}")

                if status == "active":
                    col_a, col_b = st.columns(2)

                    new_level = col_a.selectbox(
                        "Update Permission Level",
                        PERMISSION_LEVELS,
                        index=PERMISSION_LEVELS.index(
                            c.get("permission_level", "Full")
                        ),
                        key=f"upd_{c['_id']}"
                    )

                    if col_a.button("Update", key=f"upd_btn_{c['_id']}"):
                        consents.update_one(
                            {"_id": c["_id"]},
                            {"$set": {"permission_level": new_level}}
                        )
                        st.success("Updated!")
                        st.rerun()

                    if col_b.button("Revoke", key=f"rev_{c['_id']}", type="primary"):
                        consents.update_one(
                            {"_id": c["_id"]},
                            {"$set": {"status": "revoked"}}
                        )
                        st.warning("Consent revoked.")
                        st.rerun()

    # ───────────── TAB 2: GRANT CONSENT ─────────────
    with tabs[1]:
        st.subheader("Grant a New Consent")

        with st.form("new_consent_form"):

            st.write(f"Patient Email: {email}")

            data_type = st.selectbox("Data Type", DATA_TYPES)
            consent_type = st.selectbox("Consent Type", CONSENT_TYPES)
            permission_lvl = st.selectbox("Permission Level", PERMISSION_LEVELS)

            use_expiry = st.checkbox("Set expiry date")
            expiry_date = None

            if use_expiry:
                days = st.number_input("Expires in (days)", 1, 3650, 365)
                expiry_date = datetime.now() + timedelta(days=int(days))

            submitted = st.form_submit_button("Grant Consent")

            if submitted:
                consents.insert_one({
                    "patient_email": email,
                    "data_type": data_type,
                    "consent_type": consent_type,
                    "permission_level": permission_lvl,
                    "expiry_date": expiry_date,
                    "timestamp": datetime.now(),
                    "status": "active"
                })

                st.success("Consent granted successfully!")
                st.rerun()

    # ───────────── TAB 3: REPORT ─────────────
    with tabs[2]:
        st.subheader("Privacy Compliance Report")

        if st.button("Generate Report"):

            data = list(consents.find({"patient_email": email}))

            total = len(data)

            by_type = {}
            by_status = {}
            by_permission = {}

            for c in data:
                by_type[c["consent_type"]] = by_type.get(c["consent_type"], 0) + 1
                by_status[c.get("status", "active")] = by_status.get(c.get("status", "active"), 0) + 1
                by_permission[c["permission_level"]] = by_permission.get(c["permission_level"], 0) + 1

            st.write(f"**Total consents:** {total}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**By Type**")
                for k, v in by_type.items():
                    st.write(f"- {k}: {v}")

            with col2:
                st.write("**By Status**")
                for k, v in by_status.items():
                    st.write(f"- {k}: {v}")

            with col3:
                st.write("**By Permission Level**")
                for k, v in by_permission.items():
                    st.write(f"- {k}: {v}")