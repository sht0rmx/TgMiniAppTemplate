import { Tokens } from "../../../services/auth/index.js";
import { Router } from "express";

const router = Router();


router.get("/generate", (req, res) => {
    /*
    #swagger.path = '/api/v1/auth/fingerprint/generate'
    #swagger.tags = []
    #swagger.description = 'generate fingerprint for browser and set it in httpOnly cookie'
    */
  try {
    const ua = req.headers["user-agent"] || "web";
    const ip = req.ip || req.headers["x-forwarded-for"]?.split(",")[0] || "0.0.0.0";
    const fp = Tokens.makeFingerprintToken(ua, ip);
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

export default router;