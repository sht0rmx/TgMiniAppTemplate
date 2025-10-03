import jwt from "jsonwebtoken";
import crypto from "crypto";
import { AppDataSource } from "../database/index.js";
import { RefreshSession } from "../database/entities/RefreshSession.js";

export async function authMiddleware(req, res, next) {
    const authHeader = req.headers["authorization"];
    if (!authHeader?.startsWith("Bearer ")) {
        return res.status(401).json({ detail: "Missing token" });
    }

    const token = authHeader.split(" ")[1];
    let payload;
    try {
        payload = jwt.verify(token, process.env.JWT_SECRET);
    } catch {
        return res.status(401).json({ detail: "Invalid token" });
    }

    const telegramId = parseInt(payload.sub);
    const sessionId = payload.sid;
    if (!telegramId || !sessionId) {
        return res.status(401).json({ detail: "Invalid token payload" });
    }

    try {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);
        const session = await sessionRepo.findOne({
            where: { id: sessionId },
            relations: ["user"],
        });

        if (!session) return res.status(401).json({ detail: "Session not found" });
        if (session.expiresIn < new Date()) {
            await sessionRepo.remove(session);
            return res.status(401).json({ detail: "Session expired" });
        }

        const ua = req.headers["user-agent"] || "web";
        if (session.user_agent && session.user_agent !== ua) {
            return res.status(401).json({ detail: "User-agent mismatch" });
        }

        const fp = req.cookies.fp || "default";
        const fpHash = crypto.createHash("sha256").update(String(fp)).digest("hex");

        if (session.fingerprint !== fpHash) {
            return res.status(401).json({ detail: "Fingerprint mismatch" });
        }

        req.user = session.user;
        req.session = session;
        req.role = payload.role || "user";
        next();
    } catch (err) {
        console.error(err);
        res.status(500).json({ detail: "Internal server error" });
    }
}

export function roleMiddleware(requiredRole) {
    return (req, res, next) => {
        if (!req.user) return res.status(401).json({ detail: "Unauthorized" });
        if (req.role !== requiredRole)
            return res.status(403).json({ detail: "Forbidden" });
        next();
    };
}