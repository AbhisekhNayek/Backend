import jwt from "jsonwebtoken";
import { Doctor } from "../models/doctor.model.js";

/* ================================
   CREATE DOCTOR (ADMIN)
================================ */

export const createDoctor = async (req, res) => {
  try {

    const existing = await Doctor.findOne({
      $or: [
        { username: req.body.username },
        { email: req.body.email }
      ]
    });

    if (existing) {
      return res.status(400).json({
        message: "Doctor already exists"
      });
    }

    const doctor = await Doctor.create(req.body);

    res.status(201).json({
      success: true,
      doctor
    });

  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   DOCTOR LOGIN
================================ */

export const loginDoctor = async (req, res) => {
  try {
    const { username, password } = req.body;

    const doctor = await Doctor.findOne({ username }).select("+password");

    if (!doctor) {
      return res.status(400).json({
        message: "Invalid credentials",
      });
    }

    const isMatch = await doctor.comparePassword(password);

    if (!isMatch) {
      return res.status(400).json({
        message: "Invalid credentials",
      });
    }

    const token = jwt.sign(
      {
        id: doctor._id,
        role: "DOCTOR",
      },
      process.env.JWT_SECRET,
      { expiresIn: "7d" },
    );

    doctor.password = undefined;

    res.json({
      success: true,
      token,
      doctor,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   GET ALL DOCTORS
================================ */

export const getAllDoctors = async (req, res) => {
  try {
    const doctors = await Doctor.find();

    res.json({
      success: true,
      count: doctors.length,
      doctors,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   GET DOCTOR BY ID
================================ */

export const getDoctorById = async (req, res) => {
  try {
    const doctor = await Doctor.findById(req.params.id);

    if (!doctor) {
      return res.status(404).json({
        message: "Doctor not found",
      });
    }

    res.json({
      success: true,
      doctor,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   UPDATE DOCTOR
================================ */

export const updateDoctor = async (req, res) => {
  try {
    const doctor = await Doctor.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
    });

    if (!doctor) {
      return res.status(404).json({
        message: "Doctor not found",
      });
    }

    res.json({
      success: true,
      doctor,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

/* ================================
   DELETE DOCTOR (SOFT DELETE)
================================ */

export const deleteDoctor = async (req, res) => {
  try {
    await Doctor.findByIdAndUpdate(req.params.id, { isDeleted: 1 });

    res.json({
      success: true,
      message: "Doctor deleted successfully",
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
