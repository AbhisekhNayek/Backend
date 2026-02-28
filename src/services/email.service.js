import nodeMailer from "nodemailer";
import dotenv from "dotenv";

dotenv.config();

export const sendEmail = async ({ email, subject, otp, name }) => {

  const transporter = nodeMailer.createTransport({
    host: process.env.SMTP_HOST,
    service: process.env.SMTP_SERVICE,
    port: process.env.SMTP_PORT,
    secure: false,
    auth: {
      user: process.env.SMTP_MAIL,
      pass: process.env.SMTP_PASSWORD,
    },
  });

  const htmlMessage = `
  <div style="font-family: Arial, sans-serif; background:#f4f6f9; padding:40px;">
    <div style="max-width:500px; margin:auto; background:white; border-radius:10px; padding:30px; text-align:center; box-shadow:0 5px 15px rgba(0,0,0,0.08);">
      
      <h2 style="color:#2c3e50;">Doctor Booking App</h2>
      <p style="color:#555;">Hi ${name || "User"},</p>
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
          ${otp}
        </span>
      </div>

      <p style="color:#777; font-size:14px;">
        If you did not request this, please ignore this email.
      </p>

      <hr style="margin:30px 0; border:none; border-top:1px solid #eee;" />

      <p style="font-size:12px; color:#aaa;">
        © ${new Date().getFullYear()} Doctor Booking App. All rights reserved.
      </p>
    </div>
  </div>
  `;

  const options = {
    from: process.env.SMTP_MAIL,
    to: email,
    subject,
    html: htmlMessage,
  };

  await transporter.sendMail(options);
};