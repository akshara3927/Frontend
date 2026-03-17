import streamlit as st
from g4_patient_consent.consent_db import get_patient_by_id

def show_consent_page():
    role = st.session_state.get("role", None)

    st.title("🔒 G4 - Patient Consent & Data Privacy")
    st.divider()

    if role == "Patient":
        patient_id = st.session_state.get("patient_id", None)
        patient = get_patient_by_id(patient_id)

        if not patient:
            st.error("No record found for your account.")
            return

        st.success(f"Welcome, {patient['name']}!")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🆔 Patient ID:** {patient['patient_id']}")
            st.markdown(f"**👤 Name:** {patient['name']}")
            st.markdown(f"**🎂 Age:** {patient['age']}")
            st.markdown(f"**🩺 Doctor:** {patient['doctor']}")
        with col2:
            st.markdown(f"**🏥 Diagnosis:** {patient['diagnosis']}")
            st.markdown(f"**📏 Height:** {patient.get('height', 'N/A')} cm")
            st.markdown(f"**⚖️ Weight:** {patient.get('weight', 'N/A')} kg")
            st.markdown(f"**📊 BMI:** {patient.get('bmi', 'N/A')}")

        st.divider()
        st.markdown("### 🔐 Your Consent Status")
        consent = patient.get("consent_given", False)
        if consent:
            st.success("✅ You have allowed access to your records.")
        else:
            st.warning("❌ You have not allowed access to your records.")

    elif role == "Doctor":
        show_doctor_view()

    elif role == "Admin":
        show_admin_view()

    else:
        st.error("You are not authorized to view this page.")


def show_doctor_view():
    from g4_patient_consent.consent_db import get_all_patients, update_consent, add_patient, get_next_patient_id

    if "g4_view" not in st.session_state:
        st.session_state.g4_view = "menu"
    if "privacy_agreed" not in st.session_state:
        st.session_state.privacy_agreed = False

    if st.session_state.g4_view == "menu":
        st.subheader("Welcome to Patient Consent Management")
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
            st.warning("⚠️ Agree to Privacy Policy before viewing records.")
            st.markdown("""
1. **Confidentiality** — All data is strictly confidential.
2. **Purpose Limitation** — Use only for authorized medical purposes.
3. **No Sharing** — Do not share with unauthorized parties.
4. **Consent Respect** — Respect patient consent decisions.
5. **Audit Compliance** — All access is logged.
6. **Legal Liability** — Unauthorized use is a legal offense.
            """)
            agreed = st.checkbox("I agree to the Privacy Policy")
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
            patients = get_all_patients()
            st.subheader("📋 Patient Records")
            if st.button("⬅ Back"):
                st.session_state.g4_view = "menu"
                st.session_state.privacy_agreed = False
                st.rerun()
            st.divider()
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
                            st.write(f"**BMI:** {p.get('bmi', 'N/A')}")
                else:
                    st.warning(f"🔒 {p['patient_id']} — Access Denied (No Consent)")

    elif st.session_state.g4_view == "add":
        st.subheader("➕ Add New Patient Record")
        if st.button("⬅ Back"):
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
                cat = "Underweight"
            elif bmi < 25:
                cat = "Normal"
            elif bmi < 30:
                cat = "Overweight"
            else:
                cat = "Obese"
            st.success(f"📊 BMI: **{bmi}** — {cat}")
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
                st.success(f"✅ {name} saved! ID: {next_id}")
            else:
                st.error("Fill in all fields.")


def show_admin_view():
    from g4_patient_consent.consent_db import get_all_patients, update_consent
    patients = get_all_patients()
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
                st.write(f"**BMI:** {p.get('bmi', 'N/A')}")
            st.write(f"**Consent:** {'✅ Yes' if p['consent_given'] else '❌ No'}")
            new_consent = st.toggle("Toggle Consent", value=p['consent_given'], key=p['patient_id'])
            if new_consent != p['consent_given']:
                update_consent(p['patient_id'], new_consent)
                st.success("Updated!")
                st.rerun()