import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    /* ===============================
       BASIC INFO
    =============================== */

    name: {
      type: String,
      trim: true,
      maxlength: 50
    },

    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\S+@\S+\.\S+$/, "Invalid email format"]
    },

    phone: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      match: [/^[0-9]{10,15}$/, "Invalid phone number"]
    },

    profilePic: {
      type: String
    },

    gender: {
      type: String,
      enum: ["male", "female", "other"],
      required: true,
    },

    dob: {
      type: Date,
      required: true
    },

    /* ===============================
       AUTHENTICATION
    =============================== */

    password: {
      type: String,
      minlength: 6,
      select: false
    },

    role: {
      type: String,
      enum: ["PATIENT", "DOCTOR", "ADMIN"],
      default: "PATIENT"
    },

    isEmailVerified: {
      type: Boolean,
      default: false
    },

    isPhoneVerified: {
      type: Boolean,
      default: false
    },

    /* ===============================
       ADDRESS INFO
    =============================== */

    address: {
      line1: String,
      line2: String,
      city: String,
      state: String,
      country: {
        type: String,
        default: "India"
      },
      pincode: String
    },

    /* ===============================
       ACCOUNT STATUS
    =============================== */

    isBlocked: {
      type: Boolean,
      default: false
    },

    isDeleted: {
      type: Boolean,
      default: false
    },

    lastLoginAt: {
      type: Date
    },

    /* ===============================
       SECURITY TRACKING
    =============================== */

    loginAttempts: {
      type: Number,
      default: 0
    },

    lockUntil: {
      type: Date
    },

    refreshToken: {
      type: String,
      select: false
    }
  },
  {
    timestamps: true,
    versionKey: false
  }
);

export const User = mongoose.model("User", userSchema);