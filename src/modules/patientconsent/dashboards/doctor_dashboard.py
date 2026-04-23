# dashboards/doctor_dashboard.py
import requests
import streamlit as st
from src.modules.patientconsent.components.sidebar import sidebar
from src.modules.patientconsent.components.charts import patient_line_chart, appointment_donut_chart
import matplotlib.pyplot as plt
from src.modules.patientconsent.database import consents

BASE_URL = "http://localhost:8000"

# All categories and their modules
CATEGORIES = {
    "A - Patient Clinical Data": {
        "title": "Patient Clinical Data Management",
        "description": "Patient records, medical history, diagnoses, and treatment plans",
        "icon": "🏥",
        "stats": {"modules": "6", "records": "45,230", "alerts": "12"},
        "modules": [
            ("A1", "Patient Demographics & Visit History", "Patient demographics and admission data", 5, 12500),
            ("A2", "Chronic Disease Patient Record", "Past medical records and conditions", 4, 8900),
            ("A3", "Pediatric Patient Clinical Data", "ICD codes and diagnosis tracking", 3, 15600),
            ("A4", "Geriatric Patient Health Record", "Care plans and treatment", 6, 7800),
            ("A5", "Patient Allergy & Immunization", "Patient vitals and monitoring", 4, 9200),
            ("A6", "Clinical Alert System", "Doctor notes and observations", 5, 11400)
        ]
    },
    "B - Laboratory Management": {
        "title": "Laboratory Management",
        "description": "Lab tests, results, equipment, and sample tracking",
        "icon": "🧪",
        "stats": {"modules": "5", "records": "12,840", "alerts": "5"},
        "modules": [
            ("B1", "Laboratory Test Management", "Test ordering system", 9, 22300),
            ("B2", "Automated Lab Result Interpretation", "AI result analysis", 6, 15800),
            ("B3", "Reference Range Validation", "Normal range database", 4, 12400),
            ("B4", "Follow-Up Test Recommendation", "Test suggestion system", 5, 9100),
            ("B5", "Pathology Report Management", "Pathology database", 7, 11200)
        ]
    },
    "C - Pharmacy & Medications": {
        "title": "Pharmacy & Medications",
        "description": "Drug inventory, prescriptions, and dispensing records",
        "icon": "💊",
        "stats": {"modules": "6", "records": "28,450", "alerts": "3"},
        "modules": [
            ("C1", "Drug-Drug Interaction Alert", "Interaction database", 7, 18500),
            ("C2", "Prescription Validation System", "Consistency checks", 5, 12300),
            ("C3", "Allergy-Aware Medication Alert", "Allergy cross-reference", 4, 9800),
            ("C4", "Polypharmacy Risk Detection", "Multiple drug analysis", 6, 11200),
            ("C5", "High-Risk Drug Monitoring", "Critical medication tracking", 5, 8700),
            ("C6", "Automated Prescription Audit", "Prescription review system", 4, 7300)
        ]
    },
    "D - Hospital Operations": {
        "title": "Hospital Operations",
        "description": "Bed management, admissions, and facility operations",
        "icon": "🏥",
        "stats": {"modules": "6", "records": "34,120", "alerts": "8"},
        "modules": [
            ("D1", "Bed Management System", "Bed allocation and tracking", 5, 8900),
            ("D2", "Patient Admission & Discharge", "Admission workflows", 7, 12400),
            ("D3", "Operating Room Scheduling", "OR booking system", 6, 5600),
            ("D4", "Emergency Department Triage", "ED patient management", 8, 4200),
            ("D5", "Ward Management System", "Ward operations", 5, 2100),
            ("D6", "Hospital Facility Management", "Facility tracking", 4, 920)
        ]
    },
    "E - Billing & Insurance": {
        "title": "Billing & Insurance",
        "description": "Patient billing, insurance claims, and payment processing",
        "icon": "💳",
        "stats": {"modules": "5", "records": "18,760", "alerts": "6"},
        "modules": [
            ("E1", "Patient Billing System", "Invoice generation", 8, 15600),
            ("E2", "Insurance Claims Management", "Claims processing", 6, 12300),
            ("E3", "Payment Processing", "Payment tracking", 5, 9800),
            ("E4", "Revenue Cycle Management", "Financial analytics", 7, 8900),
            ("E5", "Pricing & Tariff Management", "Price management", 4, 4160)
        ]
    },
    "F - HR & Staff Management": {
        "title": "HR & Staff Management",
        "description": "Employee records, scheduling, and performance tracking",
        "icon": "👥",
        "stats": {"modules": "5", "records": "5,240", "alerts": "2"},
        "modules": [
            ("F1", "Doctor & Staff Registry", "Employee database", 6, 2400),
            ("F2", "Shift Scheduling System", "Staff scheduling", 5, 8900),
            ("F3", "Attendance & Leave Management", "Time tracking", 4, 12100),
            ("F4", "Performance Evaluation", "Staff reviews", 3, 1800),
            ("F5", "Training & Certification", "Credential tracking", 4, 940)
        ]
    },
    "G - Compliance & Security": {
        "title": "Compliance & Security",
        "description": "Regulatory compliance, auditing, and data security",
        "icon": "🔒",
        "stats": {"modules": "4", "records": "156,300", "alerts": "1"},
        "modules": [
            ("G1", "Secure Electronic Health Record", "Main EHR database", 12, 45000),
            ("G2", "Role-Based Access Control", "Permission management", 8, 28900),
            ("G3", "Clinical Audit Trail & Logging", "Activity logging system", 6, 32100),
            ("G4", "Patient Consent & Privacy", "Privacy management", 5, 18700)
        ]
    },
    "H - Supply Chain": {
        "title": "Supply Chain & Inventory",
        "description": "Medical supplies, equipment, and vendor management",
        "icon": "📦",
        "stats": {"modules": "5", "records": "42,180", "alerts": "9"},
        "modules": [
            ("H1", "Medical Equipment Tracking", "Equipment inventory", 7, 12400),
            ("H2", "Supply Inventory Management", "Stock management", 8, 18900),
            ("H3", "Vendor & Procurement", "Supplier management", 5, 3200),
            ("H4", "Equipment Maintenance", "Maintenance schedules", 4, 5400),
            ("H5", "Pharmacy Inventory", "Drug stock tracking", 6, 2280)
        ]
    },
    "I - Analytics & Reporting": {
        "title": "Analytics & Reporting",
        "description": "Data analytics, KPIs, and business intelligence",
        "icon": "📊",
        "stats": {"modules": "4", "records": "125,600", "alerts": "4"},
        "modules": [
            ("I1", "Hospital Performance Dashboard", "KPI tracking and metrics", 15, 78900),
            ("I2", "Clinical Outcomes Analysis", "Treatment effectiveness", 12, 46700),
            ("I3", "Financial Analytics", "Revenue and cost analysis", 10, 32100),
            ("I4", "Predictive Analytics", "AI-powered predictions", 18, 18900)
        ]
    }
}

def doctor_dashboard():
    st.session_state.setdefault("view", "main")
    st.session_state.setdefault("selected_category", None)
    st.session_state.setdefault("selected_module", None)

    # Sidebar - but don't automatically trigger category view
    selected = sidebar([
        "Dashboard",
        "A - Patient Clinical Data",
        "B - Laboratory Management",
        "C - Pharmacy & Medications",
        "D - Hospital Operations",
        "E - Billing & Insurance",
        "F - HR & Staff Management",
        "G - Compliance & Security",
        "H - Supply Chain",
        "I - Analytics & Reporting"
    ])

    # Only change view if a category is explicitly selected AND it's not "Dashboard"
    if selected != "Dashboard" and selected in CATEGORIES and st.session_state.view == "main":
        # Don't auto-navigate, let button clicks handle it
        pass

    # ROUTER
    if st.session_state.view == "category":
        show_category_view()
    elif st.session_state.view == "module":
        show_module_detail()
    else:
        show_main_dashboard()

def show_main_dashboard():
    st.markdown("### Welcome back! Here's your hospital overview.")
    
    st.divider()

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Patients", "12,450", "+12% vs last month")
    c2.metric("⚠️ Active Alerts", "320", "-5% vs last month")
    c3.metric("📋 Lab Reports", "185", "+8% vs last month")
    c4.metric("💊 Prescriptions", "750", "+15% vs last month")

    st.divider()

    # Main content area
    main_col, side_col = st.columns([2, 1])
    
    with main_col:
        st.subheader("Your Patients Today")
        st.markdown("[All patients →](#)")
        
        # Patient 1 - Highlighted
        with st.container():
            p_col1, p_col2, p_col3 = st.columns([1, 5, 1])
            with p_col1:
                st.markdown("🕐 **10:30am**")
            with p_col2:
                st.markdown("**SH | Sarah Hostern**")
                st.caption("Diagnosis: Bronchi")
            with p_col3:
                st.button("📍", key="loc1")
                st.button("⋮", key="menu1")
        
        st.success("Currently Active")
        st.markdown("---")
        
        # Patient 2
        with st.container():
            p_col1, p_col2, p_col3 = st.columns([1, 5, 1])
            with p_col1:
                st.markdown("🕐 **11:00am**")
            with p_col2:
                st.markdown("**DS | Dakota Smith**")
                st.caption("Diagnosis: Stroke")
            with p_col3:
                st.button("📹", key="video1")
                st.button("⋮", key="menu2")
        
        st.markdown("---")
        
        # Patient 3
        with st.container():
            p_col1, p_col2, p_col3 = st.columns([1, 5, 1])
            with p_col1:
                st.markdown("🕐 **11:30am**")
            with p_col2:
                st.markdown("**JL | John Lane**")
                st.caption("Diagnosis: Liver")
            with p_col3:
                st.button("📞", key="call1")
                st.button("⋮", key="menu3")
        
        st.markdown("---")
        
        # Patient 4
        with st.container():
            p_col1, p_col2, p_col3 = st.columns([1, 5, 1])
            with p_col1:
                st.markdown("🕐 **12:00pm**")
            with p_col2:
                st.markdown("**MG | Maria Garcia**")
                st.caption("Diagnosis: Cardiac")
            with p_col3:
                st.button("📍", key="loc2")
                st.button("⋮", key="menu4")
        
        st.divider()
        
        # Charts section
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### Patient Analytics")
            patient_line_chart()
        
        with chart_col2:
            st.markdown("### Appointments Overview")
            appointment_donut_chart()
    
    with side_col:
        st.subheader("Recent Activity")
        st.markdown("[View All](#)")
        
        # Activity 1
        st.markdown("👤 **New patient registration: John Smith**")
        st.caption("🕐 2 min ago • Reception")
        st.markdown("---")
        
        # Activity 2
        st.markdown("⚠️ **Critical lab result for Patient #4521**")
        st.caption("🕐 5 min ago • Lab")
        st.markdown("---")
        
        # Activity 3
        st.markdown("✅ **Surgery completed successfully - Room 5**")
        st.caption("🕐 12 min ago • Dr. Wilson")
        st.markdown("---")
        
        # Activity 4
        st.markdown("📊 **Monthly analytics report generated**")
        st.caption("🕐 25 min ago • System")
        st.markdown("---")
        
        # Activity 5
        st.markdown("👤 **Patient discharge: Emily Brown**")
        st.caption("🕐 1 hour ago • Ward B")
    
    st.divider()
    
    # System Categories Section
    st.markdown("## System Categories (A-I)")
    
    cols = st.columns(3)
    for idx, (key, cat) in enumerate(CATEGORIES.items()):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {cat['icon']} {key}")
                st.caption(cat['description'])
                
                stat_cols = st.columns([1, 2, 1])
                with stat_cols[0]:
                    st.metric("Modules", cat['stats']['modules'])
                with stat_cols[1]:
                    st.metric("Records", cat['stats']['records'])
                with stat_cols[2]:
                    st.markdown(f"⚠️ {cat['stats']['alerts']}")
                    st.caption("Alerts")
                
                if st.button("View Details →", key=f"cat_{idx}", use_container_width=True):
                    st.session_state.selected_category = key
                    st.session_state.view = "category"
                    st.rerun()
                st.markdown("---")

def show_category_view():
    cat_key = st.session_state.selected_category
    category = CATEGORIES[cat_key]
    
    # Header with icon and title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# {category['icon']} {category['title']}")
        st.markdown(f"*{category['description']}*")
    with col2:
        st.button("📄 Export Data", use_container_width=True)
    
    st.divider()
    
    # Stats cards
    stats = category['stats']
    c1, c2, c3 = st.columns(3)
    c1.metric("⚡ Modules", stats['modules'])
    c2.metric("📊 Total Records", stats['records'])
    c3.metric("⚠️ Active Alerts", stats['alerts'])
    
    st.divider()
    st.markdown("## Modules")
    
    # Module cards in grid
    cols = st.columns(3)
    for idx, module in enumerate(category['modules']):
        code, name, desc, tables, records = module
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {code}")
                st.markdown(f"**{name}**")
                st.caption(desc)
                
                mcol1, mcol2 = st.columns(2)
                mcol1.metric("Tables", tables)
                mcol2.metric("Records", f"{records:,}")
                
                if st.button("→", key=f"mod_{code}", use_container_width=True):
                    st.session_state.selected_module = module
                    st.session_state.view = "module"
                    st.rerun()
                st.markdown("---")
    
    st.divider()
    if st.button("⬅ Back to Dashboard"):
        st.session_state.view = "main"
        st.rerun()

def show_module_detail():
    code, name, desc, tables, records = st.session_state.selected_module
    cat_key = st.session_state.selected_category

    # Breadcrumb
    st.markdown(f"Category {cat_key.split('-')[0].strip()} > {name}")
    st.markdown(f"# {name}")
    st.markdown(f"*{desc}*")

    # Tabs
    if code == "G4":
        tabs = st.tabs([
            "🔐 Patient Access Control",
            "🔬 Research Studies",
            "👥 Study Participants"
        ])

        # ───────────── TAB 1: ACCESS CONTROL ─────────────
        with tabs[0]:
            st.subheader("Patient Consent Access Control")

            patient_email = st.text_input("Enter Patient Email")

            if st.button("Check Access"):
                if not patient_email or not patient_email.strip():
                    st.error("Enter email")
                else:
                    try:
                        consents_list = requests.get(
                            f"{BASE_URL}/consents/{patient_email.strip()}"
                        ).json()

                        if not consents_list:
                            st.warning("No consent found ❌")
                        else:
                            st.subheader("📄 Consents")

                            active = []

                            for c in consents_list:
                                st.write(
                                    f"- {c['consent_type']} | "
                                    f"{c['permission_level']} | "
                                    f"{c['status']}"
                                )

                                if c["status"] == "active":
                                    active.append(c)

                            if not active:
                                st.error("🚫 Access Denied")
                            else:
                                st.success("✅ Access Allowed")

                                for c in active:
                                    if c["permission_level"] == "Anonymous":
                                        st.warning("⚠ Anonymous data only")
                                    elif c["permission_level"] == "Limited":
                                        st.info("ℹ Limited access")
                                    elif c["permission_level"] == "Full":
                                        st.success("✔ Full access")

                    except Exception as e:
                        st.error(str(e))

        # ───────────── TAB 2: CREATE + VIEW STUDIES ─────────────
        with tabs[1]:
            st.subheader("Create Research Study")

            with st.form("create_study"):
                title = st.text_input("Title")
                description = st.text_area("Description")
                data_types = st.multiselect(
                    "Data Required",
                    ["medical_records", "lab_results", "imaging", "prescriptions"]
                )
                status = st.selectbox("Status", ["Recruiting", "Active", "Closed"])

                if st.form_submit_button("Create Study"):
                    payload = {
                        "title": title,
                        "description": description,
                        "researcher_email": st.session_state.get("email"),
                        "data_types_required": data_types,
                        "status": status
                    }

                    r = requests.post(f"{BASE_URL}/research-studies", json=payload)

                    if r.ok:
                        st.success("Study created!")
                        st.rerun()
                    else:
                        st.error(r.text)

            st.divider()

            st.subheader("All Studies")

            try:
                studies = requests.get(f"{BASE_URL}/research-studies").json()
            except Exception as e:
                studies = []
                st.error(str(e))

            for s in studies:
                with st.expander(f"{s['title']} [{s['status']}]"):
                    st.write(s["description"])
                    st.write(f"Data: {', '.join(s.get('data_types_required', []))}")

        # ───────────── TAB 3: STUDY PARTICIPANTS ─────────────
        with tabs[2]:
            st.subheader("View Study Participants")

            try:
                studies = requests.get(f"{BASE_URL}/research-studies").json()
            except Exception as e:
                studies = []
                st.error(str(e))

            study_map = {s["title"]: s["id"] for s in studies}

            if not study_map:
                st.info("No studies available")
            else:
                selected = st.selectbox("Select Study", list(study_map.keys()))
                study_id = study_map[selected]

                if st.button("View Participants"):
                    try:
                        r = requests.get(
                            f"{BASE_URL}/research-studies/participants/{study_id}"
                        )

                        data = r.json()

                        # 🔥 DEBUG
                        st.write("DEBUG:", data)

                        if not isinstance(data, list):
                            st.error("Invalid response from backend")
                        elif not data:
                            st.info("No participants yet")
                        else:
                            for p in data:
                                name = p.get("patient")
                                anonymized = p.get("anonymized")
                                status = p.get("status")

                                # 🎨 badges
                                status_color = "green" if status == "active" else "red"
                                privacy_label = "🔒 Anonymous" if anonymized else "👤 Identified"

                                st.markdown(f"""
                                <div style="
                                    padding:15px;
                                    border-radius:12px;
                                    border:1px solid #333;
                                    margin-bottom:10px;
                                    background-color:#111;
                                ">
                                    <h4 style="margin:0;">{name}</h4>

                                    <p style="margin:5px 0;">
                                        <span style="
                                            background-color:{status_color};
                                            padding:3px 8px;
                                            border-radius:6px;
                                            font-size:12px;
                                            color:white;
                                        ">
                                            {status.upper()}
                                        </span>

                                        &nbsp;

                                        <span style="
                                            background-color:#444;
                                            padding:3px 8px;
                                            border-radius:6px;
                                            font-size:12px;
                                            color:white;
                                        ">
                                            {privacy_label}
                                        </span>
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(str(e))
    else:
        tab = st.radio("", ["🏠 Home", "🔗 ER Diagram", "📋 Tables", "🔍 SQL Query", "⚡ Triggers", "📊 Output"], horizontal=True)
        st.divider()

        if tab == "🏠 Home":
            st.info(f"**{name}** - {desc}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Input Entities")
                st.success("1️⃣ Patient Form")
                st.success("2️⃣ Insurance Details")
                st.success("3️⃣ Emergency Contact")

            with col2:
                st.markdown("### Output Entities")
                st.success("1️⃣ Patient Record")
                st.success("2️⃣ Admission Summary")
                st.success("3️⃣ Patient ID")

        elif tab == "🔗 ER Diagram":
            st.info("ER diagram placeholder")
        elif tab == "📋 Tables":
            st.info("Table schema placeholder")
        elif tab == "🔍 SQL Query":
            st.info("SQL query builder placeholder")
        elif tab == "⚡ Triggers":
            st.info("Trigger logic placeholder")
        elif tab == "📊 Output":
            st.info("Output preview placeholder")

        # Research Consents Section
        st.divider()
        st.subheader("🔬 Research Study Consents")

        research_consents = list(consents.find({"consent_type": "research"}))

        if research_consents:
            for rc in research_consents:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Patient:** {rc.get('patient_email')}")
                        st.caption(f"Data Type: {rc.get('data_type')} | Study: {rc.get('study', 'Not Applicable')}")
                    with col2:
                        if rc.get("status") == "active":
                            st.success("Active")
                        else:
                            st.error("Revoked")
                    st.divider()
        else:
            st.info("No research consents found")

    if st.button("⬅ Back to Modules"):
        st.session_state.view = "category"
        st.rerun()
