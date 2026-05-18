import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from app.config import settings

async def send_email(email: str, subject: str, otp: str, name: str = "User"):
    # Replicate HTML format
    curr_year = datetime.now().year
    html_message = f"""
    <div style="font-family: Arial, sans-serif; background:#f4f6f9; padding:40px;">
      <div style="max-width:500px; margin:auto; background:white; border-radius:10px; padding:30px; text-align:center; box-shadow:0 5px 15px rgba(0,0,0,0.08);">
        
        <h2 style="color:#2c3e50;">Doctor Booking App</h2>
        <p style="color:#555;">Hi {name},</p>
        <p style="color:#555;">
          Use the OTP below to verify your email address.
          This OTP is valid for <strong>10 minutes</strong>.
        </p>

        <div style="margin:25px 0;">
          <span style="
            display:inline-block;
            font-size:28px;
            letter-spacing:5px;
            background:#4CAF50;
            color:white;
            padding:15px 25px;
            border-radius:8px;
            font-weight:bold;">
            {otp}
          </span>
        </div>

        <p style="color:#777; font-size:14px;">
          If you did not request this, please ignore this email.
        </p>

        <hr style="margin:30px 0; border:none; border-top:1px solid #eee;" />

        <p style="font-size:12px; color:#aaa;">
          © {curr_year} Doctor Booking App. All rights reserved.
        </p>
      </div>
    </div>
    """

    message = MIMEMultipart("alternative")
    message["From"] = settings.smtp_mail
    message["To"] = email
    message["Subject"] = subject
    
    html_part = MIMEText(html_message, "html")
    message.attach(html_part)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_mail,
        password=settings.smtp_password,
        use_tls=False,  # False because we set secure: false in NodeMailer and use standard SMTP ports usually (587 or 25)
        start_tls=True if settings.smtp_port == 587 else False
    )
