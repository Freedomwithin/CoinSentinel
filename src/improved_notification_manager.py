import plyer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from pathlib import Path

class ImprovedNotificationManager:
    def __init__(self, email_config=None):
        """
        Initialize notification manager with email configuration.
        
        Args:
            email_config: Dictionary with email settings
                - smtp_server: SMTP server address
                - port: SMTP port (usually 587 for TLS)
                - sender_email: Sender email address
                - password: Email password or app password
                - use_tls: Whether to use TLS (default True)
        """
        self.email_config = email_config or {}
        self.notification_history = []
        self.max_history = 100
        self.history_file = "notification_history.json"
        self.load_history()
        
        # Alert cooldown to prevent spam (in seconds)
        self.alert_cooldowns = {}
        self.cooldown_period = 300  # 5 minutes default
    
    def send_desktop_notification(self, title, message, app_name="CoinSentinel", timeout=10):
        """
        Send desktop notification with better error handling.
        
        Args:
            title: Notification title
            message: Notification message
            app_name: Application name to display
            timeout: How long to show notification (seconds)
        """
        try:
            plyer.notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=timeout
            )
            
            self._log_notification('desktop', title, message)
            return True
            
        except Exception as e:
            print(f"Desktop notification error: {e}")
            return False
    
    def send_email_alert(self, recipient, subject, body, html_body=None):
        """
        Send email alert with HTML support and better formatting.
        
        Args:
            recipient: Recipient email address or list of addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            Boolean indicating success
        """
        if not self._validate_email_config():
            print("Email configuration is incomplete. Please configure SMTP settings.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_config.get('sender_email')
            msg['To'] = recipient if isinstance(recipient, str) else ', '.join(recipient)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(
                self.email_config.get('smtp_server', 'smtp.gmail.com'),
                self.email_config.get('port', 587)
            ) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                
                server.login(
                    self.email_config['sender_email'],
                    self.email_config['password']
                )
                
                server.send_message(msg)
            
            self._log_notification('email', subject, body, recipient)
            return True
            
        except Exception as e:
            print(f"Email notification error: {e}")
            return False
    
    def send_price_alert(self, coin_symbol, current_price, alert_type, threshold_price):
        """
        Send price alert notification (desktop + optional email).
        
        Args:
            coin_symbol: Cryptocurrency symbol
            current_price: Current price
            alert_type: 'above' or 'below'
            threshold_price: Alert threshold price
        """
        # Check cooldown
        cooldown_key = f"{coin_symbol}_{alert_type}_{threshold_price}"
        if not self._check_cooldown(cooldown_key):
            return False
        
        # Create notification message
        if alert_type == 'above':
            title = f"🚀 {coin_symbol} Price Alert!"
            message = f"{coin_symbol} has risen above ${threshold_price:,.2f}\nCurrent price: ${current_price:,.2f}"
        else:
            title = f"⚠️ {coin_symbol} Price Alert!"
            message = f"{coin_symbol} has fallen below ${threshold_price:,.2f}\nCurrent price: ${current_price:,.2f}"
        
        # Send desktop notification
        self.send_desktop_notification(title, message)
        
        # Send email if configured
        if self._validate_email_config() and self.email_config.get('send_alerts', False):
            html_body = self._create_price_alert_html(
                coin_symbol, current_price, alert_type, threshold_price
            )
            recipient = self.email_config.get('alert_recipient', self.email_config.get('sender_email'))
            self.send_email_alert(recipient, title, message, html_body)
        
        return True
    
    def send_portfolio_summary(self, portfolio_data, recipient=None):
        """
        Send portfolio summary email with performance metrics.
        
        Args:
            portfolio_data: Dictionary with portfolio information
            recipient: Email recipient (uses default if not specified)
        """
        if not self._validate_email_config():
            return False
        
        recipient = recipient or self.email_config.get('alert_recipient', self.email_config.get('sender_email'))
        
        subject = f"📊 Crypto Portfolio Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create plain text body
        body = self._create_portfolio_text(portfolio_data)
        
        # Create HTML body
        html_body = self._create_portfolio_html(portfolio_data)
        
        return self.send_email_alert(recipient, subject, body, html_body)
    
    def send_market_update(self, market_data, recipient=None):
        """
        Send market update email with top movers.
        
        Args:
            market_data: List of coin data
            recipient: Email recipient
        """
        if not self._validate_email_config():
            return False
        
        recipient = recipient or self.email_config.get('alert_recipient', self.email_config.get('sender_email'))
        
        subject = f"📈 Crypto Market Update - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create plain text body
        body = self._create_market_update_text(market_data)
        
        # Create HTML body
        html_body = self._create_market_update_html(market_data)
        
        return self.send_email_alert(recipient, subject, body, html_body)
    
    def _validate_email_config(self):
        """Check if email configuration is complete."""
        required_fields = ['smtp_server', 'port', 'sender_email', 'password']
        return all(self.email_config.get(field) for field in required_fields)
    
    def _check_cooldown(self, key):
        """
        Check if enough time has passed since last alert.
        
        Args:
            key: Unique identifier for the alert
            
        Returns:
            Boolean indicating if alert can be sent
        """
        now = datetime.now().timestamp()
        
        if key in self.alert_cooldowns:
            elapsed = now - self.alert_cooldowns[key]
            if elapsed < self.cooldown_period:
                return False
        
        self.alert_cooldowns[key] = now
        return True
    
    def _log_notification(self, notification_type, title, message, recipient=None):
        """Log notification to history."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': notification_type,
            'title': title,
            'message': message[:100],  # Truncate long messages
            'recipient': recipient
        }
        
        self.notification_history.append(log_entry)
        
        # Keep only recent notifications
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
        
        self.save_history()
    
    def _create_price_alert_html(self, coin_symbol, current_price, alert_type, threshold_price):
        """Create HTML email for price alerts."""
        color = "#4CAF50" if alert_type == "above" else "#f44336"
        icon = "🚀" if alert_type == "above" else "⚠️"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background-color: {color}; color: white; padding: 20px; border-radius: 10px;">
                <h2>{icon} {coin_symbol} Price Alert</h2>
                <p style="font-size: 18px;">
                    {coin_symbol} has {alert_type} <strong>${threshold_price:,.2f}</strong>
                </p>
                <p style="font-size: 24px; font-weight: bold;">
                    Current Price: ${current_price:,.2f}
                </p>
            </div>
            <p style="margin-top: 20px; color: #666;">
                Alert triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
    
    def _create_portfolio_text(self, portfolio_data):
        """Create plain text portfolio summary."""
        text = f"Portfolio Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Total Value: ${portfolio_data.get('total_value', 0):,.2f}\n"
        text += f"24h Change: {portfolio_data.get('change_24h', 0):+.2f}%\n"
        text += f"Total P/L: ${portfolio_data.get('total_pl', 0):+,.2f}\n\n"
        
        text += "Holdings:\n"
        text += "-" * 50 + "\n"
        
        for holding in portfolio_data.get('holdings', []):
            text += f"{holding['symbol']}: {holding['amount']:.4f} @ ${holding['price']:,.2f}\n"
        
        return text
    
    def _create_portfolio_html(self, portfolio_data):
        """Create HTML portfolio summary."""
        pl_color = "#4CAF50" if portfolio_data.get('total_pl', 0) >= 0 else "#f44336"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>📊 Portfolio Summary</h2>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Overview</h3>
                <p><strong>Total Value:</strong> ${portfolio_data.get('total_value', 0):,.2f}</p>
                <p><strong>24h Change:</strong> {portfolio_data.get('change_24h', 0):+.2f}%</p>
                <p style="color: {pl_color};"><strong>Total P/L:</strong> ${portfolio_data.get('total_pl', 0):+,.2f}</p>
            </div>
            
            <h3>Holdings</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #333; color: white;">
                    <th style="padding: 10px; text-align: left;">Coin</th>
                    <th style="padding: 10px; text-align: right;">Amount</th>
                    <th style="padding: 10px; text-align: right;">Price</th>
                    <th style="padding: 10px; text-align: right;">Value</th>
                </tr>
        """
        
        for i, holding in enumerate(portfolio_data.get('holdings', [])):
            bg = "#f9f9f9" if i % 2 == 0 else "white"
            html += f"""
                <tr style="background-color: {bg};">
                    <td style="padding: 10px;">{holding['symbol']}</td>
                    <td style="padding: 10px; text-align: right;">{holding['amount']:.4f}</td>
                    <td style="padding: 10px; text-align: right;">${holding['price']:,.2f}</td>
                    <td style="padding: 10px; text-align: right;">${holding['value']:,.2f}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def _create_market_update_text(self, market_data):
        """Create plain text market update."""
        text = f"Market Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        text += "=" * 50 + "\n\n"
        
        # Top gainers
        gainers = sorted(market_data, key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)[:5]
        text += "Top Gainers (24h):\n"
        for coin in gainers:
            text += f"  {coin['symbol'].upper()}: {coin.get('price_change_percentage_24h', 0):+.2f}%\n"
        
        text += "\n"
        
        # Top losers
        losers = sorted(market_data, key=lambda x: x.get('price_change_percentage_24h', 0))[:5]
        text += "Top Losers (24h):\n"
        for coin in losers:
            text += f"  {coin['symbol'].upper()}: {coin.get('price_change_percentage_24h', 0):+.2f}%\n"
        
        return text
    
    def _create_market_update_html(self, market_data):
        """Create HTML market update."""
        gainers = sorted(market_data, key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)[:5]
        losers = sorted(market_data, key=lambda x: x.get('price_change_percentage_24h', 0))[:5]
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>📈 Market Update</h2>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <h3 style="color: #4CAF50;">Top Gainers (24h)</h3>
            <ul>
        """
        
        for coin in gainers:
            html += f"<li><strong>{coin['symbol'].upper()}</strong>: {coin.get('price_change_percentage_24h', 0):+.2f}%</li>"
        
        html += """
            </ul>
            
            <h3 style="color: #f44336;">Top Losers (24h)</h3>
            <ul>
        """
        
        for coin in losers:
            html += f"<li><strong>{coin['symbol'].upper()}</strong>: {coin.get('price_change_percentage_24h', 0):+.2f}%</li>"
        
        html += """
            </ul>
        </body>
        </html>
        """
        
        return html
    
    def save_history(self):
        """Save notification history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.notification_history, f, indent=2)
        except Exception as e:
            print(f"Error saving notification history: {e}")
    
    def load_history(self):
        """Load notification history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.notification_history = json.load(f)
        except Exception as e:
            print(f"Error loading notification history: {e}")
            self.notification_history = []
    
    def get_notification_history(self, limit=20):
        """
        Get recent notification history.
        
        Args:
            limit: Number of recent notifications to return
            
        Returns:
            List of recent notifications
        """
        return self.notification_history[-limit:]
    
    def clear_history(self):
        """Clear notification history."""
        self.notification_history = []
        self.save_history()
    
    def set_cooldown_period(self, seconds):
        """Set alert cooldown period in seconds."""
        self.cooldown_period = seconds


# Example usage
if __name__ == "__main__":
    # Example email configuration (use environment variables in production!)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'sender_email': 'your-email@gmail.com',
        'password': 'your-app-password',  # Use app password for Gmail
        'use_tls': True,
        'send_alerts': True,
        'alert_recipient': 'recipient@example.com'
    }
    
    # Create notification manager
    nm = ImprovedNotificationManager(email_config)
    
    # Send desktop notification
    nm.send_desktop_notification(
        "Test Alert",
        "This is a test notification from CoinSentinel"
    )
    
    # Send price alert
    nm.send_price_alert('BTC', 45250.00, 'above', 45000.00)
    
    # Send portfolio summary
    portfolio_data = {
        'total_value': 50000.00,
        'change_24h': 2.5,
        'total_pl': 5000.00,
        'holdings': [
            {'symbol': 'BTC', 'amount': 0.5, 'price': 45000, 'value': 22500},
            {'symbol': 'ETH', 'amount': 10, 'price': 2500, 'value': 25000},
        ]
    }
    # nm.send_portfolio_summary(portfolio_data)
    
    print("Notifications sent! Check notification history:")
    for notification in nm.get_notification_history():
        print(f"  {notification['timestamp']}: {notification['title']}")