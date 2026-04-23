from .database import collection, consents, db, research, privacy_policies, permissions
from datetime import datetime
from bson import ObjectId

# ── Existing Services ─────────────────────────────────────────────────────────

class UserService:
    @staticmethod
    def signup(email, password, name, role):
        user = collection.find_one({"email": email})
        if user:
            raise ValueError("Email already exists")
        collection.insert_one({"email": email, "password": password, "name": name, "role": role})
        return {"message": "Signup successful"}

    @staticmethod
    def login(email, password, role):
        user = collection.find_one({"email": email, "password": password, "role": role})
        if not user:
            raise ValueError("Invalid credentials")
        return {"email": email, "name": user["name"], "role": role}


class MedicalRecordService:
    @staticmethod
    def create(patient_email, doctor_email, diagnosis, treatment, notes=None):
        records_db = db["medical_records"]
        records_db.insert_one({
            "patient_email": patient_email,
            "doctor_email": doctor_email,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "notes": notes,
            "date_recorded": datetime.now()
        })
        return {"message": "Record created"}

    @staticmethod
    def get_patient_records(patient_email):
        records_db = db["medical_records"]
        if not ConsentService.check_access(patient_email, "medical_records"):
            raise ValueError("No consent")
        items = list(records_db.find({"patient_email": patient_email}))
        return [{"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}} for i in items]


# ── Module 40: Consent Service ────────────────────────────────────────────────

class ConsentService:
    @staticmethod
    def create(patient_email, data_type, consent_type, permission_level, expiry_date=None):
        """
        Create a new consent record.
        consent_type  : Treatment | Research | Sharing | Marketing
        permission_level: Full | Limited | Anonymous | None
        expiry_date   : optional datetime for dynamic/time-limited consent
        """
        consents.insert_one({
            "patient_email": patient_email,
            "data_type": data_type,
            "consent_type": consent_type,
            "permission_level": permission_level,
            "status": "active",
            "timestamp": datetime.now(),
            "expiry_date": expiry_date,
            "history": []           # audit trail
        })
        return {"message": "Consent created"}

    @staticmethod
    def get_consents(patient_email):
        items = list(consents.find({"patient_email": patient_email}))
        result = []
        for i in items:
            doc = {"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}}
            # auto-expire check
            expiry_date = doc.get("expiry_date")
            if expiry_date:
                if isinstance(expiry_date, str):
                    try:
                        expiry_date = datetime.fromisoformat(expiry_date)
                    except ValueError:
                        expiry_date = None
                if expiry_date and expiry_date < datetime.now():
                    consents.update_one({"_id": i["_id"]}, {"$set": {"status": "expired"}})
                    doc["status"] = "expired"
            result.append(doc)
        return result

    @staticmethod
    def check_access(patient_email, data_type):
        """Returns True only if an active, non-expired consent exists."""
        result = consents.find_one({
            "patient_email": patient_email,
            "data_type": data_type,
            "status": "active"
        })
        if not result:
            return False
            "if no consent acess is denined"
        expiry_date = result.get("expiry_date")
        if expiry_date:
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.fromisoformat(expiry_date)
                except ValueError:
                    expiry_date = None
            if expiry_date and expiry_date < datetime.now():
                consents.update_one({"_id": result["_id"]}, {"$set": {"status": "expired"}})
                return False
        return True

    @staticmethod
    def update(consent_id, permission_level, expiry_date=None):
        """Dynamic consent: update permission level or expiry."""
        old = consents.find_one({"_id": ObjectId(consent_id)})
        if not old:
            raise ValueError("Consent not found")
        # push old state to history for audit trail
        history_entry = {
            "permission_level": old["permission_level"],
            "status": old["status"],
            "changed_at": datetime.now()
        }
        consents.update_one(
            {"_id": ObjectId(consent_id)},
            {
                "$set": {"permission_level": permission_level, "expiry_date": expiry_date},
                "$push": {"history": history_entry}
            }
        )
        return {"message": "Consent updated"}

    @staticmethod
    def revoke(consent_id):
        old = consents.find_one({"_id": ObjectId(consent_id)})
        if old:
            history_entry = {
                "permission_level": old.get("permission_level"),
                "status": old.get("status"),
                "changed_at": datetime.now()
            }
            consents.update_one(
                {"_id": ObjectId(consent_id)},
                {"$set": {"status": "revoked"}, "$push": {"history": history_entry}}
            )
        return {"message": "Consent revoked"}

    @staticmethod
    def compliance_report(patient_email):
        """
        Compliance report: summary of all consent types and statuses for a patient.
        Useful for HIPAA / GDPR audit documentation.
        """
        all_consents = list(consents.find({"patient_email": patient_email}))
        report = {
            "patient_email": patient_email,
            "generated_at": datetime.now().isoformat(),
            "total": len(all_consents),
            "by_type": {},
            "by_status": {},
            "by_permission": {}
        }
        for c in all_consents:
            ct = c.get("consent_type", "Unknown")
            st = c.get("status", "Unknown")
            pl = c.get("permission_level", "Unknown")
            report["by_type"][ct] = report["by_type"].get(ct, 0) + 1
            report["by_status"][st] = report["by_status"].get(st, 0) + 1
            report["by_permission"][pl] = report["by_permission"].get(pl, 0) + 1
        return report


# ── Module 40: Permission Service (Granular Permissions) ─────────────────────

class PermissionService:
    @staticmethod
    def grant(patient_email, resource, granted_to, level):
        """
        Grant granular permission on a specific resource to a specific entity.
        e.g. grant "lab_results" to "doctor@x.com" at "Limited" level.
        """
        permissions.update_one(
            {"patient_email": patient_email, "resource": resource, "granted_to": granted_to},
            {"$set": {"level": level, "updated_at": datetime.now()},
             "$setOnInsert": {"created_at": datetime.now()}},
            upsert=True
        )
        return {"message": f"Permission '{level}' granted on '{resource}' to '{granted_to}'"}

    @staticmethod
    def check(patient_email, resource, granted_to):
        perm = permissions.find_one({
            "patient_email": patient_email,
            "resource": resource,
            "granted_to": granted_to
        })
        if not perm:
            return "None"
        return perm.get("level", "None")

    @staticmethod
    def get_all(patient_email):
        items = list(permissions.find({"patient_email": patient_email}))
        return [{"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}} for i in items]

    @staticmethod
    def revoke(patient_email, resource, granted_to):
        permissions.delete_one({
            "patient_email": patient_email,
            "resource": resource,
            "granted_to": granted_to
        })
        return {"message": "Permission revoked"}


# ── Module 40: Research Study Service ────────────────────────────────────────

class ResearchStudyService:
    @staticmethod
    def create(title, description, researcher_email, data_types_required, status="Recruiting"):
        research.insert_one({
            "title": title,
            "description": description,
            "researcher_email": researcher_email,
            "data_types_required": data_types_required,
            "status": status,
            "created_at": datetime.now(),
            "participants": []
        })
        return {"message": "Research study created"}

    @staticmethod
    def get_all(status_filter=None):
        query = {}
        if status_filter:
            query["status"] = status_filter
        items = list(research.find(query))
        return [{"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}} for i in items]

    @staticmethod
    def get_by_id(study_id):
        item = research.find_one({"_id": ObjectId(study_id)})
        if not item:
            raise ValueError("Study not found")
        return {"id": str(item["_id"]), **{k: v for k, v in item.items() if k != "_id"}}

    @staticmethod
    def enroll_patient(patient_email, study_id, anonymized=True):
        """
        Enroll a patient in a research study.
        Checks that the patient has a Research consent active before enrolling.
        anonymized=True → stores data without PII linkage (Anonymous permission level).
        """
        consents = list(db.consents.find({
            "patient_email": patient_email,
            "consent_type": "Research",
            "status": "active"
        }))

        if not consents:
            raise ValueError("No active research consent")

        study = research.find_one({"_id": ObjectId(study_id)})
        if not study:
            raise ValueError("Study not found")
        if study["status"] != "Recruiting":
            raise ValueError("Study is not recruiting")

        # Check research consent exists
        has_consent = ConsentService.check_access(patient_email, "research")
        if not has_consent:
            raise ValueError("Patient has no active Research consent for 'research' data type")

        # Check not already enrolled
        participations_db = db["research_participations"]
        existing = participations_db.find_one({
            "patient_email": patient_email,
            "study_id": study_id,
            "status": "active"
        })
        if existing:
            raise ValueError("Already enrolled")

        participations_db.insert_one({
            "patient_email": patient_email,
            "study_id": study_id,
            "anonymized": anonymized,
            "enrolled_at": datetime.now(),
            "status": "active"
        })
        research.update_one({"_id": ObjectId(study_id)}, {"$addToSet": {"participants": patient_email}})
        return {"message": "Enrolled in study"}

    @staticmethod
    def withdraw_patient(patient_email, study_id):
        participations_db = db["research_participations"]
        participations_db.update_one(
            {"patient_email": patient_email, "study_id": study_id},
            {"$set": {"status": "withdrawn", "withdrawn_at": datetime.now()}}
        )
        research.update_one({"_id": ObjectId(study_id)}, {"$pull": {"participants": patient_email}})
        return {"message": "Withdrawn from study"}

    @staticmethod
    def get_patient_participations(patient_email):
        participations_db = db["research_participations"]
        items = list(participations_db.find({"patient_email": patient_email}))
        return [{"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}} for i in items]

    @staticmethod
    def get_study_participants(study_id: str):
        participants = list(db.research_participations.find({
            "study_id": study_id
        }))

        result = []

        for p in participants:
            anonymized = p.get("anonymized", False)

            if anonymized:
                identity = "Anonymous Patient"
            else:
                identity = p.get("patient_email")

            result.append({
                "patient": identity,
                "anonymized": anonymized,
                "status": p.get("status", "active")
            })

        return result

# ── Module 40: Privacy Policy Service ────────────────────────────────────────

class PrivacyPolicyService:
    @staticmethod
    def create(version, content, effective_date, created_by):
        privacy_policies.insert_one({
            "version": version,
            "content": content,
            "effective_date": effective_date,
            "created_by": created_by,
            "created_at": datetime.now()
        })
        return {"message": f"Privacy policy v{version} created"}

    @staticmethod
    def get_latest():
        policy = privacy_policies.find_one(sort=[("effective_date", -1)])
        if not policy:
            return None
        return {"id": str(policy["_id"]), **{k: v for k, v in policy.items() if k != "_id"}}

    @staticmethod
    def get_all():
        items = list(privacy_policies.find().sort("effective_date", -1))
        return [{"id": str(i["_id"]), **{k: v for k, v in i.items() if k != "_id"}} for i in items]