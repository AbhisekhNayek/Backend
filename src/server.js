import express from "express";
import { env } from "./config/dotenv.config.js";
import { connectDB } from "./config/db.config.js";

const app = express();

/* -------------------- Middlewares -------------------- */
app.use(express.json());

/* -------------------- Health Check -------------------- */
app.get("/health", (req, res) => {
  res.status(200).json({
    success: true,
    message: "Server is running 🚀"
  });
});

/* -------------------- Start Server -------------------- */
const startServer = async () => {
  try {
    await connectDB();

    app.listen(env.port, () => {
      console.log(
        `🚀 Express server running on port ${env.port} [${env.nodeEnv}]`
      );
    });
  } catch (error) {
    console.error("❌ Failed to start server:", error.message);
    process.exit(1);
  }
};

startServer();
