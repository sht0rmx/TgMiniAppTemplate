import { AuthService as AuthServ } from "../../../services/AuthService.js";
import { authMiddleware } from "../../../middleware/auth.js";

import { Router } from "express";
import { body } from "express-validator";
import AppDataSource from "../../../database/index.js";
import {RefreshSession} from "../../../database/entities/RefreshSession.js";

const router = Router();
const authService = new AuthServ();

router.get("/fingerprint/generate", (req, res) => {
  try {
    const ua = req.headers["user-agent"] || "web";
    const ip = req.ip || req.headers["x-forwarded-for"]?.split(",")[0] || "0.0.0.0";
    const fp = authService.makeFingerprintToken(ua, ip);
    res.cookie("fp", fp, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });
    return res.json({ ok: 1 });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ detail: "Internal server error" });
  }
});

router.post("/webapp", body("initData").exists(), async (req, res) => {
  try {
    const { initData } = req.body;
    const botToken = process.env.BOT_TOKEN;

    const params = authService.parseInitData(initData);
    const hashStr = params.hash;
    delete params.hash;

    if (!hashStr || !(await authService.checkValidateInitData(hashStr, initData, botToken))) {
      return res.status(401).json({ detail: "Invalid Telegram initData" });
    }

    const userInfo = params.user || {};
    const telegramId = parseInt(userInfo.id || 0);
    const username = userInfo.username || "";
    const firstname = userInfo.first_name || "";
    const photo = userInfo.photo_url || null;

    const ua = req.headers["user-agent"] || "web";
    const ip = req.ip || req.headers["x-forwarded-for"]?.split(",")[0] || "0.0.0.0";

    let fpToken = req.cookies.fp;
    if (!fpToken || !authService.checkFingerprintToken(fpToken, ua, ip)) {
      fpToken = authService.makeFingerprintToken(ua, ip);
      res.cookie("fp", fpToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });
    }

    const {user, session, tokens} = await authService.UpdateUser({
      telegramId,
      username,
      firstname,
      photo,
      ua,
      ip,
      fpToken,
    });

    if (tokens.refresh_token) {
      res.cookie("refreshToken", tokens.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });
    }
    res.json({
      tokens,
      user: {
        id: user.id,
        telegram_id: user.telegram_id,
        username: user.username,
        name: user.name,
        avatar_url: user.avatar_url,
        role: user.role,
      },
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Internal server error" });
  }
});

router.post("/check/bot", async (req, res) => {
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

router.get("/check", authMiddleware, async (req, res) => {
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

export default router;