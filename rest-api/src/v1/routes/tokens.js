import { AuthService as AuthServ } from "../../services/AuthService.js";
import { AppDataSource } from "../../database/index.js";
import {RefreshSession} from "../../database/entities/RefreshSession.js";
import {Router} from "express";

const router = Router();
const authService = new AuthServ();

router.post("/refresh", async (req, res) => {
  try {
    const refreshToken = req.body.refresh_token || req.cookies.refreshToken;
    if (!refreshToken) {
      return res.status(401).json({ error: "No refresh token" });
    }

    const fingerprint = req.body.fingerprint || req.headers["user-agent"] || "default";
    const { user, tokens } = await authService.refreshTokens(refreshToken, fingerprint);

    res.cookie("refreshToken", tokens.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.json({
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      user,
    });
  } catch (err) {
    console.error(err);
    return res.status(401).json({ error: err.message });
  }
});

router.post("/revoke", async (req, res) => {
  try {
    const refreshToken = req.cookies.refreshToken;
    if (!refreshToken) {
      return res.status(400).json({ error: "No refresh token" });
    }

    const sessionRepo = AppDataSource.getRepository(RefreshSession);
    const session = await sessionRepo.findOne({ where: { refreshToken } });

    if (session) {
      await sessionRepo.remove(session);
    }

    res.clearCookie("refreshToken", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict"
    });

    return res.json({ status: "revoked" });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error" });
  }
});

export default router;
