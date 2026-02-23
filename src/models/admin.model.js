import mongoose from "mongoose";
import bcrypt from "bcryptjs";

const adminSchema = new mongoose.Schema(
  {
    username: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      lowercase: true,
      maxlength: 50,
      index: true
    },

    password: {
      type: String,
      required: true,
      minlength: 8,
      select: false
    },

    name: {
      type: String,
      trim: true,
      maxlength: 50
    },

    role: {
      type: String,
      enum: ["super_admin", "admin", "moderator"],
      default: "admin"
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

export const Admin = mongoose.model("Admin", adminSchema);
