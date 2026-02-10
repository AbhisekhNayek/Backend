import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    mobile: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      maxlength: 15,
      index: true
    },

    isMobileVerified: {
      type: Boolean,
      enum: [true, false],
      default: false
    },

    name: {
      type: String,
      trim: true,
      maxlength: 50
    },

    email: {
      type: String,
      lowercase: true,
      trim: true,
      maxlength: 100,
      match: [/^\S+@\S+\.\S+$/, "Invalid email format"],
      sparse: true
    },

    profilePic: {
      type: String,
      trim: true
    },

    gender: {
      type: String,
      enum: ["male", "female", "other"],
      lowercase: true
    },

    dob: {
      type: Date
    },

    location: {
      latitude: {
        type: Number
      },
      longitude: {
        type: Number
      }
    },

    isLocationGranted: {
      type: Number,
      enum: [0, 1],
      default: 0
    },

    isDeleted: {
      type: Number,
      enum: [0, 1],
      default: 0,
      index: true
    }
  },
  {
    timestamps: true,
    versionKey: false
  }
);

/* ---------------- Indexes ---------------- */
userSchema.index({ mobile: 1 });
userSchema.index({ isDeleted: 1 });

/* ---------------- Query Helpers ---------------- */
userSchema.pre(/^find/, function (next) {
  this.where({ isDeleted: 0 });
  next();
});

export const User = mongoose.model("User", userSchema);
