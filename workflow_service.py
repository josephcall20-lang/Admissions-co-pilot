from datetime import datetime, timedelta
from src.models.lead import db, Lead
from src.services.notification_service import notification_service
from src.services.sharepoint_service import sharepoint_service
from src.services.esign_service import esign_service

class WorkflowService:
    def __init__(self):
        self.workflows = {
            'F1_WebLead': self.process_web_lead,
            'F2_PhoneLead': self.process_phone_lead
        }
    
    def process_web_lead(self, lead_id):
        """Process F1 - Website Lead workflow"""
        try:
            lead = Lead.query.filter_by(lead_id=lead_id).first()
            if not lead:
                return {'error': 'Lead not found'}
            
            workflow_steps = []
            
            # Step 1: Lead already created by CreateOrUpdateLead API
            workflow_steps.append({
                'step': 'create_lead',
                'status': 'completed',
                'timestamp': lead.last_touch_iso
            })
            
            # Step 2: Issue document request and generate consent link
            if lead.stage == 'inquiry':
                # Generate upload link
                upload_result = sharepoint_service.generate_upload_link(lead_id)
                if upload_result:
                    # Generate consent link
                    lead_data = {
                        'first_name': lead.first_name,
                        'last_name': lead.last_name,
                        'email': lead.email,
                        'phone': lead.phone,
                        'relationship': lead.relationship
                    }
                    
                    consent_link = esign_service.generate_consent_link(lead_data)
                    
                    # Send initial email with both links
                    notification_sent = notification_service.send_secure_upload_and_consent(
                        lead_data, 
                        upload_result['upload_link'], 
