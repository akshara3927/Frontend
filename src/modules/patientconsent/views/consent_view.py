"""
Module 40 – Consent Management View
"""
import streamlit as st
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

CONSENT_TYPES = ["Treatment", "Research", "Sharing", "Marketing"]
PERMISSION_LEVELS = ["Full", "Limited", "Anonymous", "None"]
DATA_TYPES = [
    "medical_records", "lab_results", "imaging",
    "prescriptions", "research", "personal_data", "billing"
]


def _fetch_consents(email):
    try:
        r = requests.get(f"{BASE_URL}/consents/{email}", timeout=5)
        return r.json() if r.ok else []
    except Exception:
        return []


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

        consents = _fetch_consents(email)

        if not consents:
            st.info("No consents found.")

        for c in consents:
            with st.expander(
                f"{c.get('consent_type','?')} › {c.get('data_type','?')} — {_status_badge(c.get('status',''))}"
            ):
                col1, col2 = st.columns(2)

                col1.write(f"**Permission Level:** {c.get('permission_level','—')}")
                col2.write(f"**Granted:** {str(c.get('timestamp','—'))[:16]}")

                if c.get("expiry_date"):
                    st.write(f"**Expires:** {str(c['expiry_date'])[:16]}")

                if c.get("status") == "active":
                    col_a, col_b = st.columns(2)

                    new_level = col_a.selectbox(
                        "Update Permission Level",
                        PERMISSION_LEVELS,
                        index=PERMISSION_LEVELS.index(
                            c.get("permission_level", "Full")
                        ),
                        key=f"upd_{c['id']}"
                    )

                    if col_a.button("Update", key=f"upd_btn_{c['id']}"):
                        try:
                            r = requests.put(
                                f"{BASE_URL}/consents/update",
                                json={
                                    "consent_id": c["id"],
                                    "permission_level": new_level
                                },
                                timeout=5
                            )
                            st.success("Updated!" if r.ok else "Error")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

                    if col_b.button("Revoke", key=f"rev_{c['id']}", type="primary"):
                        try:
                            requests.post(
                                f"{BASE_URL}/consents/{c['id']}/revoke",
                                timeout=5
                            )
                            st.warning("Consent revoked.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ───────────── TAB 2: GRANT CONSENT ─────────────
    with tabs[1]:
        st.subheader("Grant a New Consent")

        with st.form("new_consent_form"):

            # 🔥 IMPORTANT FIX: use session email ONLY
            patient_email = email
            st.write(f"Patient Email: {email}")

            data_type = st.selectbox("Data Type", DATA_TYPES)
            consent_type = st.selectbox("Consent Type", CONSENT_TYPES)
            permission_lvl = st.selectbox("Permission Level", PERMISSION_LEVELS)

            use_expiry = st.checkbox("Set expiry date (Dynamic Consent)")
            expiry_date = None

            if use_expiry:
                days = st.number_input(
                    "Expires in (days)",
                    min_value=1,
                    max_value=3650,
                    value=365
                )
                expiry_date = (
                    datetime.now() + timedelta(days=int(days))
                ).isoformat()

            submitted = st.form_submit_button("Grant Consent")

            if submitted:
                payload = {
                    "patient_email": patient_email,
                    "data_type": data_type,
                    "consent_type": consent_type,
                    "permission_level": permission_lvl,
                    "expiry_date": expiry_date
                }

                try:
                    r = requests.post(
                        f"{BASE_URL}/consents",
                        json=payload,
                        timeout=5
                    )
                    if r.ok:
                        st.success("Consent granted successfully!")
                        st.rerun()   # 🔥 refresh → now visible in Tab 1
                    else:
                        st.error(r.text)
                except Exception as e:
                    st.error(str(e))

    # ───────────── TAB 3: COMPLIANCE REPORT ─────────────
    with tabs[2]:
        st.subheader("Privacy Compliance Report")

        if st.button("Generate Report"):
            try:
                r = requests.get(
                    f"{BASE_URL}/consents/{email}/compliance-report",
                    timeout=5
                )

                if r.ok:
                    report = r.json()

                    st.write(f"**Generated at:** {report.get('generated_at','')}")
                    st.write(f"**Total consents:** {report.get('total', 0)}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write("**By Type**")
                        for k, v in report.get("by_type", {}).items():
                            st.write(f"- {k}: {v}")

                    with col2:
                        st.write("**By Status**")
                        for k, v in report.get("by_status", {}).items():
                            st.write(f"- {k}: {v}")

                    with col3:
                        st.write("**By Permission Level**")
                        for k, v in report.get("by_permission", {}).items():
                            st.write(f"- {k}: {v}")

                else:
                    st.error("Could not fetch report")

            except Exception as e:
                st.error(str(e))