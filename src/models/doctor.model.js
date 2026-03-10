import mongoose from "mongoose";
import bcrypt from "bcryptjs";

const doctorSchema = new mongoose.Schema(
  {
    username: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      lowercase: true,
      maxlength: 50,
      index: true,
    },

    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },

    phone: {
      type: String,
      trim: true,
    },

    password: {
      type: String,
      required: true,
      minlength: 8,
      select: false,
    },

    isFirstLogin: {
      type: Number,
      enum: [0, 1],
      default: 1,
    },

    /* ---------------- Profile ---------------- */

    name: {
      type: String,
      required: true,
      trim: true,
    },

    profileImage: {
      type: String,
    },

    bio: {
      type: String,
    },

    specialization: {
      type: String,
      trim: true,
      index: true,
    },

    qualifications: {
      type: [String],
    },

    experience: {
      type: Number,
      min: 0,
    },

    languages: {
      type: [String],
    },

    /* ---------------- License ---------------- */

    licenseNo: {
      type: String,
      trim: true,
      index: true,
    },

    verificationStatus: {
      type: Number,
      enum: [0, 1, 2], // 0=PENDING,1=APPROVED,2=REJECTED
      default: 0,
      index: true,
    },

    /* ---------------- Fees ---------------- */

    fees: {
      video: { type: Number, min: 0 },
      clinic: { type: Number, min: 0 },
    },

    consultationMode: {
      type: [String],
      enum: ["VIDEO", "CLINIC"],
    },

    /* ---------------- Clinic ---------------- */

    clinicName: {
      type: String,
    },

    clinicAddress: {
      type: String,
    },

    location: {
      latitude: Number,
      longitude: Number,
    },

    /* ---------------- Rating ---------------- */

    rating: {
      type: Number,
      default: 0,
    },

    totalReviews: {
      type: Number,
      default: 0,
    },

    /* ---------------- Status ---------------- */

    isOnline: {
      type: Number,
      enum: [0, 1],
      default: 0,
    },

    isDeleted: {
      type: Number,
      enum: [0, 1],
      default: 0,
      index: true,
    },
  },
  {
    timestamps: true,
    versionKey: false,
  },
);

/* ---------------- Password Hash ---------------- */

doctorSchema.pre("save", async function () {
  if (!this.isModified("password")) return;

  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});

/* ---------------- Compare Password ---------------- */

doctorSchema.methods.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

export const Doctor = mongoose.model("Doctor", doctorSchema);
