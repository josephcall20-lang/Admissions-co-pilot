#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.lead import db, Lead
from flask import Flask
import uuid
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    # Drop all tables and recreate
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating fresh tables...")
    db.create_all()
    
    # Add a single test lead
    print("Adding test lead...")
    test_lead = Lead(
        lead_id=str(uuid.uuid4()),
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="555-000-0000",
        timezone="America/Phoenix",
        relationship="self",
        stage="inquiry",
        required_docs='["imaging", "pathology", "labs", "med_list", "prior_notes"]',
        received_docs='[]',
        missing_docs='["imaging", "pathology", "labs", "med_list", "prior_notes"]',
        owner_user_id="admissions_staff",
        last_touch_iso=datetime.utcnow().isoformat(),
        idempotency_key="test_user_key"
    )
    
    db.session.add(test_lead)
    db.session.commit()
    
    print(f"Database reset complete! Test lead created with ID: {test_lead.lead_id}")
    
    # Verify the lead exists
    all_leads = Lead.query.all()
    print(f"Total leads in database: {len(all_leads)}")
    for lead in all_leads:
        print(f"- {lead.first_name} {lead.last_name} ({lead.lead_id})")

