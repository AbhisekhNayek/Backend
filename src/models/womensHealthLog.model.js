import mongoose from "mongoose";

const womensHealthLogSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    },

    cycleStart: {
      type: Date,
      required: true
    },

    cycleEnd: {
      type: Date,
      required: true
    },

    isFreePackageEligible: {
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
womensHealthLogSchema.index({ userId: 1, created_at: -1 });

/* ---------------- Validations ---------------- */
womensHealthLogSchema.pre("save", function (next) {
  if (this.cycleStart >= this.cycleEnd) {
    return next(new Error("cycleStart must be before cycleEnd"));
  }
  next();
});

export const WomensHealthLog = mongoose.model(
  "WomensHealthLog",
  womensHealthLogSchema
);
