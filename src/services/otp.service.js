import { OTP } from "../models/otp.model.js";

export const generateOTP = () =>
  Math.floor(100000 + Math.random() * 900000).toString();

export const saveOTP = async (mobile, otp) => {
  await OTP.deleteMany({ mobile });

  return OTP.create({
    mobile,
    otp,
    expiresAt: new Date(Date.now() + 5 * 60 * 1000)
  });
};

export const verifyOTP = async (mobile, otp) => {
  return OTP.findOne({ mobile, otp });
};
