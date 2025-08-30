from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lead(db.Model):
    lead_id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    timezone = db.Column(db.String, default='America/Phoenix')
    relationship = db.Column(db.String)
    stage = db.Column(db.String, nullable=False)
    has_consent = db.Column(db.Boolean, default=False)
    consent_type = db.Column(db.String)
    consent_version = db.Column(db.String)
    consent_timestamp = db.Column(db.String)
    required_docs = db.Column(db.String)
    received_docs = db.Column(db.String)
    missing_docs = db.Column(db.String)
    ehr_patient_id = db.Column(db.String)
    owner_user_id = db.Column(db.String)
    last_touch_iso = db.Column(db.String)
    idempotency_key = db.Column(db.String, unique=True)


