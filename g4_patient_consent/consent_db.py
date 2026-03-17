from pymongo import MongoClient

DOCTOR_PASSCODE = "MEDICARE2024"

def get_client():
    return MongoClient("mongodb+srv://zustnithin_db_user:Criminal@cluster0.xflljxp.mongodb.net/?appName=Cluster0")

def get_patients_collection():
    return get_client()["patient_consent_db"]["patients"]

def get_doctors_collection():
    return get_client()["patient_consent_db"]["doctors"]

# ── Patient functions ──
def get_all_patients():
    return list(get_patients_collection().find())

def get_patient_by_id(patient_id):
    return get_patients_collection().find_one({"patient_id": patient_id})

def update_consent(patient_id, consent_value):
    get_patients_collection().update_one(
        {"patient_id": patient_id},
        {"$set": {"consent_given": consent_value}}
    )

def add_patient(patient_data):
    get_patients_collection().insert_one(patient_data)

def get_next_patient_id():
    count = get_patients_collection().count_documents({})
    return f"PT{str(count + 1).zfill(3)}"

# ── Doctor functions ──
def signup_doctor(name, email, password):
    doctors = get_doctors_collection()
    if doctors.find_one({"email": email}):
        return False, "Email already exists"
    doctors.insert_one({"name": name, "email": email, "password": password})
    return True, "Account created"

def login_doctor(email, password):
    doctors = get_doctors_collection()
    doc = doctors.find_one({"email": email, "password": password})
    if doc:
        return True, doc["name"]
    return False, "Invalid email or password"

def login_patient(patient_id, age):
    patient = get_patients_collection().find_one({"patient_id": patient_id, "age": int(age)})
    if patient:
        return True, patient["name"]
    return False, "Invalid Patient ID or Age"