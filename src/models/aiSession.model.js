import mongoose from "mongoose";

const aiSessionSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    },

    mode: {
      type: String,
      required: true,
      enum: ["GENERAL", "LAB", "WOMENS"],
      index: true
    },

    inputText: {
      type: String,
      trim: true
    },

    inputFile: {
      type: String,
      trim: true,
      maxlength: 255
    },

    aiSummary: {
      type: String,
      trim: true
    },

    aiRecommendation: {
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
aiSessionSchema.index({ userId: 1, mode: 1 });
aiSessionSchema.index({ created_at: -1 });

export const AiSession = mongoose.model("AiSession", aiSessionSchema);
