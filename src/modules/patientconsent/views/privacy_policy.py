import streamlit as st
from database import privacy_policies


def privacy_policy_view():
    st.header("🔒 Privacy Policy")

    st.subheader("📜 Current Policy")

    # 🔹 Fetch latest policy from MongoDB
    policy = privacy_policies.find_one(sort=[("effective_date", -1)])

    if policy:
        st.markdown(f"""
### Version: {policy.get("version", "1.0")}
**Effective Date:** {policy.get("effective_date", "N/A")}

---

{policy.get("content", "")}
""")
    else:
        st.warning("No policy found. Showing default policy.")

        # 🔥 fallback default
        st.markdown("""
### Privacy Policy – MediCare

We respect and protect patient data. All personal and medical information is stored securely and accessed only through consent.

Data is used only for treatment and research (if approved). Users can control their data at any time.

By using this system, you agree to these terms.
""")

    st.divider()

    # ✅ acknowledgment
    agree = st.checkbox("I have read and agree to the privacy policy")

    if agree:
        st.success("✅ You have accepted the privacy policy")