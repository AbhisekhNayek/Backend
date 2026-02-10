import mongoose from "mongoose";

const carePackageSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    },

    packageType: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50
    },

    status: {
      type: String,
      enum: ["TRIGGERED", "SHIPPED"],
      default: "TRIGGERED",
      index: true
    },

    triggeredAt: {
      type: Date,
      default: Date.now
    },

    shippedAt: {
      type: Date
    }
  },
  {
    timestamps: false,
    versionKey: false
  }
);

/* ---------------- Indexes ---------------- */
carePackageSchema.index({ userId: 1, status: 1 });

/* ---------------- Status Lifecycle Logic ---------------- */
carePackageSchema.pre("save", function (next) {
  if (this.status === "SHIPPED" && !this.shippedAt) {
    this.shippedAt = new Date();
  }
  next();
});

export const CarePackage = mongoose.model(
  "CarePackage",
  carePackageSchema
);
