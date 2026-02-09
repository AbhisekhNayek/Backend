import app from "./app.js";
import { env } from "./config/dotenv.config.js";

app.listen(env.port, () => {
  console.log(
    `Server Running On Port ${env.port} [${env.nodeEnv}]`
  );
});
