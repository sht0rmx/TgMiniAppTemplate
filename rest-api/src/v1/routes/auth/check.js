import { authMiddleware } from "../../../middleware/auth.js";

import { Router } from "express";
import { Utils } from "../../../services/auth/index.js";

const router = Router();


router.get("/", authMiddleware, async (req, res) => {
    /*
    #swagger.path = '/api/v1/auth/check'
    #swagger.tags = ["Auth"]
    #swagger.description = 'get user data from JWT token and validate active session'
    */
  try {
    const user = req.user;

    res.json({
      id: user.id.toString(),
      telegram_id: user.telegram_id,
      username: user.username,
      name: user.name,
      avatar_url: user.avatar_url,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Internal server error" });
  }
});

router.post("/bot", authMiddleware, async (req, res) => {
    /*
    #swagger.path = '/api/v1/auth/check/bot'
    #swagger.tags = ["Auth"]
    #swagger.description = 'validate apiToken'
    */
  try {
    const authHeader = req.headers["authorization"];
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(403).json({ detail: "Invalid API token" });
    }

    const token = authHeader.split(" ")[1];
    if (!Utils.checkApiKey(token)) {
      return res.status(403).json({ detail: "Invalid API token" });
    }

    res.json({ status: "ok" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Internal server error" });
  }
});

export default router;
