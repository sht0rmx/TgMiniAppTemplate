import { AuthService as AuthServ } from "../../services/AuthService.js";
import { AppDataSource } from "../../database/index.js";
import { User } from "../../database/entities/User.js";

import {Router} from "express";
import jwt from "jsonwebtoken";
import { body } from "express-validator";


const router = Router();
const authService = new AuthServ();


router.post("/webapp", body("initData").exists(), async (req, res) => {
  try {
    const { initData } = req.body;
    const botToken = process.env.BOT_TOKEN;

    const params = authService.parseInitData(initData);
    const hashStr = params.hash;
    delete params.hash;

    if (!hashStr || !(await authService.checkTelegramAuth(hashStr, initData, botToken))) {
      return res.status(401).json({ detail: "Invalid Telegram initData" });
    }

    const userInfo = params.user || {};
    const telegramId = parseInt(userInfo.id || 0);
    const username = userInfo.username || "";
    const firstname = userInfo.first_name || "";
    const photo = userInfo.photo_url || null;

    const ua = req.headers["user-agent"] || "web";
    const ip = req.ip || "0.0.0.0";

    const result = await authService.UpdateUser({
      telegramId,
      username,
      firstname,
      photo,
      fingerprint: req.body.fingerprint || "default",
      ua,
      ip,
    });

    const { user, tokens } = result;

    res.json({
      user: {
        id: user.id.toString(),
        telegram_id: user.telegram_id,
        username: user.username,
        name: user.name,
        avatar_url: user.avatar_url,
      },
      tokens,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Internal server error" });
  }
});


router.post("/bot", async (req, res) => {
  try {
    const authHeader = req.headers["authorization"];
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(403).json({ detail: "Invalid API token" });
    }

    const token = authHeader.split(" ")[1];
    if (!authService.checkAdminToken(token)) {
      return res.status(403).json({ detail: "Invalid API token" });
    }

    res.json({ status: "ok" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Internal server error" });
  }
});


router.get("/check", async (req, res) => {
  try {
    const authHeader = req.headers["authorization"];
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({ detail: "Missing token" });
    }

    const token = authHeader.split(" ")[1];
    let payload;
    try {
      payload = jwt.verify(token, process.env.JWT_SECRET);
    } catch (err) {
      return res.status(401).json({ detail: "Invalid token" });
    }

    const userId = payload.sub;
    if (!userId) {
      return res.status(401).json({ detail: "Invalid token payload" });
    }

    const userRepo = AppDataSource.getRepository(User);
    const user = await userRepo.findOneBy({ telegram_id: parseInt(userId) });

    if (!user) {
      return res.status(404).json({ detail: "User not found" });
    }

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

export default router;
