import plyer
import smtplib

class NotificationManager:
    def __init__(self, email_config=None):
        self.email_config = email_config or {}
    
    def send_desktop_notification(self, title, message):
        plyer.notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    
    def send_email_alert(self, recipient, subject, body):
        try:
            with smtplib.SMTP(
                self.email_config.get('smtp_server', 'smtp.gmail.com'), 
                self.email_config.get('port', 587)
            ) as server:
                server.starttls()
                server.login(
                    self.email_config.get('sender_email', ''),
                    self.email_config.get('password', '')
                )
                server.sendmail(
                    self.email_config.get('sender_email', ''), 
                    recipient, 
                    f"Subject: {subject}\n\n{body}"
                )
        except Exception as e:
            print(f"Email notification error: {e}")

