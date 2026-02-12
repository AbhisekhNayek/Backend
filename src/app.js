import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";

import healthRoutes from "./routes/health.routes.js";
import authRoutes from "./routes/auth.routes.js";
import userAuthRoutes from "./routes/user.auth.routes.js";

import { errorHandler } from "./middlewares/error.middleware.js";

const app = express();

/* ---------- Global Middlewares ---------- */
app.use(express.json());
app.use(cors());
app.use(helmet());
app.use(morgan("dev"));

/* ---------- Routes ---------- */
app.use("/api/health", healthRoutes);
app.use("/api/auth", authRoutes);
app.use("/api/user/auth", userAuthRoutes);

/* ---------- Error Handler ---------- */
app.use(errorHandler);

export default app;
