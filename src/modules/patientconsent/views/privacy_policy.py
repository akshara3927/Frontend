import streamlit as st
import requests

BASE_URL = "http://localhost:8000"


def privacy_policy_view():
    st.header("🔒 Privacy Policy")

    st.subheader("📜 Current Policy")

    try:
        r = requests.get(f"{BASE_URL}/privacy-policies/latest", timeout=5)

        if r.ok:
            policy = r.json()

            st.markdown(f"""
### Version: {policy.get("version", "1.0")}
**Effective Date:** {policy.get("effective_date", "N/A")}

---

We respect and protect patient data. All personal and medical information is stored securely and accessed only through patient consent.

Data is used for treatment, authorized sharing, and research participation. Patients can grant or revoke consent at any time.

For research, data may be anonymized to protect identity. No data is shared without permission.

By using this system, you agree to this policy.
""")

        else:
            st.warning("No policy found in backend. Showing default policy.")

            # 🔥 fallback default
            st.markdown("""
### Privacy Policy – MediCare

We respect and protect patient data. All personal and medical information is stored securely and accessed only through consent.

Data is used only for treatment and research (if approved). Users can control their data at any time.

By using this system, you agree to these terms.
""")

    except Exception:
        st.warning("Backend not reachable. Showing default policy.")

        # 🔥 fallback default
        st.markdown("""
### Privacy Policy – MediCare

We respect and protect patient data. All personal and medical information is stored securely and accessed only through consent.

Data is used only for treatment and research (if approved). Users can control their data at any time.

By using this system, you agree to these terms.
""")

    st.divider()

    # ✅ simple acknowledgment
    agree = st.checkbox("I have read and agree to the privacy policy")

    if agree:
        st.success("✅ You have accepted the privacy policy")