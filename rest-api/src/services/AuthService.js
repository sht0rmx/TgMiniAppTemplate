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
        this.apiKeyHash = process.env.API_TOKEN_HASH;
        this.HMAC_SECRET = process.env.HMAC_SECRET;
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
        console.log(1)
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
        console.log(2)
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        if (!user.id) {
            const userRepo = AppDataSource.getRepository(User);
            user = await userRepo.save(user);
        }

        const refreshRaw = uuid_v4();
        const refreshHash = await this.hashToken(refreshRaw);
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

        const session = sessionRepo.create({
            userId: user.id,
            refreshTokenHash: refreshHash,
            fingerprint: this.fingerprintHash(fpToken || ""),
            user_agent: ua,
            ip,
            expiresIn: expiresAt,
            revoked: false,
            lastUsed: new Date(),
        });

        console.log(session);

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

    async hashToken(token) {
        console.log(3, token, this.HMAC_SECRET);
        let hash = crypto.createHmac("sha256", this.HMAC_SECRET).update(token).digest("hex");
        console.log(hash);
        return hash
    }

    async refreshTokens(refreshRaw, fpToken) {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);

        const tokenHash = await this.hashToken(refreshRaw);

        const found = await sessionRepo.findOne({
            where: {refreshTokenHash: tokenHash},
            relations: ["user"],
        });

        if (!found) throw new Error("Invalid refresh token");
        if (found.revoked) throw new Error("Refresh revoked");

        const expectedFpHash = this.fingerprintHash(fpToken)
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
        found.refreshTokenHash = await this.hashToken(newRefreshRaw);
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

    checkApiKey(rawKey) {
        if (!rawKey) return false;
        const hash = crypto.createHash("sha256").update(rawKey).digest("hex");
        return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(this.apiKeyHash));
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