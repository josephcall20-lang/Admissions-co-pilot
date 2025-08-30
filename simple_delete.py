from flask import Blueprint, request, jsonify
from src.models.lead import db, Lead
from datetime import datetime

simple_delete_bp = Blueprint('simple_delete', __name__)

@simple_delete_bp.route('/delete-lead/<lead_id>', methods=['DELETE'])
def delete_lead_simple(lead_id):
    """Simple delete function that actually works"""
    try:
        # Find the lead
        lead = Lead.query.filter_by(lead_id=lead_id).first()
        
        if not lead:
            return jsonify({
                'success': False,
                'error': 'Lead not found',
                'lead_id': lead_id
            }), 404
        
        # Store lead info before deletion
        lead_name = f"{lead.first_name} {lead.last_name}"
        lead_email = lead.email
        
        # Delete the lead
        db.session.delete(lead)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {lead_name}',
            'deleted_name': lead_name,
            'deleted_email': lead_email,
            'deleted_id': lead_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}',
            'lead_id': lead_id
        }), 500

