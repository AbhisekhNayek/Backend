import { Router } from "express";
import {
  registerUser,
  verifyEmailOtp,
  loginUser,
  getAllUsers,
  getUserById,
  updateUser,
  deleteUser
} from "../controllers/user.controller.js";

import { authMiddleware } from "../middlewares/auth.middleware.js";

const router = Router();

/* ===============================
   PUBLIC ROUTES
=============================== */

router.post("/register", registerUser);
router.post("/verify-otp", verifyEmailOtp);
router.post("/login", loginUser);

/* ===============================
   PROTECTED ROUTES
=============================== */

/* Get logged-in user profile */
router.get("/me", authMiddleware, getUserById);

/* ===============================
   ADMIN ONLY ROUTES
=============================== */

router.get(
  "/",
  authMiddleware,
  (req, res, next) => {
    if (req.user.role !== "ADMIN") {
      return res.status(403).json({ message: "Access denied" });
    }
    next();
  },
  getAllUsers
);

router.get(
  "/:id",
  authMiddleware,
  getUserById
);

router.put(
  "/:id",
  authMiddleware,
  updateUser
);

router.delete(
  "/:id",
  authMiddleware,
  deleteUser
);

export default router;