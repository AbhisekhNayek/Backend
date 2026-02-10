import mongoose from "mongoose";

const paymentSchema = new mongoose.Schema(
  {
    bookingId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Booking",
      required: true,
      index: true
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
      refPath: "providerType"
    },

    totalAmount: {
      type: Number,
      required: true,
      min: 0
    },

    platformFee: {
      type: Number,
      required: true,
      min: 0
    },

    providerAmount: {
      type: Number,
      required: true,
      min: 0
    },

    paymentMode: {
      type: String,
      required: true,
      enum: [
        "UPI",
        "CARD",
        "NET_BANKING",
        "WALLET",
        "CASH"
      ]
    },

    gatewayRef: {
      type: String,
      trim: true,
      maxlength: 100,
      index: true
    },

    status: {
      type: String,
      enum: ["SUCCESS", "FAILED", "PENDING"],
      default: "PENDING",
      index: true
    }
  },
  {
    timestamps: { createdAt: "created_at", updatedAt: false },
    versionKey: false
  }
);

/* ---------------- Compound Indexes ---------------- */
paymentSchema.index({ bookingId: 1, status: 1 });
paymentSchema.index({ providerId: 1, status: 1 });

/* ---------------- Validations ---------------- */
paymentSchema.pre("save", function (next) {
  const calculatedTotal = this.platformFee + this.providerAmount;

  if (this.totalAmount !== calculatedTotal) {
    return next(
      new Error("totalAmount must equal platformFee + providerAmount")
    );
  }

  next();
});

export const Payment = mongoose.model("Payment", paymentSchema);
