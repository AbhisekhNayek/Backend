import mongoose from "mongoose";

const bookingSchema = new mongoose.Schema(
  {
    bookingType: {
      type: String,
      required: true,
      enum: ["DOCTOR", "NURSE"],
      index: true
    },

    mode: {
      type: String,
      required: true,
      enum: ["VIDEO", "CLINIC", "HOME"]
    },

    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    },

    providerType: {
      type: String,
      required: true,
      enum: ["DOCTOR", "NURSE"],
      index: true
    },

    providerId: {
      type: mongoose.Schema.Types.ObjectId,
      required: true,
      refPath: "providerType" // Dynamic reference (Doctor / Nurse)
    },

    bookingDate: {
      type: Date,
      required: true,
      index: true
    },

    startTime: {
      type: String,
      required: true,
      match: [/^([01]\d|2[0-3]):([0-5]\d)$/, "Invalid time format (HH:mm)"]
    },

    endTime: {
      type: String,
      required: true,
      match: [/^([01]\d|2[0-3]):([0-5]\d)$/, "Invalid time format (HH:mm)"]
    },

    nurseDurationType: {
      type: String,
      enum: ["HOURLY", "DAILY", "MONTHLY"]
    },

    nurseDurationValue: {
      type: Number,
      min: 1
    },

    status: {
      type: String,
      enum: ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"],
      default: "PENDING",
      index: true
    },

    chatEnabledAt: {
      type: Date
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Compound Indexes ---------------- */
bookingSchema.index({
  providerId: 1,
  bookingDate: 1,
  startTime: 1,
  endTime: 1
});

/* ---------------- Validations ---------------- */
bookingSchema.pre("save", function (next) {
  if (this.startTime >= this.endTime) {
    return next(new Error("startTime must be before endTime"));
  }

  // Nurse-only duration validation
  if (this.bookingType === "NURSE" && !this.nurseDurationType) {
    return next(new Error("nurseDurationType is required for nurse bookings"));
  }

  next();
});

export const Booking = mongoose.model("Booking", bookingSchema);
