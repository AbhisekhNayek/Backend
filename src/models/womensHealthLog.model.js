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

export const WomensHealthLog = mongoose.model(
  "WomensHealthLog",
  womensHealthLogSchema
);
