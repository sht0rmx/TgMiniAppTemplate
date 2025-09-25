import dotenv from "dotenv";
import "module-alias/register.js";
import express from "express";
import cors from "cors";
import swaggerUi from "swagger-ui-express";
import swaggerDocument from "./swagger.json" with { type: "json" };

import v1Router from "./v1/routes/index.js";
import v1AuthRouter from "./v1/routes/auth.js";
import v1TokenRouter from "./v1/routes/tokens.js";

dotenv.config();

const app = express();

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || "localhost";

const corsOptions = {
  origin: [
    "http://localhost",
    "http://192.168.31.140",
    "https://miniapp.snipla.com",
  ],
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));
app.use(express.json());

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));
app.use("/api/v1", v1Router);
app.use("/api/v1/auth", v1AuthRouter);
app.use("/api/v1/auth/token", v1TokenRouter);

app.listen(PORT, HOST, () => {
  console.log(`API is listening on ${HOST}:${PORT}`);
});
