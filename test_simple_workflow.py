#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'src')

from flask import Flask
from models.lead import db, Lead

# Create a simple Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("src/database/app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def test_simple_workflow(lead_id):
    """Simple workflow that just prints success without external services"""
    try:
        with app.app_context():
            lead = Lead.query.filter_by(lead_id=lead_id).first()
            if not lead:
                return {'error': 'Lead not found'}
            
            print(f"WORKFLOW: Processing lead {lead.first_name} {lead.last_name}")
            print(f"EMAIL: Sending follow-up email to {lead.email}")
            print(f"SHAREPOINT: Creating upload folder for {lead_id}")
            print(f"DOCUSIGN: Generating consent link for {lead.first_name}")
            
            # Update lead stage if it's inquiry
            if lead.stage == 'inquiry':
                lead.stage = 'docs_requested'
                db.session.commit()
                print(f"UPDATED: Lead stage changed to docs_requested")
            
            return {
                'status': 'success',
                'lead_id': lead_id,
                'message': 'Follow-up email sent successfully',
                'steps': [
                    {'step': 'email_sent', 'status': 'completed'},
                    {'step': 'upload_link_created', 'status': 'completed'},
                    {'step': 'consent_link_generated', 'status': 'completed'},
                    {'step': 'stage_updated', 'status': 'completed'}
                ]
            }
    except Exception as e:
        return {'error': f'Workflow error: {str(e)}'}

if __name__ == '__main__':
    # Test the workflow
    result = test_simple_workflow('984a67d6-a950-4173-b9d6-0905c8259533')
    print(f"Result: {result}")

