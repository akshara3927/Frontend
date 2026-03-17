import streamlit as st
from g4_patient_consent.consent_db import get_all_patients, update_consent, add_patient, get_next_patient_id

def show_consent_page():
    role = st.session_state.get("role", None)
    st.title("🔒 G4 - Patient Consent & Data Privacy")
    st.divider()

    if "g4_view" not in st.session_state:
        st.session_state.g4_view = "menu"
    if "privacy_agreed" not in st.session_state:
        st.session_state.privacy_agreed = False

    if st.session_state.g4_view == "menu":
        st.subheader("Welcome to Patient Consent Management")
        st.markdown("Manage patient consent records securely and efficiently.")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Record", use_container_width=True):
                st.session_state.g4_view = "add"
                st.rerun()
        with col2:
            if st.button("📋 View Records", use_container_width=True):
                st.session_state.g4_view = "privacy"
                st.rerun()

    elif st.session_state.g4_view == "privacy":
        if not st.session_state.privacy_agreed:
            st.warning("⚠️ You must agree to the Privacy Policy before viewing patient records.")
            st.markdown("""
### 📋 Privacy Policy & Terms of Access

By accessing this module, you agree to the following:

1. **Confidentiality** — All patient data viewed here is strictly confidential.
2. **Purpose Limitation** — Data may only be used for authorized medical purposes.
3. **No Sharing** — Patient information must not be shared with unauthorized parties.
4. **Consent Respect** — You must respect patient consent decisions at all times.
5. **Audit Compliance** — All access is logged and may be audited.
6. **Legal Liability** — Unauthorized use of patient data is a legal offense.
            """)
            agreed = st.checkbox("I have read and agree to the Privacy Policy and Terms of Access")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Proceed", disabled=not agreed):
                    st.session_state.privacy_agreed = True
                    st.rerun()
            with col2:
                if st.button("⬅ Back"):
                    st.session_state.g4_view = "menu"
                    st.rerun()
        else:
            show_records(role)

    elif st.session_state.g4_view == "add":
        show_add_record()


def show_records(role):
    patients = get_all_patients()
    st.subheader("📋 Patient Consent Records")

    if st.button("⬅ Back to Menu"):
        st.session_state.g4_view = "menu"
        st.session_state.privacy_agreed = False
        st.rerun()

    st.divider()

    if role == "Admin":
        st.success("✅ Admin View — Full Access")
        for p in patients:
            with st.expander(f"{p['patient_id']} — {p['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Age:** {p['age']}")
                    st.write(f"**Doctor:** {p['doctor']}")
                    st.write(f"**Diagnosis:** {p['diagnosis']}")
                with col2:
                    st.write(f"**Height:** {p.get('height', 'N/A')} cm")
                    st.write(f"**Weight:** {p.get('weight', 'N/A')} kg")
                    if p.get('bmi'):
                        st.write(f"**BMI:** {p['bmi']}")
                st.write(f"**Consent:** {'✅ Yes' if p['consent_given'] else '❌ No'}")
                new_consent = st.toggle("Toggle Consent", value=p['consent_given'], key=p['patient_id'])
                if new_consent != p['consent_given']:
                    update_consent(p['patient_id'], new_consent)
                    st.success("Updated!")
                    st.rerun()

    elif role == "Doctor":
        st.info("🩺 Doctor View — Showing only consented patients")
        for p in patients:
            if p['consent_given']:
                with st.expander(f"{p['patient_id']} — {p['name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Age:** {p['age']}")
                        st.write(f"**Doctor:** {p['doctor']}")
                        st.write(f"**Diagnosis:** {p['diagnosis']}")
                    with col2:
                        st.write(f"**Height:** {p.get('height', 'N/A')} cm")
                        st.write(f"**Weight:** {p.get('weight', 'N/A')} kg")
                        if p.get('bmi'):
                            st.write(f"**BMI:** {p['bmi']}")
            else:
                st.warning(f"🔒 {p['patient_id']} — Access Denied (No Consent)")

    elif role == "Patient":
        st.info("👤 Patient View — Manage your own consent")
        for p in patients:
            with st.expander(f"{p['patient_id']} — {p['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Age:** {p['age']}")
                    st.write(f"**Doctor:** {p['doctor']}")
                    st.write(f"**Diagnosis:** {p['diagnosis']}")
                with col2:
                    st.write(f"**Height:** {p.get('height', 'N/A')} cm")
                    st.write(f"**Weight:** {p.get('weight', 'N/A')} kg")
                    if p.get('bmi'):
                        st.write(f"**BMI:** {p['bmi']}")
                new_consent = st.toggle("Allow access to my records", value=p['consent_given'], key=p['patient_id'])
                if new_consent != p['consent_given']:
                    update_consent(p['patient_id'], new_consent)
                    st.success("Consent updated!")
                    st.rerun()

    else:
        st.error("❌ You are not authorized to view this page.")


def show_add_record():
    st.subheader("➕ Add New Patient Record")

    if st.button("⬅ Back to Menu"):
        st.session_state.g4_view = "menu"
        st.rerun()

    st.divider()

    next_id = get_next_patient_id()
    st.info(f"🆔 Auto-generated Patient ID: **{next_id}**")

    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=25)
    doctor = st.text_input("Doctor Name")
    diagnosis = st.text_input("Diagnosis")

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0)
    with col2:
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)

    if height > 0 and weight > 0:
        bmi = round(weight / ((height / 100) ** 2), 2)
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        st.success(f"📊 BMI: **{bmi}** — {category}")
    else:
        bmi = None

    consent = st.radio("Consent Given?", ["Yes", "No"])

    if st.button("💾 Save Record"):
        if name and doctor and diagnosis:
            add_patient({
                "patient_id": next_id,
                "name": name,
                "age": int(age),
                "doctor": doctor,
                "diagnosis": diagnosis,
                "height": height,
                "weight": weight,
                "bmi": bmi,
                "consent_given": consent == "Yes"
            })
            st.success(f"✅ Record for {name} saved! Patient ID: {next_id}")
        else:
            st.error("Please fill in all fields.")