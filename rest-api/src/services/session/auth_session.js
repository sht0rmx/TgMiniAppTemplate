import crypto from "crypto";
import { v4 as uuid_v4 } from "uuid";
import { AppDataSource } from "../../database/index.js";
import { RefreshSession } from "../../database/entities/RefreshSession.js";
import { User } from "../../database/entities/User.js";
import { genToken, fingerprintHash } from "../auth/tokens.js";

const HMAC_SECRET = process.env.HMAC_SECRET;

export async function hashToken(token) {
    return crypto.createHmac("sha256", HMAC_SECRET).update(token).digest("hex");
}

export async function reuseSession(session, user) {
    const repo = AppDataSource.getRepository(RefreshSession);
    session.lastUsed = new Date();
    await repo.save(session);

    const access = genToken(String(user.telegram_id), String(session.id), user.role, "30m");
    return { user, session, tokens: { access_token: access, refresh_token: null } };
}

export async function createSession(user, ua, ip, fpToken) {
    const repo = AppDataSource.getRepository(RefreshSession);

    if (!user.id) {
        const userRepo = AppDataSource.getRepository(User);
        user = await userRepo.save(user);
    }

    const raw = uuid_v4();
    const hash = await hashToken(raw);
    const exp = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    const s = repo.create({
        userId: user.id,
        refreshTokenHash: hash,
        fingerprint: fingerprintHash(fpToken || ""),
        user_agent: ua,
        ip,
        expiresIn: exp,
        revoked: false,
        lastUsed: new Date(),
    });

    await repo.save(s);
    const access = genToken(String(user.telegram_id), String(s.id), "user", "30m");
    return { user, session: s, tokens: { access_token: access, refresh_token: raw } };
}

export async function refreshTokens(refreshRaw, fpToken) {
    const repo = AppDataSource.getRepository(RefreshSession);
    const tokenHash = await hashToken(refreshRaw);

    const found = await repo.findOne({ where: { refreshTokenHash: tokenHash }, relations: ["user"] });
    if (!found) throw new Error("Invalid refresh token");
    if (found.revoked) throw new Error("Refresh revoked");

    const expectedFp = fingerprintHash(fpToken);
    if (found.fingerprint !== expectedFp) {
        found.revoked = true;
        await repo.save(found);
        throw new Error("Fingerprint mismatch");
    }

    if (found.expiresIn < new Date()) {
        await repo.remove(found);
        throw new Error("Refresh expired");
    }

    const newRaw = uuid_v4();
    found.refreshTokenHash = await hashToken(newRaw);
    found.expiresIn = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    found.lastUsed = new Date();
    await repo.save(found);

    const user = found.user;
    const newAccess = genToken(String(user.telegram_id), String(found.id), "user", "30m");

    return { user, tokens: { access_token: newAccess, refresh_token: newRaw } };
}
