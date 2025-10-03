import crypto from "crypto";
import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";
import {AppDataSource} from "../database/index.js";
import {RefreshSession} from "../database/entities/RefreshSession.js";
import {User} from "../database/entities/User.js";
import {v4 as uuid_v4} from "uuid";

const FP_SECRET = process.env.FP_SECRET || "fp-secret-change";
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_ALG = process.env.JWT_ALG || "HS256";

export class AuthService {
    constructor() {
    }

    makeFingerprintToken(ua = "", ip = "") {
        const rnd = crypto.randomBytes(16).toString("hex");
        const base = `${ua}|${ip}|${rnd}`;
        const sig = crypto.createHmac("sha256", FP_SECRET).update(base).digest("hex");
        return Buffer.from(`${rnd}.${sig}`).toString("base64url");
    }

    checkFingerprintToken(fpToken, ua = "", ip = "") {
        try {
            const dec = Buffer.from(fpToken, "base64url").toString("utf8");
            const [rnd, sig] = dec.split(".");
            if (!rnd || !sig) return false;
            const base = `${ua}|${ip}|${rnd}`;
            const want = crypto.createHmac("sha256", FP_SECRET).update(base).digest("hex");
            // timing-safe compare
            return crypto.timingSafeEqual(Buffer.from(want), Buffer.from(sig));
        } catch (e) {
            return false;
        }
    }

    fingerprintHash(fpToken) {
        return crypto.createHash("sha256").update(String(fpToken)).digest("hex");
    }

    async UpdateUser({telegramId, username, firstname, photo, ua = "web", ip = "0.0.0.0", fpToken = null}) {
        const userRepo = AppDataSource.getRepository(User);

        let user = await userRepo.findOne({where: {telegram_id: telegramId}});

        if (!user) {
            user = userRepo.create({
                telegram_id: telegramId,
                name: firstname,
                username,
                avatar_url: photo,
                role: "user",
            });
        } else {
            user.username = username;
            user.name = firstname;
            user.avatar_url = photo;
        }

        user = await userRepo.save(user);

        const fpHash = this.fingerprintHash(fpToken || "");
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        const exist = await sessionRepo.findOne({
            where: {userId: user.id, fingerprint: fpHash, revoked: false},
        });

        if (exist) return await this.reuseSession(exist, user);

        return await this.createSession(user, ua, ip, fpToken);
    }


    async reuseSession(session, user) {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        session.lastUsed = new Date();
        await sessionRepo.save(session);

        const accessToken = this._genToken(
            String(user.telegram_id),
            String(session.id),
            user.role,
            "30m"
        );

        return {
            user,
            session,
            tokens: {
                access_token: accessToken,
                refresh_token: null,
            },
        };
    }

    async createSession(user, ua, ip, fpToken) {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        if (!user.id) {
            const userRepo = AppDataSource.getRepository(User);
            user = await userRepo.save(user); // гарантируем наличие id
        }

        const refreshRaw = uuid_v4();
        const refreshHash = await bcrypt.hash(refreshRaw, 10);
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

        const session = sessionRepo.create({
            userId: user.id, // теперь точно есть
            refreshTokenHash: refreshHash,
            fingerprint: this.fingerprintHash(fpToken || ""),
            user_agent: ua,
            ip,
            expiresIn: expiresAt,
            revoked: false,
            lastUsed: new Date(),
        });

        await sessionRepo.save(session);

        const accessToken = this._genToken(String(user.telegram_id), String(session.id), "user", "30m");

        return {
            user,
            session,
            tokens: {
                access_token: accessToken,
                refresh_token: refreshRaw,
            },
        };
    }


    async refreshTokens(refreshRaw, fpToken) {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        const sessions = await sessionRepo.find({where: {}, relations: ["user"]});
        let found = null;
        for (const s of sessions) {
            const ok = await bcrypt.compare(refreshRaw, s.refreshTokenHash);
            if (ok) {
                found = s;
                break;
            }
        }
        if (!found) throw new Error("Invalid refresh token");

        if (found.revoked) throw new Error("Refresh revoked");

        const expectedFpHash = this.fingerprintHash(fpToken);
        if (found.fingerprint !== expectedFpHash) {
            found.revoked = true;
            await sessionRepo.save(found);
            throw new Error("Fingerprint mismatch");
        }

        if (found.expiresIn < new Date()) {
            await sessionRepo.remove(found);
            throw new Error("Refresh token expired");
        }

        const newRefreshRaw = uuid_v4();
        found.refreshTokenHash = await bcrypt.hash(newRefreshRaw, 10);
        found.expiresIn = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        found.lastUsed = new Date();
        await sessionRepo.save(found);

        const user = found.user;
        const newAccess = this._genToken(String(user.telegram_id), String(found.id), "user", "30m");

        return {
            user,
            tokens: {
                access_token: newAccess,
                refresh_token: newRefreshRaw,
            },
        };
    }

    _genToken(userId, sessionId, role = "user", expiresIn = "60d") {
        return jwt.sign(
            {sub: String(userId), sid: String(sessionId), role: String(role)},
            JWT_SECRET,
            {
                algorithm: JWT_ALG,
                expiresIn,
            }
        );
    }

    checkAdminToken(token) {
        return token === process.env.API_TOKEN;
    }

    async checkValidateInitData(hashStr, initData, token, cStr = "WebAppData") {
        const sortedData = initData
            .split("&")
            .filter((chunk) => !chunk.startsWith("hash="))
            .map((chunk) => chunk.split("="))
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([key, value]) => `${key}=${decodeURIComponent(value)}`)
            .join("\n");

        const secretKey = new Uint8Array(
            crypto.createHmac("sha256", cStr).update(token).digest()
        );

        const dataCheck = crypto.createHmac("sha256", new Uint8Array(secretKey))
            .update(sortedData)
            .digest("hex");

        return dataCheck === hashStr;
    }

    parseInitData(initData) {
        const params = Object.fromEntries(
            initData
                .split("&")
                .map((x) => x.split("="))
                .filter((x) => x.length === 2)
        );

        if (params.user) {
            try {
                const rawUser = decodeURIComponent(params.user);
                params.user = JSON.parse(rawUser);
            } catch {
                params.user = null;
            }
        }

        return params;
    }
}