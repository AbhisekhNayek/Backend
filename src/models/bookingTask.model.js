import mongoose from "mongoose";

const bookingTaskSchema = new mongoose.Schema(
  {
    bookingId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Booking",
      required: true,
      index: true
    },

    task: {
      type: String,
      required: true,
      trim: true,
      maxlength: 100
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Indexes ---------------- */
bookingTaskSchema.index({ bookingId: 1 });

export const BookingTask = mongoose.model(
  "BookingTask",
  bookingTaskSchema
);
