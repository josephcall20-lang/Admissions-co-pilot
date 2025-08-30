import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from src.models.lead import Lead

class ObservabilityService:
    def __init__(self):
        # In-memory metrics storage (in production, would use proper metrics store)
        self.metrics = defaultdict(list)
        self.logs = deque(maxlen=1000)  # Keep last 1000 log entries
        self.alerts = []
        
        # Performance thresholds
        self.thresholds = {
            'api_response_time_ms': 1000,
            'docs_completion_days': 5,
            'consult_overrun_rate': 10,
            'automation_failure_rate': 1
        }
    
    def log_event(self, event_type, message, level='INFO', metadata=None):
        """Log an event with structured data"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'level': level,
            'message': message,
            'metadata': metadata or {}
        }
        
        self.logs.append(log_entry)
        
        # Print to console (in production, would send to proper logging system)
        print(f"[{level}] {event_type}: {message}")
        if metadata:
            print(f"  Metadata: {json.dumps(metadata, indent=2)}")
    
    def record_metric(self, metric_name, value, tags=None):
        """Record a metric value"""
        metric_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'value': value,
            'tags': tags or {}
        }
        
        self.metrics[metric_name].append(metric_entry)
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
        
        # Check thresholds
        self.check_threshold(metric_name, value)
    
    def check_threshold(self, metric_name, value):
        """Check if metric value exceeds threshold"""
        if metric_name in self.thresholds:
            threshold = self.thresholds[metric_name]
            
            if value > threshold:
                alert = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'threshold_exceeded',
                    'metric': metric_name,
                    'value': value,
                    'threshold': threshold,
                    'severity': 'warning'
                }
                
                self.alerts.append(alert)
                self.log_event('ALERT', f'Threshold exceeded: {metric_name} = {value} > {threshold}', 'WARNING', alert)
    
    def track_api_performance(self, endpoint, duration_ms, status_code):
        """Track API endpoint performance"""
        self.record_metric('api_response_time_ms', duration_ms, {
            'endpoint': endpoint,
            'status_code': status_code
        })
        
        self.log_event('API_CALL', f'{endpoint} completed in {duration_ms}ms', 'INFO', {
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'status_code': status_code
        })
    
    def track_lead_progression(self, lead_id, from_stage, to_stage):
        """Track lead stage progression"""
        self.log_event('LEAD_PROGRESSION', f'Lead {lead_id} moved from {from_stage} to {to_stage}', 'INFO', {
            'lead_id': lead_id,
            'from_stage': from_stage,
            'to_stage': to_stage
        })
        
        # Record stage transition metric
        self.record_metric('stage_transitions', 1, {
            'from_stage': from_stage,
            'to_stage': to_stage
        })
    
    def track_workflow_execution(self, workflow_type, lead_id, duration_ms, success):
        """Track workflow execution"""
        self.record_metric('workflow_duration_ms', duration_ms, {
            'workflow_type': workflow_type,
            'success': success
        })
        
        if not success:
            self.record_metric('workflow_failures', 1, {
                'workflow_type': workflow_type
            })
        
        self.log_event('WORKFLOW_EXECUTION', f'Workflow {workflow_type} for lead {lead_id}', 
                      'INFO' if success else 'ERROR', {
            'workflow_type': workflow_type,
            'lead_id': lead_id,
            'duration_ms': duration_ms,
            'success': success
        })
    
    def calculate_kpis(self):
        """Calculate key performance indicators"""
        try:
            # Get all leads
            leads = Lead.query.all()
            total_leads = len(leads)
            
            if total_leads == 0:
                return {
                    'docs_to_consult_conversion': 0,
                    'median_docs_completion_days': 0,
                    'consult_overrun_rate': 0,
                    'automation_failure_rate': 0,
                    'consent_compliance_rate': 100
                }
            
            # Docs to consult conversion rate
            docs_received_leads = [l for l in leads if l.stage in ['docs_received', 'clinical_review', 'consult_ready', 'scheduled', 'decision']]
            scheduled_leads = [l for l in leads if l.stage in ['scheduled', 'decision']]
            
            docs_to_consult_conversion = (len(scheduled_leads) / len(docs_received_leads) * 100) if docs_received_leads else 0
            
            # Median docs completion time (simulated)
            completion_times = []
            for lead in docs_received_leads:
                if lead.last_touch_iso:
                    # Simulate completion time (in real system, would track actual times)
                    completion_times.append(3)  # Assume 3 days average
            
            median_docs_completion_days = sorted(completion_times)[len(completion_times)//2] if completion_times else 0
            
            # Consult overrun rate (simulated - would track actual consult durations)
            consult_overrun_rate = 5  # Assume 5% overrun rate
            
            # Automation failure rate
            workflow_failures = sum(entry['value'] for entry in self.metrics.get('workflow_failures', []))
            total_workflows = len(self.metrics.get('workflow_duration_ms', []))
            automation_failure_rate = (workflow_failures / total_workflows * 100) if total_workflows > 0 else 0
            
            # Consent compliance rate
            consented_leads = [l for l in leads if l.has_consent]
            consent_compliance_rate = (len(consented_leads) / total_leads * 100) if total_leads > 0 else 0
            
            kpis = {
                'docs_to_consult_conversion': round(docs_to_consult_conversion, 2),
                'median_docs_completion_days': median_docs_completion_days,
                'consult_overrun_rate': round(consult_overrun_rate, 2),
                'automation_failure_rate': round(automation_failure_rate, 2),
                'consent_compliance_rate': round(consent_compliance_rate, 2)
            }
            
            # Check KPI thresholds
            if docs_to_consult_conversion < 60:
                self.create_alert('kpi_below_target', 'Docs to consult conversion below 60%', 'warning')
            
            if median_docs_completion_days > 5:
                self.create_alert('kpi_below_target', 'Median docs completion time exceeds 5 days', 'warning')
            
            return kpis
            
        except Exception as e:
            self.log_event('ERROR', f'Error calculating KPIs: {e}', 'ERROR')
            return {}
    
    def create_alert(self, alert_type, message, severity='info'):
        """Create an alert"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        self.log_event('ALERT', message, severity.upper(), alert)
    
    def get_daily_digest(self):
        """Generate daily operational digest"""
        try:
            # Get leads by stage
            leads = Lead.query.all()
            stage_counts = defaultdict(int)
            
            for lead in leads:
                stage_counts[lead.stage] += 1
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_logs = [
                log for log in self.logs 
                if datetime.fromisoformat(log['timestamp']) > yesterday
            ]
            
            # Count events by type
            event_counts = defaultdict(int)
            for log in recent_logs:
                event_counts[log['event_type']] += 1
            
            # Get active alerts
            active_alerts = [alert for alert in self.alerts if not alert.get('acknowledged', False)]
            
            digest = {
                'date': datetime.utcnow().date().isoformat(),
                'lead_counts': dict(stage_counts),
                'total_leads': len(leads),
                'recent_activity': dict(event_counts),
                'active_alerts': len(active_alerts),
                'kpis': self.calculate_kpis(),
                'system_health': 'healthy' if len(active_alerts) == 0 else 'attention_needed'
            }
            
            return digest
            
        except Exception as e:
            self.log_event('ERROR', f'Error generating daily digest: {e}', 'ERROR')
            return {}
    
    def get_metrics_summary(self, metric_name, hours=24):
        """Get summary statistics for a metric over time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_metrics = [
                entry for entry in self.metrics.get(metric_name, [])
                if datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]
            
            if not recent_metrics:
                return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
            
            values = [entry['value'] for entry in recent_metrics]
            
            return {
                'count': len(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1] if values else 0
            }
            
        except Exception as e:
            self.log_event('ERROR', f'Error getting metrics summary: {e}', 'ERROR')
            return {}
    
    def health_check(self):
        """Perform system health check"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        try:
            # Database connectivity
            lead_count = Lead.query.count()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'lead_count': lead_count
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # Check for recent errors
        recent_errors = [
            log for log in self.logs 
            if log['level'] == 'ERROR' and 
            datetime.fromisoformat(log['timestamp']) > datetime.utcnow() - timedelta(hours=1)
        ]
        
        health_status['checks']['error_rate'] = {
            'status': 'healthy' if len(recent_errors) < 5 else 'unhealthy',
            'recent_errors': len(recent_errors)
        }
        
        if len(recent_errors) >= 5:
            health_status['status'] = 'unhealthy'
        
        # Check active alerts
        active_alerts = [alert for alert in self.alerts if not alert.get('acknowledged', False)]
        critical_alerts = [alert for alert in active_alerts if alert.get('severity') == 'critical']
        
        health_status['checks']['alerts'] = {
            'status': 'healthy' if len(critical_alerts) == 0 else 'unhealthy',
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts)
        }
        
        if len(critical_alerts) > 0:
            health_status['status'] = 'unhealthy'
        
        return health_status

# Global instance
observability_service = ObservabilityService()

