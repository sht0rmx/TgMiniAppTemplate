import dotenv from "dotenv";
dotenv.config();

import crypto from "crypto";
import jwt from "jsonwebtoken";

const FP_SECRET = process.env.FP_SECRET || "fp-secret-change";
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_ALG = process.env.JWT_ALG || "HS256";


export function makeFingerprintToken(ua = "", ip = "") {
    const rnd = crypto.randomBytes(16).toString("hex");
    const base = `${ua}|${ip}|${rnd}`;
    const sig = crypto.createHmac("sha256", FP_SECRET).update(base).digest("hex");
    return Buffer.from(`${rnd}.${sig}`).toString("base64url");
}

export function checkFingerprintToken(fpToken, ua = "", ip = "") {
    try {
        const dec = Buffer.from(fpToken, "base64url").toString("utf8");
        const [rnd, sig] = dec.split(".");
        if (!rnd || !sig) return false;
        const base = `${ua}|${ip}|${rnd}`;
        const want = crypto.createHmac("sha256", FP_SECRET).update(base).digest("hex");
        return crypto.timingSafeEqual(Buffer.from(want), Buffer.from(sig));
    } catch {
        return false;
    }
}

export function fingerprintHash(fpToken) {
    return crypto.createHash("sha256").update(String(fpToken)).digest("hex");
}

export function genToken(userId, sessionId, role = "user", expiresIn = "60d") {
    return jwt.sign(
        { sub: String(userId), sid: String(sessionId), role: String(role) },
        JWT_SECRET,
        { algorithm: JWT_ALG, expiresIn }
    );
}
