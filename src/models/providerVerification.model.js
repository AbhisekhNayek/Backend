import mongoose from "mongoose";

const providerVerificationSchema = new mongoose.Schema(
  {
    providerType: {
      type: String,
      required: true,
      enum: ["DOCTOR", "NURSE"],
      index: true
    },

    providerId: {
      type: mongoose.Schema.Types.ObjectId,
      required: true,
      refPath: "providerType",
      index: true
    },

    documentUrl: {
      type: String,
      required: true,
      trim: true,
      maxlength: 255
    },

    status: {
      type: String,
      enum: ["PENDING", "APPROVED", "REJECTED"],
      default: "PENDING",
      index: true
    },

    adminId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Admin"
    },

    remarks: {
      type: String,
      trim: true
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Indexes ---------------- */
providerVerificationSchema.index({
  providerType: 1,
  providerId: 1,
  status: 1
});

/* ---------------- Lifecycle Validation ---------------- */
providerVerificationSchema.pre("save", function (next) {
  if (this.status !== "PENDING" && !this.adminId) {
    return next(
      new Error("adminId is required for APPROVED or REJECTED verifications")
    );
  }
  next();
});

export const ProviderVerification = mongoose.model(
  "ProviderVerification",
  providerVerificationSchema
);
