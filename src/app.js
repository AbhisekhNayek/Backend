import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";

import healthRoutes from "./routes/health.routes.js";
import userRoutes from "./routes/user.routes.js";

import { errorHandler } from "./middlewares/error.middleware.js";

const app = express();

/* ===============================
   GLOBAL MIDDLEWARES
=============================== */

app.use(express.json({ limit: "10kb" }));
app.use(cors());
app.use(helmet());
app.use(morgan("dev"));

/* ===============================
   ROUTES
=============================== */

app.use("/api/health", healthRoutes);
app.use("/api/users", userRoutes);

/* ===============================
   404 HANDLER
=============================== */
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: "Route not found"
  });
});

/* ===============================
   ERROR HANDLER
=============================== */
app.use(errorHandler);

export default app;