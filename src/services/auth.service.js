import { User } from "../models/user.model.js";
import { Admin } from "../models/admin.model.js";
import { Doctor } from "../models/doctor.model.js";
import { Nurse } from "../models/nurse.model.js";
import bcrypt from "bcryptjs";

export const findAccountByRole = async (role, username) => {
  switch (role) {
    case "USER":
      return User.findOne({ mobile: username });
    case "ADMIN":
      return Admin.findOne({ username }).select("+password");
    case "DOCTOR":
      return Doctor.findOne({ username }).select("+password");
    case "NURSE":
      return Nurse.findOne({ username }).select("+password");
    default:
      return null;
  }
};

export const verifyPassword = async (plain, hashed) => {
  return bcrypt.compare(plain, hashed);
};
