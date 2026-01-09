import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class AlertManager:
    def __init__(self):
        self.alerts = []

    def create_alert(self, alert_type, message, job_id=None, severity='info'):
        alert = {
            'type': alert_type,
            'message': message,
            'job_id': job_id,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self, job_id=None, alert_type=None, limit=100):
        filtered = self.alerts

        if job_id:
            filtered = [a for a in filtered if a['job_id'] == job_id]

        if alert_type:
            filtered = [a for a in filtered if a['type'] == alert_type]

        return filtered[-limit:]


class EmailNotifier:
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.enabled = bool(self.username and self.password)

    def send_job_completion(self, recipient, job_name, job_id, status):
        if not self.enabled:
            return False

        subject = f"Training Job {status.upper()}: {job_name}"
        body = f"""
Training job '{job_name}' (ID: {job_id}) has {status}.

Status: {status.upper()}
Time: {datetime.utcnow().isoformat()}
        """

        return self._send_email(recipient, subject, body)

    def send_alert(self, recipient, alert_type, message):
        if not self.enabled:
            return False

        subject = f"Alert: {alert_type}"
        body = f"""
Alert Type: {alert_type}
Message: {message}
Time: {datetime.utcnow().isoformat()}
        """

        return self._send_email(recipient, subject, body)

    def _send_email(self, recipient, subject, body):
        if not self.enabled:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            print(f"Email send failed: {str(e)}")
            return False


class SlackNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)

    def send_job_update(self, job_name, job_id, status, progress):
        if not self.enabled:
            return False

        import requests

        payload = {
            'text': f'Training Update',
            'attachments': [
                {
                    'color': self._get_color(status),
                    'title': job_name,
                    'fields': [
                        {'title': 'Job ID', 'value': str(job_id), 'short': True},
                        {'title': 'Status', 'value': status.upper(), 'short': True},
                        {'title': 'Progress', 'value': f'{progress}%', 'short': True},
                        {'title': 'Time', 'value': datetime.utcnow().isoformat(), 'short': True}
                    ]
                }
            ]
        }

        try:
            requests.post(self.webhook_url, json=payload)
            return True
        except Exception as e:
            print(f"Slack notification failed: {str(e)}")
            return False

    def _get_color(self, status):
        colors = {
            'queued': '#FFC107',
            'running': '#17A2B8',
            'completed': '#28A745',
            'failed': '#DC3545',
            'paused': '#6C757D'
        }
        return colors.get(status, '#6C757D')


class NotificationService:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()

    def notify_job_started(self, job_id, job_name, user_email=None):
        self.alert_manager.create_alert(
            'job_started',
            f'Training job {job_name} has started',
            job_id,
            'info'
        )

    def notify_job_completed(self, job_id, job_name, status, user_email=None):
        self.alert_manager.create_alert(
            'job_completed',
            f'Training job {job_name} has {status}',
            job_id,
            'success' if status == 'completed' else 'error'
        )

        if user_email:
            self.email_notifier.send_job_completion(user_email, job_name, job_id, status)

        self.slack_notifier.send_job_update(job_name, job_id, status, 100)

    def notify_resource_limit(self, job_id, resource_type, limit, current):
        message = f'{resource_type} limit exceeded. Limit: {limit}, Current: {current}'
        self.alert_manager.create_alert(
            'resource_limit',
            message,
            job_id,
            'warning'
        )

    def notify_error(self, job_id, error_message):
        self.alert_manager.create_alert(
            'training_error',
            f'Training error: {error_message}',
            job_id,
            'error'
        )
