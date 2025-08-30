import os
import hashlib
import hmac
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

class SecurityService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.phi_encryption_key = os.getenv('PHI_ENCRYPTION_KEY', 'phi-encryption-key')
        
        # HIPAA compliance settings
        self.hipaa_settings = {
            'require_consent_before_phi': True,
            'phi_in_email_forbidden': True,
            'phi_in_calendar_forbidden': True,
            'audit_all_phi_access': True,
            'data_retention_days': 365
        }
    
    def generate_token(self, user_id, role='staff'):
        """Generate JWT token for authentication"""
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
        except Exception as e:
            print(f"Error generating token: {e}")
            return None
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = self.verify_token(token)
            if 'error' in payload:
                return jsonify(payload), 401
            
            request.user = payload
            return f(*args, **kwargs)
        
        return decorated_function
    
    def check_consent_gate(self, lead):
        """Check if consent gate is satisfied before PHI operations"""
        if not self.hipaa_settings['require_consent_before_phi']:
            return True
        
        return lead.has_consent
    
    def validate_phi_request(self, lead, operation):
        """Validate PHI request against HIPAA rules"""
        validation_result = {
            'allowed': True,
            'violations': []
        }
        
        # Check consent gate
        if not self.check_consent_gate(lead):
            validation_result['allowed'] = False
            validation_result['violations'].append('Consent required before PHI access')
        
        # Check operation type
        if operation in ['email_phi', 'calendar_phi']:
            if self.hipaa_settings['phi_in_email_forbidden'] and operation == 'email_phi':
                validation_result['allowed'] = False
                validation_result['violations'].append('PHI in email is forbidden')
            
            if self.hipaa_settings['phi_in_calendar_forbidden'] and operation == 'calendar_phi':
                validation_result['allowed'] = False
                validation_result['violations'].append('PHI in calendar is forbidden')
        
        return validation_result
    
    def audit_phi_access(self, lead_id, user_id, operation, details=None):
        """Audit PHI access for compliance"""
        try:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'lead_id': lead_id,
                'user_id': user_id,
                'operation': operation,
                'details': details or {},
                'ip_address': request.remote_addr if request else 'system',
                'user_agent': request.headers.get('User-Agent') if request else 'system'
            }
            
            # In a real implementation, this would be stored in a secure audit database
            print(f"PHI AUDIT: {audit_entry}")
            
            return audit_entry
        except Exception as e:
            print(f"Error creating audit entry: {e}")
            return None
    
    def encrypt_phi_data(self, data):
        """Encrypt PHI data for storage"""
        try:
            # In a real implementation, this would use proper encryption
            # For demo purposes, we'll use a simple hash
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = str(data).encode('utf-8')
            
            encrypted = hashlib.sha256(data_bytes + self.phi_encryption_key.encode()).hexdigest()
            return f"ENCRYPTED:{encrypted}"
        except Exception as e:
            print(f"Error encrypting PHI data: {e}")
            return data
    
    def decrypt_phi_data(self, encrypted_data):
        """Decrypt PHI data for use"""
        try:
            if isinstance(encrypted_data, str) and encrypted_data.startswith('ENCRYPTED:'):
                # In a real implementation, this would properly decrypt
                # For demo, we'll return a placeholder
                return "[DECRYPTED PHI DATA]"
            return encrypted_data
        except Exception as e:
            print(f"Error decrypting PHI data: {e}")
            return encrypted_data
    
    def validate_webhook_signature(self, payload, signature, secret):
        """Validate webhook signature for security"""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            print(f"Error validating webhook signature: {e}")
            return False
    
    def sanitize_log_data(self, data):
        """Sanitize data for logging to prevent PHI exposure"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['ssn', 'dob', 'medical_record', 'diagnosis', 'treatment']:
                    sanitized[key] = '[REDACTED]'
                elif isinstance(value, dict):
                    sanitized[key] = self.sanitize_log_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        return data
    
    def check_data_retention(self, lead):
        """Check if lead data should be retained or purged"""
        try:
            if not lead.last_touch_iso:
                return {'action': 'retain', 'reason': 'No last touch date'}
            
            last_touch = datetime.fromisoformat(lead.last_touch_iso.replace('Z', '+00:00'))
            days_since_touch = (datetime.utcnow() - last_touch).days
            
            if days_since_touch > self.hipaa_settings['data_retention_days']:
                # Check if patient is enrolled (would prevent deletion)
                if lead.stage == 'decision':
                    return {'action': 'retain', 'reason': 'Patient enrolled'}
                else:
                    return {'action': 'purge', 'reason': f'Retention period exceeded ({days_since_touch} days)'}
            
            return {'action': 'retain', 'reason': f'Within retention period ({days_since_touch} days)'}
            
        except Exception as e:
            return {'action': 'retain', 'reason': f'Error checking retention: {e}'}
    
    def generate_compliance_report(self):
        """Generate HIPAA compliance report"""
        try:
            from src.models.lead import Lead
            
            total_leads = Lead.query.count()
            consented_leads = Lead.query.filter_by(has_consent=True).count()
            
            report = {
                'report_date': datetime.utcnow().isoformat(),
                'total_leads': total_leads,
                'consented_leads': consented_leads,
                'consent_compliance_rate': (consented_leads / total_leads * 100) if total_leads > 0 else 0,
                'hipaa_settings': self.hipaa_settings,
                'violations': [],  # Would track any violations
                'audit_entries_count': 0  # Would count audit entries
            }
            
            # Check for potential violations
            non_consented = total_leads - consented_leads
            if non_consented > 0:
                report['violations'].append({
                    'type': 'missing_consent',
                    'count': non_consented,
                    'description': 'Leads without proper consent on file'
                })
            
            return report
            
        except Exception as e:
            return {'error': f'Error generating compliance report: {e}'}

# Global instance
security_service = SecurityService()

