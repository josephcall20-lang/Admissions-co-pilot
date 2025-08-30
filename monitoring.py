from flask import Blueprint, request, jsonify
from src.services.observability_service import observability_service
from src.services.security_service import security_service
from datetime import datetime, timedelta

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    try:
        health_status = observability_service.health_check()
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        metric_name = request.args.get('metric')
        hours = int(request.args.get('hours', 24))
        
        if metric_name:
            # Get specific metric
            summary = observability_service.get_metrics_summary(metric_name, hours)
            return jsonify({
                'metric': metric_name,
                'period_hours': hours,
                'summary': summary
            })
        else:
            # Get all available metrics
            available_metrics = list(observability_service.metrics.keys())
            return jsonify({
                'available_metrics': available_metrics,
                'total_metrics': len(available_metrics)
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/kpis', methods=['GET'])
def get_kpis():
    """Get key performance indicators"""
    try:
        kpis = observability_service.calculate_kpis()
        
        return jsonify({
            'kpis': kpis,
            'timestamp': datetime.utcnow().isoformat(),
            'targets': {
                'docs_to_consult_conversion': 60,
                'median_docs_completion_days': 5,
                'consult_overrun_rate': 10,
                'automation_failure_rate': 1,
                'consent_compliance_rate': 100
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/digest/daily', methods=['GET'])
def get_daily_digest():
    """Get daily operational digest"""
    try:
        digest = observability_service.get_daily_digest()
        return jsonify(digest)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        alerts = observability_service.alerts
        
        if active_only:
            alerts = [alert for alert in alerts if not alert.get('acknowledged', False)]
        
        return jsonify({
            'alerts': alerts,
            'total_count': len(observability_service.alerts),
            'active_count': len([a for a in observability_service.alerts if not a.get('acknowledged', False)])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alerts/<int:alert_index>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_index):
    """Acknowledge an alert"""
    try:
        if 0 <= alert_index < len(observability_service.alerts):
            observability_service.alerts[alert_index]['acknowledged'] = True
            observability_service.alerts[alert_index]['acknowledged_at'] = datetime.utcnow().isoformat()
            
            return jsonify({'status': 'acknowledged'})
        else:
            return jsonify({'error': 'Alert not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get system logs"""
    try:
        level = request.args.get('level', '').upper()
        event_type = request.args.get('event_type', '')
        limit = int(request.args.get('limit', 100))
        
        logs = list(observability_service.logs)
        
        # Filter by level
        if level:
            logs = [log for log in logs if log['level'] == level]
        
        # Filter by event type
        if event_type:
            logs = [log for log in logs if log['event_type'] == event_type]
        
        # Limit results
        logs = logs[-limit:]
        
        return jsonify({
            'logs': logs,
            'total_count': len(observability_service.logs),
            'filtered_count': len(logs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/compliance/report', methods=['GET'])
def get_compliance_report():
    """Get HIPAA compliance report"""
    try:
        report = security_service.generate_compliance_report()
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/performance/api', methods=['GET'])
def get_api_performance():
    """Get API performance metrics"""
    try:
        hours = int(request.args.get('hours', 24))
        
        # Get API response time metrics
        api_metrics = observability_service.get_metrics_summary('api_response_time_ms', hours)
        
        # Get recent API calls
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_logs = [
            log for log in observability_service.logs 
            if log['event_type'] == 'API_CALL' and 
            datetime.fromisoformat(log['timestamp']) > cutoff_time
        ]
        
        # Group by endpoint
        endpoint_stats = {}
        for log in recent_logs:
            endpoint = log['metadata'].get('endpoint', 'unknown')
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_duration': 0,
                    'errors': 0
                }
            
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_duration'] += log['metadata'].get('duration_ms', 0)
            
            if log['metadata'].get('status_code', 200) >= 400:
                endpoint_stats[endpoint]['errors'] += 1
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            if stats['count'] > 0:
                stats['avg_duration_ms'] = stats['total_duration'] / stats['count']
                stats['error_rate'] = (stats['errors'] / stats['count']) * 100
            else:
                stats['avg_duration_ms'] = 0
                stats['error_rate'] = 0
        
        return jsonify({
            'period_hours': hours,
            'overall_metrics': api_metrics,
            'endpoint_stats': endpoint_stats,
            'total_requests': len(recent_logs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        health = observability_service.health_check()
        kpis = observability_service.calculate_kpis()
        active_alerts = [alert for alert in observability_service.alerts if not alert.get('acknowledged', False)]
        
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': health['status'],
            'health_checks': health['checks'],
            'kpis': kpis,
            'active_alerts_count': len(active_alerts),
            'critical_alerts_count': len([a for a in active_alerts if a.get('severity') == 'critical']),
            'system_uptime': 'N/A',  # Would track actual uptime
            'version': '1.0.0'
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

