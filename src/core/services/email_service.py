
from email.message import EmailMessage

import aiosmtplib

from src.config.settings import settings



async def send_invitation_email(
    recipient_email: str,
    invitation_url: str,
) -> None:
    message = EmailMessage()
    message["Subject"] = "TalentIQ - Your account invitation"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient_email

    message.set_content(
        f"""
Hello,

You have been invited to join TalentIQ.

Use the link below to set your password and activate your account setup:

{invitation_url}

This invitation expires in 48 hours and can be used only once.

If you were not expecting this invitation, you can ignore this email.

Regards,
TalentIQ Support
"""
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
        timeout=20,
    )

async def send_otp_email(
    recipient_email: str,
    otp: str,
) -> None:
    message = EmailMessage()
    message["Subject"] = "TalentIQ - Password Reset OTP"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient_email

    message.set_content(
        f"""
Hello,

We received a request to reset your TalentIQ password.

Your verification code is: {otp}

This code expires in 5 minutes.

If you did not request a password reset, you can ignore this email.

Regards,
TalentIQ Support
"""
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
        timeout=20,
    )
