import { Router } from "express";
import {
  createDoctor,
  loginDoctor,
  getAllDoctors,
  getDoctorById,
  updateDoctor,
  deleteDoctor
} from "../controllers/doctor.controller.js";

import { authMiddleware, adminOnly } from "../middlewares/auth.middleware.js";

const router = Router();

/* PUBLIC */

router.post("/login", loginDoctor);


/* PROTECTED */

router.post("/", authMiddleware, adminOnly, createDoctor);

router.get("/", getAllDoctors);

router.get("/:id", getDoctorById);

router.put("/:id", authMiddleware, updateDoctor);

router.delete("/:id", authMiddleware, deleteDoctor);

export default router;