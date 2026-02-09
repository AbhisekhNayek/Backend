import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";

import healthRoutes from "./routes/health.routes.js";
import { errorHandler } from "./middlewares/error.middleware.js";

const app = express();

/* ---------- Global Middlewares ---------- */
app.use(express.json());
app.use(cors());
app.use(helmet());
app.use(morgan("dev"));

/* ---------- Routes ---------- */
app.use("/api/health", healthRoutes);

/* ---------- Error Handler ---------- */
app.use(errorHandler);

export default app;
