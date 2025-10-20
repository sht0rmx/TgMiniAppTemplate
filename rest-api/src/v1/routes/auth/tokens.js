import {AppDataSource} from "../../../database/index.js";
import {RefreshSession} from "../../../database/entities/RefreshSession.js";
import { Session } from "../../../services/session/index.js";
import {Router} from "express";
import bcrypt from "bcrypt";
import {authMiddleware} from "../../../middleware/auth.js";

const router = Router();

router.get("/refresh", async (req, res) => {
    /*
    #swagger.path = '/api/v1/auth/token/refresh'
    #swagger.tags = []
    #swagger.description = 'get access JWT token from session token & fingerprint'
    */
    try {
        const refreshToken = req.cookies.refreshToken;
        if (!refreshToken) {
            return res.status(401).json({error: "No refresh token"});
        }

        const fpToken = req.cookies.fp;
        if (!fpToken) return res.status(401).json({error: "No fp"});

        const ua = req.headers["user-agent"] || "web";


        const {user, tokens} = await Session.refreshTokens(refreshToken, fpToken, ua);

        res.cookie("refreshToken", tokens.refresh_token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            maxAge: 7 * 24 * 60 * 60 * 1000,
        });

        res.cookie("fp", fpToken, {
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
        return res.status(401).json({error: err.message});
    }
});

router.get("/revoke", authMiddleware, async (req, res) => {
    /*
    #swagger.path = '/api/v1/auth/token/revoke'
    #swagger.tags = ["Auth"]
    #swagger.description = 'close session and mark session token "revoked"'
    */
    try {
        const refreshToken = req.cookies.refreshToken;
        if (!refreshToken) {
            return res.status(400).json({error: "No refresh token"});
        }

        const sessionRepo = AppDataSource.getRepository(RefreshSession);
        const sessions = await sessionRepo.find();
        for (const s of sessions) {
            const ok = await bcrypt.compare(refreshToken, s.refreshTokenHash);
            if (ok) {
                s.revoked = true;
                await sessionRepo.save(s);
                break;
            }
        }

        res.clearCookie("refreshToken", {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
        });

        res.clearCookie("fp", {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
        });

        return res.json({status: "revoked"});
    } catch (err) {
        console.error(err);
        return res.status(500).json({error: "Server error"});
    }
});

export default router;