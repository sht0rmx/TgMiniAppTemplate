import "module-alias/register.js";
import express from "express";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import cors from "cors";
import swaggerUi from "swagger-ui-express";
import swaggerDocument from "./swagger.json" with { type: "json" };

import v1Router from "./v1/routes/index.js";
import v1AuthRouter from "./v1/routes/auth/index.js";
import v1TokenRouter from "./v1/routes/tokens.js";
import { AppDataSource } from "./database/index.js";
import { RefreshSession } from "./database/entities/RefreshSession.js";
import { storageClient } from "./minio/client.js";

const app = express();

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || "localhost";

const corsOptions = {
  origin: [
    "https://jlj73h8b-5173.euw.devtunnels.ms",
    "https://miniapp.snipla.com"
  ],
  credentials: true,
  optionsSuccessStatus: 200,
};

console.log("API: alowed origins: ", corsOptions.origin);

app.use(cors(corsOptions));
app.use(express.json());

app.use(express.json());
app.use(cookieParser());

morgan.token("body", (req) => JSON.stringify(req.body));
morgan.token("cookies", (req) => JSON.stringify(req.cookies));

app.use(
  morgan(
    ":method :url :status :res[content-length] - :response-time ms :body :cookies"
  )
);

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));
app.use("/api/v1", v1Router);
app.use("/api/v1/auth", v1AuthRouter);
app.use("/api/v1/auth/token", v1TokenRouter);


AppDataSource.initialize()
  .then(() => {
    console.log("DB: connected");

    const clearSessions = async () => {
      try {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);
        await sessionRepo
          .createQueryBuilder()
          .delete()
          .where("expiresIn < :now OR revoked = true", { now: new Date() })
          .execute();
        console.log("DB: old sessions cleaned up");
      } catch (err) {
        console.error("DB: session cleanup error:", err);
      }
    };

    clearSessions().then(r => null);
    setInterval(clearSessions, 1000 * 60 * 60);

    storageClient.init().then(r => null)

    app.listen(PORT, HOST, () => {
      console.log(`API: listening on ${HOST}:${PORT}`);
    });
  })
  .catch((err) => {
    console.error("DB init error:", err);
  });
