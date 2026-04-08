from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

# ── Existing Schemas ──────────────────────────────────────────────────────────

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str

class MedicalRecord(BaseModel):
    patient_email: EmailStr
    doctor_email: EmailStr
    diagnosis: str
    treatment: str
    notes: Optional[str] = None

# ── Module 40: Consent & Privacy Schemas ─────────────────────────────────────

# Consent Types: Treatment | Research | Sharing | Marketing
# Permission Levels: Full | Limited | Anonymous | None

class ConsentCreate(BaseModel):
    patient_email: EmailStr
    data_type: str
    consent_type: Literal["Treatment", "Research", "Sharing", "Marketing"]
    permission_level: Literal["Full", "Limited", "Anonymous", "None"]
    expiry_date: Optional[datetime] = None   # Dynamic consent: optional expiry

class ConsentUpdate(BaseModel):
    consent_id: str
    permission_level: Literal["Full", "Limited", "Anonymous", "None"]
    expiry_date: Optional[datetime] = None

# Permission entity (granular per data field)
class PermissionCreate(BaseModel):
    patient_email: EmailStr
    resource: str          # e.g. "lab_results", "imaging", "prescriptions"
    granted_to: str        # email or role, e.g. "doctor@x.com" or "Researcher"
    level: Literal["Full", "Limited", "Anonymous", "None"]

# Research Study entity
class ResearchStudyCreate(BaseModel):
    title: str
    description: str
    researcher_email: EmailStr
    data_types_required: list[str]   # e.g. ["lab_results", "imaging"]
    status: Literal["Recruiting", "Active", "Closed"] = "Recruiting"

class ResearchParticipationCreate(BaseModel):
    patient_email: EmailStr
    study_id: str
    anonymized: bool = True          # True = Anonymous level participation

# Privacy Policy entity
class PrivacyPolicyCreate(BaseModel):
    version: str
    content: str
    effective_date: datetime
    created_by: EmailStr