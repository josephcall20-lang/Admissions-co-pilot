from flask import Blueprint, request, jsonify, current_app
from src.services.simple_workflow_service import simple_workflow_service
from datetime import datetime

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/workflows/<workflow_type>/<lead_id>', methods=['POST'])
def trigger_workflow(workflow_type, lead_id):
    """Trigger a specific workflow for a lead"""
    try:
        if workflow_type not in ['F1_WebLead', 'F2_PhoneLead']:
            return jsonify({'error': 'Invalid workflow type'}), 400
        
        result = simple_workflow_service.workflows[workflow_type](lead_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Workflow error: {str(e)}'}), 500

@workflow_bp.route('/workflows/consent/webhook', methods=['POST'])
def consent_webhook():
    """Handle consent completion webhooks from e-sign provider"""
    try:
        data = request.get_json()
        
        envelope_id = data.get('envelope_id')
        status = data.get('status')
        
        if not envelope_id or not status:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Process the webhook
        result = workflow_service.process_consent_webhook(envelope_id, status)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflows/maintenance/daily', methods=['POST'])
def run_daily_maintenance():
    """Run daily maintenance tasks"""
    try:
        result = workflow_service.run_daily_maintenance()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflows/status/<lead_id>', methods=['GET'])
def get_workflow_status(lead_id):
    """Get the current workflow status for a lead"""
    try:
        # Run the workflow to get current status
        result = workflow_service.process_web_lead(lead_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'lead_id': lead_id,
            'current_stage': result['current_stage'],
            'workflow_steps': result['steps'],
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflows/reminders/send', methods=['POST'])
def send_reminders():
    """Manually trigger reminder sending for all eligible leads"""
    try:
        from src.models.lead import Lead
        
        # Get all leads in docs_requested stage
        leads = Lead.query.filter_by(stage='docs_requested').all()
        
        reminders_sent = 0
        for lead in leads:
            if workflow_service.should_send_reminder(lead):
                # Trigger workflow to send reminder
                workflow_service.process_web_lead(lead.lead_id)
                reminders_sent += 1
        
        return jsonify({
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workflow_bp.route('/workflows/metrics', methods=['GET'])
def get_workflow_metrics():
    """Get workflow performance metrics"""
    try:
        from src.models.lead import Lead
        import json
        
        # Calculate metrics
        total_leads = Lead.query.count()
        
        # Stage distribution
        stages = {}
        for stage in ['inquiry', 'docs_requested', 'docs_received', 'clinical_review', 'consult_ready', 'scheduled', 'decision']:
            stages[stage] = Lead.query.filter_by(stage=stage).count()
        
        # Consent rate
        consented_leads = Lead.query.filter_by(has_consent=True).count()
        consent_rate = (consented_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Document completion rate
        leads_with_docs = Lead.query.filter(Lead.stage.in_(['docs_received', 'clinical_review', 'consult_ready', 'scheduled', 'decision'])).count()
        docs_completion_rate = (leads_with_docs / total_leads * 100) if total_leads > 0 else 0
        
        # Conversion rate (docs to consult)
        scheduled_leads = Lead.query.filter_by(stage='scheduled').count()
        conversion_rate = (scheduled_leads / leads_with_docs * 100) if leads_with_docs > 0 else 0
        
        return jsonify({
            'total_leads': total_leads,
            'stage_distribution': stages,
            'consent_rate': round(consent_rate, 2),
            'docs_completion_rate': round(docs_completion_rate, 2),
            'docs_to_consult_conversion_rate': round(conversion_rate, 2),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

