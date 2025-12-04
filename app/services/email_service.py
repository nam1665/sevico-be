import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import utils as email_utils
from typing import List
import logging
from app.config.settings import get_settings


logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        plain_text: str = None
    ) -> bool:
        """
        Send an email via SMTP (supports AWS SES, Gmail, etc).
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_content: HTML content of email
            plain_text: Plain text fallback
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = email_utils.formataddr((self.settings.sender_name, self.settings.sender_email))
            message["To"] = recipient_email
            
            # Add AWS SES Configuration Set if configured
            if self.settings.aws_ses_configuration_set:
                message.add_header('X-SES-CONFIGURATION-SET', self.settings.aws_ses_configuration_set)
            
            # Add plain text part
            if plain_text:
                message.attach(MIMEText(plain_text, "plain"))
            
            # Add HTML part
            message.attach(MIMEText(html_content, "html"))
            
            # Send email with proper EHLO/STARTTLS sequence for AWS SES
            server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
            server.ehlo()
            if self.settings.smtp_tls:
                server.starttls()
                server.ehlo()  # EHLO again after STARTTLS
            server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.sendmail(self.settings.sender_email, recipient_email, message.as_string())
            server.close()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, verification_code: str) -> bool:
        """
        Send email verification code.
        
        Args:
            email: Recipient email
            verification_code: 6-digit verification code
            
        Returns:
            True if sent successfully
        """
        subject = "Email Verification - Sevico"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Email Verification</h2>
                <p>Hello,</p>
                <p>Your verification code is:</p>
                <h1 style="color: #007bff; letter-spacing: 5px;">{verification_code}</h1>
                <p>This code will expire in {self.settings.verification_code_expiration_minutes} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Sevico Team</p>
            </body>
        </html>
        """
        
        plain_text = f"Your verification code is: {verification_code}"
        
        return self.send_email(email, subject, html_content, plain_text)
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """
        Send password reset email with token.
        
        Args:
            email: Recipient email
            reset_token: Password reset token
            
        Returns:
            True if sent successfully
        """
        subject = "Password Reset - Sevico"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password. Use the token below:</p>
                <code style="background-color: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                    {reset_token}
                </code>
                <p>This token will expire in {self.settings.password_reset_expiration_hours} hour(s).</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Sevico Team</p>
            </body>
        </html>
        """
        
        plain_text = f"Your password reset token is: {reset_token}"
        
        return self.send_email(email, subject, html_content, plain_text)


# Singleton instance
email_service = EmailService()
