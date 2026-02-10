import mongoose from "mongoose";

const doctorAvailabilitySchema = new mongoose.Schema(
  {
    doctorId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Doctor",
      required: true,
      index: true
    },

    day: {
      type: String,
      required: true,
      enum: [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
      ],
      lowercase: true,
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
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Compound Index ---------------- */
doctorAvailabilitySchema.index(
  { doctorId: 1, day: 1, startTime: 1, endTime: 1 },
  { unique: true }
);

/* ---------------- Validation ---------------- */
doctorAvailabilitySchema.pre("save", function (next) {
  if (this.startTime >= this.endTime) {
    return next(new Error("startTime must be before endTime"));
  }
  next();
});

export const DoctorAvailability = mongoose.model(
  "DoctorAvailability",
  doctorAvailabilitySchema
);
