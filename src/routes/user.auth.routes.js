import { Router } from "express";
import {
  sendOtp,
  verifyOtp
} from "../controllers/user.auth.controller.js";
import { authMiddleware } from "../middlewares/auth.middleware.js"

const router = Router();

router.post("/send-otp", sendOtp);
router.post("/verify-otp", verifyOtp);

export default router;
