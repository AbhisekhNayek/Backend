import app from "./app.js";
import { env } from "./config/dotenv.config.js";
import { connectDB } from "./config/db.config.js";

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
