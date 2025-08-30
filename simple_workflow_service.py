from datetime import datetime
from src.models.lead import db, Lead

class SimpleWorkflowService:
    def __init__(self):
        self.workflows = {
            'F1_WebLead': self.process_web_lead,
            'F2_PhoneLead': self.process_phone_lead
        }
    
    def process_web_lead(self, lead_id):
        """Process F1 - Website Lead workflow (simplified version)"""
        try:
            lead = Lead.query.filter_by(lead_id=lead_id).first()
            if not lead:
                return {'error': 'Lead not found'}
            
            workflow_steps = []
            
            # Step 1: Send follow-up email (simulated)
            print(f"WORKFLOW: Processing lead {lead.first_name} {lead.last_name}")
            print(f"EMAIL: Sending follow-up email to {lead.email}")
            workflow_steps.append({
                'step': 'email_sent',
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat(),
                'details': f'Follow-up email sent to {lead.email}'
            })
            
            # Step 2: Create SharePoint upload folder (simulated)
            print(f"SHAREPOINT: Creating upload folder for {lead_id}")
            upload_link = f"https://oasisofhealing.sharepoint.com/upload/{lead_id}"
            workflow_steps.append({
                'step': 'upload_link_created',
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat(),
                'details': f'Upload link created: {upload_link}'
            })
            
            # Step 3: Generate consent link (simulated)
            print(f"DOCUSIGN: Generating consent link for {lead.first_name}")
            consent_link = f"https://docusign.com/consent/{lead_id}"
            workflow_steps.append({
                'step': 'consent_link_generated',
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat(),
                'details': f'Consent link generated: {consent_link}'
            })
            
            # Step 4: Update lead stage if needed
            if lead.stage == 'inquiry':
                lead.stage = 'docs_requested'
                lead.last_touch_iso = datetime.utcnow().isoformat()
                db.session.commit()
                print(f"UPDATED: Lead stage changed to docs_requested")
                workflow_steps.append({
                    'step': 'stage_updated',
                    'status': 'completed',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': 'Lead stage updated to docs_requested'
                })
            else:
                workflow_steps.append({
                    'step': 'stage_check',
                    'status': 'completed',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': f'Lead already in {lead.stage} stage'
                })
            
            return {
                'status': 'success',
                'lead_id': lead_id,
                'message': 'Follow-up email workflow completed successfully',
                'current_stage': lead.stage,
                'steps': workflow_steps,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Workflow error: {str(e)}")
            return {'error': f'Workflow error: {str(e)}'}
    
    def process_phone_lead(self, lead_id):
        """Process F2 - Phone Lead workflow (placeholder)"""
        return {
            'status': 'success',
            'lead_id': lead_id,
            'message': 'Phone lead workflow not implemented yet',
            'steps': []
        }

# Create a global instance
simple_workflow_service = SimpleWorkflowService()

