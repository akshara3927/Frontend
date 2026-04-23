from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    UserCreate, UserLogin, MedicalRecord,
    ConsentCreate, ConsentUpdate,
    PermissionCreate,
    ResearchStudyCreate, ResearchParticipationCreate,
    PrivacyPolicyCreate
)
from .services import (
    UserService, MedicalRecordService,
    ConsentService, PermissionService,
    ResearchStudyService, PrivacyPolicyService
)

app = FastAPI(title="MediCare API – Module 40: Patient Consent & Data Privacy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok"}

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/signup")
def signup(user: UserCreate):
    try:
        return UserService.signup(user.email, user.password, user.name, user.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: UserLogin):
    try:
        return UserService.login(user.email, user.password, user.role)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# ── Medical Records ───────────────────────────────────────────────────────────

@app.post("/medical-records")
def create_record(record: MedicalRecord):
    return MedicalRecordService.create(
        record.patient_email, record.doctor_email,
        record.diagnosis, record.treatment, record.notes
    )

@app.get("/medical-records/{patient_email}")
def get_records(patient_email: str):
    try:
        return MedicalRecordService.get_patient_records(patient_email)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

# ── Consents ──────────────────────────────────────────────────────────────────

@app.post("/consents")
def create_consent(consent: ConsentCreate):
    return ConsentService.create(
        consent.patient_email, consent.data_type,
        consent.consent_type, consent.permission_level,
        consent.expiry_date
    )

@app.get("/consents/{patient_email}")
def get_consents(patient_email: str):
    return ConsentService.get_consents(patient_email)

@app.put("/consents/update")
def update_consent(data: ConsentUpdate):
    try:
        return ConsentService.update(data.consent_id, data.permission_level, data.expiry_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/consents/{consent_id}/revoke")
def revoke_consent(consent_id: str):
    return ConsentService.revoke(consent_id)

@app.get("/consents/{patient_email}/compliance-report")
def compliance_report(patient_email: str):
    return ConsentService.compliance_report(patient_email)

# ── Permissions (Granular) ────────────────────────────────────────────────────

@app.post("/permissions")
def grant_permission(perm: PermissionCreate):
    return PermissionService.grant(
        perm.patient_email, perm.resource, perm.granted_to, perm.level
    )

@app.get("/permissions/{patient_email}")
def get_permissions(patient_email: str):
    return PermissionService.get_all(patient_email)

@app.get("/permissions/{patient_email}/check")
def check_permission(patient_email: str, resource: str, granted_to: str):
    level = PermissionService.check(patient_email, resource, granted_to)
    return {"patient_email": patient_email, "resource": resource, "granted_to": granted_to, "level": level}

@app.delete("/permissions/{patient_email}/revoke")
def revoke_permission(patient_email: str, resource: str, granted_to: str):
    return PermissionService.revoke(patient_email, resource, granted_to)

# ── Research Studies ──────────────────────────────────────────────────────────

@app.post("/research-studies")
def create_study(study: ResearchStudyCreate):
    return ResearchStudyService.create(
        study.title, study.description, study.researcher_email,
        study.data_types_required, study.status
    )

@app.get("/research-studies")
def list_studies(status: str = None):
    return ResearchStudyService.get_all(status_filter=status)

@app.get("/research-studies/{study_id}")
def get_study(study_id: str):
    try:
        return ResearchStudyService.get_by_id(study_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/research-studies/enroll")
def enroll(data: ResearchParticipationCreate):
    try:
        return ResearchStudyService.enroll_patient(
            data.patient_email, data.study_id, data.anonymized
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/research-studies/withdraw")
def withdraw(data: ResearchParticipationCreate):
    return ResearchStudyService.withdraw_patient(data.patient_email, data.study_id)

@app.get("/research-studies/participations/{patient_email}")
def patient_participations(patient_email: str):
    return ResearchStudyService.get_patient_participations(patient_email)

# ── Study Participants (NEW) ───────────────────────────────────────────

@app.get("/research-studies/participants/{study_id}")
def get_study_participants(study_id: str):
    try:
        return ResearchStudyService.get_study_participants(study_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── Privacy Policies ──────────────────────────────────────────────────────────

@app.post("/privacy-policies")
def create_policy(policy: PrivacyPolicyCreate):
    return PrivacyPolicyService.create(
        policy.version, policy.content, policy.effective_date, policy.created_by
    )

@app.get("/privacy-policies")
def list_policies():
    return PrivacyPolicyService.get_all()

@app.get("/privacy-policies/latest")
def latest_policy():
    policy = PrivacyPolicyService.get_latest()
    if not policy:
        raise HTTPException(status_code=404, detail="No privacy policy found")
    return policy