import os
import json
from datetime import datetime, timedelta

class SharePointService:
    def __init__(self):
        # SharePoint configuration (placeholder - would use real SharePoint API)
        self.sharepoint_site = os.getenv('SHAREPOINT_SITE', 'https://oasisofhealing.sharepoint.com')
        self.library_path = os.getenv('SHAREPOINT_LIBRARY', '/Admissions/Intake')
        self.client_id = os.getenv('SHAREPOINT_CLIENT_ID', 'client_id')
        self.client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET', 'client_secret')
    
    def create_upload_folder(self, lead_id):
        """Create a secure upload folder for a lead"""
        try:
            folder_path = f"{self.library_path}/{lead_id}"
            
            # In a real implementation, this would create the folder in SharePoint
            print(f"SHAREPOINT: Created folder {folder_path}")
            
            return {
                'folder_path': folder_path,
                'success': True
            }
        except Exception as e:
            print(f"Error creating SharePoint folder: {e}")
            return {
                'folder_path': None,
                'success': False,
                'error': str(e)
            }
    
    def generate_upload_link(self, lead_id, expires_hours=168):  # 7 days default
        """Generate a secure upload link for a lead"""
        try:
            # Create folder first
            folder_result = self.create_upload_folder(lead_id)
            if not folder_result['success']:
                return None
            
            # Generate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            
            # In a real implementation, this would generate a SharePoint "Request files" link
            upload_link = f"{self.sharepoint_site}/_layouts/15/upload.aspx?FolderCTID=0x012001&RootFolder={self.library_path}/{lead_id}&Source={self.sharepoint_site}"
            
            print(f"SHAREPOINT: Generated upload link for {lead_id}")
            print(f"LINK: {upload_link}")
            print(f"EXPIRES: {expires_at.isoformat()}")
            
            return {
                'upload_link': upload_link,
                'expires_utc': expires_at.isoformat(),
                'folder_path': folder_result['folder_path']
            }
        except Exception as e:
            print(f"Error generating upload link: {e}")
            return None
    
    def check_documents(self, lead_id):
        """Check what documents have been uploaded for a lead"""
        try:
            folder_path = f"{self.library_path}/{lead_id}"
            
            # In a real implementation, this would query SharePoint for files
            # For now, simulate document checking
            
            # Simulate some documents being present (for testing)
            # In reality, this would scan the SharePoint folder
            simulated_files = [
                'imaging_scan_2025.pdf',
                'lab_results_recent.pdf'
            ]
            
            # Map files to categories
            received_docs = []
            if any('imaging' in f.lower() or 'scan' in f.lower() or 'mri' in f.lower() or 'ct' in f.lower() for f in simulated_files):
                received_docs.append('imaging')
            if any('lab' in f.lower() for f in simulated_files):
                received_docs.append('labs')
            if any('pathology' in f.lower() or 'biopsy' in f.lower() for f in simulated_files):
                received_docs.append('pathology')
            if any('medication' in f.lower() or 'med_list' in f.lower() or 'drugs' in f.lower() for f in simulated_files):
                received_docs.append('med_list')
            if any('oncology' in f.lower() or 'notes' in f.lower() or 'report' in f.lower() for f in simulated_files):
                received_docs.append('prior_notes')
            
            # Calculate missing documents
            required_docs = ['imaging', 'pathology', 'labs', 'med_list', 'prior_notes']
            missing_docs = [doc for doc in required_docs if doc not in received_docs]
            
            print(f"SHAREPOINT: Checked documents for {lead_id}")
            print(f"RECEIVED: {received_docs}")
            print(f"MISSING: {missing_docs}")
            
            return {
                'received': received_docs,
                'missing': missing_docs,
                'files': simulated_files
            }
        except Exception as e:
            print(f"Error checking documents: {e}")
            return {
                'received': [],
                'missing': ['imaging', 'pathology', 'labs', 'med_list', 'prior_notes'],
                'files': []
            }
    
    def set_retention_policy(self, lead_id, retention_label="Admissions Intake - 1 year unless enrolled"):
        """Set retention policy on the lead's folder"""
        try:
            folder_path = f"{self.library_path}/{lead_id}"
            
            # In a real implementation, this would set the retention label in SharePoint
            print(f"SHAREPOINT: Set retention policy '{retention_label}' on {folder_path}")
            
            return True
        except Exception as e:
            print(f"Error setting retention policy: {e}")
            return False
    
    def get_audit_log(self, lead_id):
        """Get audit log for a lead's folder"""
        try:
            folder_path = f"{self.library_path}/{lead_id}"
            
            # In a real implementation, this would query SharePoint audit logs
            audit_entries = [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'action': 'folder_created',
                    'user': 'system',
                    'details': f'Created folder {folder_path}'
                }
            ]
            
            print(f"SHAREPOINT: Retrieved audit log for {lead_id}")
            
            return audit_entries
        except Exception as e:
            print(f"Error getting audit log: {e}")
            return []

# Global instance
sharepoint_service = SharePointService()

