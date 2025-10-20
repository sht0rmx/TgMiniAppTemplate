import { Router } from "express";
import fingerprintRouter from "./fingerprint.js";
import checkRouter from "./check.js";
import tokensRouter from "./tokens.js";
import loginRouter from "./login.js";

const router = Router();

router.use("/fingerprint", fingerprintRouter);
router.use("/check", checkRouter)
router.use("/token", tokensRouter)
router.use("/login", loginRouter)

export default router;