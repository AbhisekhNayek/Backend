import { User } from "../models/user.model.js";
import { generateOTP, saveOTP, verifyOTP } from "../services/otp.service.js";
import { generateToken } from "../utils/jwt.utils.js";

export const sendOtp = async (req, res) => {
  try {
    const { mobile } = req.body;

    if (!mobile) {
      return res.status(400).json({ message: "Mobile required" });
    }

    const otp = generateOTP();
    await saveOTP(mobile, otp);

    // TODO: Integrate SMS Gateway
    console.log("OTP:", otp);

    res.json({ success: true, message: "OTP sent" });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

export const verifyOtp = async (req, res) => {
  try {
    const { mobile, otp } = req.body;

    const validOtp = await verifyOTP(mobile, otp);

    if (!validOtp) {
      return res.status(401).json({ message: "Invalid or expired OTP" });
    }

    let user = await User.findOne({ mobile });

    if (!user) {
      user = await User.create({
        mobile,
        isMobileVerified: true
      });
    }

    const token = generateToken({
      id: user._id,
      role: "USER"
    });

    res.json({
      success: true,
      token,
      user
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
