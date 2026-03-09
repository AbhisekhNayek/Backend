import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import { User } from "../models/user.model.js";
import { OTP } from "../models/otp.model.js";
import { sendEmail } from "../services/email.service.js";
import dotenv from "dotenv";

dotenv.config();

/* ================================
   GENERATE OTP
================================ */
const generateOTP = () => {
  return crypto.randomInt(100000, 999999).toString();
};

/* ================================
   REGISTER USER
================================ */
export const registerUser = async (req, res) => {
  try {
    const { name, email, phone, password, gender, dob } = req.body;

    if (!email || !password || !phone) {
      return res.status(400).json({
        message: "Email, phone and password are required"
      });
    }

    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(400).json({ message: "User already exists" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      email,
      phone,
      password: hashedPassword,
      gender,
      dob
    });

    const otp = generateOTP();

    await OTP.findOneAndDelete({ email });

    await OTP.create({
      email,
      otp,
      expiresAt: new Date(Date.now() + 5 * 60 * 1000)
    });

    await sendEmail({
      email,
      subject: "Verify Your Email",
      otp,
      name
    });

    res.status(201).json({
      success: true,
      message: "User registered. OTP sent to email."
    });

  } catch (error) {
    console.error("REGISTER ERROR:", error);
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   VERIFY EMAIL OTP
================================ */
export const verifyEmailOtp = async (req, res) => {
  try {
    const { email, otp } = req.body;

    const record = await OTP.findOne({ email, otp });

    if (!record || record.expiresAt < new Date()) {
      return res.status(400).json({ message: "Invalid or expired OTP" });
    }

    await User.updateOne({ email }, { isEmailVerified: true });
    await OTP.deleteOne({ _id: record._id });

    res.json({ success: true, message: "Email verified successfully" });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   LOGIN USER
================================ */
export const loginUser = async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email }).select("+password");

    if (!user) {
      return res.status(400).json({ message: "Invalid credentials" });
    }

    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(400).json({ message: "Invalid credentials" });
    }

    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "7d" }
    );

    user.lastLoginAt = new Date();
    await user.save();

    res.json({
      success: true,
      token
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   GET ALL USERS (Admin)
================================ */
export const getAllUsers = async (req, res) => {
  try {
    const users = await User.find();

    res.json({
      success: true,
      count: users.length,
      users
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   GET MY PROFILE
================================ */
export const getMyProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user.id);

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json({
      success: true,
      user
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   GET SINGLE USER
================================ */
export const getUserById = async (req, res) => {
  try {
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json({
      success: true,
      user
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   UPDATE USER
================================ */
export const updateUser = async (req, res) => {
  try {
    const updated = await User.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    res.json({
      success: true,
      user: updated
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   SOFT DELETE USER
================================ */
export const deleteUser = async (req, res) => {
  try {
    await User.findByIdAndUpdate(req.params.id, {
      isDeleted: true
    });

    res.json({
      success: true,
      message: "User deleted successfully"
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};