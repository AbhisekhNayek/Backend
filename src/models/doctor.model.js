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
      index: true
    },

    password: {
      type: String,
      required: true,
      minlength: 8,
      select: false
    },

    isFirstLogin: {
      type: Number,
      enum: [0, 1],
      default: 1
    },

    name: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50
    },

    specialization: {
      type: String,
      trim: true,
      maxlength: 100
    },

    experience: {
      type: Number,
      min: 0
    },

    licenseNo: {
      type: String,
      trim: true,
      maxlength: 50,
      index: true
    },

    fees: {
      video: {
        type: Number,
        min: 0
      },
      clinic: {
        type: Number,
        min: 0
      }
    },

    location: {
      latitude: {
        type: Number
      },
      longitude: {
        type: Number
      }
    },

    isOnline: {
      type: Number,
      enum: [0, 1],
      default: 0,
      index: true
    },

    verificationStatus: {
      type: Number,
      enum: [0, 1, 2], // 0=PENDING,1=APPROVED,2=REJECTED
      default: 0,
      index: true
    },

    isDeleted: {
      type: Number,
      enum: [0, 1],
      default: 0,
      index: true
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Indexes ---------------- */
doctorSchema.index({ username: 1 });
doctorSchema.index({ verificationStatus: 1 });
doctorSchema.index({ isOnline: 1 });
doctorSchema.index({ isDeleted: 1 });

/* ---------------- Password Hashing ---------------- */
doctorSchema.pre("save", async function (next) {
  if (!this.isModified("password")) return next();

  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
  next();
});

/* ---------------- Instance Methods ---------------- */
doctorSchema.methods.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

/* ---------------- Query Middleware (Soft Delete) ---------------- */
doctorSchema.pre(/^find/, function (next) {
  this.where({ isDeleted: 0 });
  next();
});

export const Doctor = mongoose.model("Doctor", doctorSchema);
