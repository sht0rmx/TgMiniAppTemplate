import { Router } from "express";
import current from "./current.js";

const router = Router();

router.use("/current", current)

export default router;