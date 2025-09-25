import crypto from "crypto";
import jwt from "jsonwebtoken";
import {AppDataSource} from "../database/index.js";
import {RefreshSession} from "../database/entities/RefreshSession.js";
import {User} from "../database/entities/User.js";
import {v4 as uuid_v4} from "uuid";

export class AuthService {
    constructor() {
    }

    async getByTelegramId(telegramId) {
        const repo = AppDataSource.getRepository(User);
        return repo.findOne({where: {telegram_id: telegramId}});
    }

    async UpdateUser({telegramId, username, firstname, photo, fingerprint = "default", ua = "web", ip = "0.0.0.0"}) {
        const userRepo = AppDataSource.getRepository(User);
        let user = await userRepo.findOne({where: {telegram_id: telegramId}});

        if (!user) {
            user = userRepo.create({
                telegram_id: telegramId,
                name: firstname,
                username,
                avatar_url: photo,
            });
        } else {
            user.username = username;
            user.name = firstname;
            user.avatar_url = photo;
        }
        await userRepo.save(user);

        const accessToken = this._genToken(user.telegram_id, "30m");

        const sessionRepo = AppDataSource.getRepository(RefreshSession);
        const refreshToken = uuid_v4();
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 дней

        const session = sessionRepo.create({
            userId: user.id,
            refreshToken,
            fingerprint,
            user_agent: ua,
            ip,
            expiresIn: expiresAt,
        });
        await sessionRepo.save(session);

        return {
            user,
            tokens: {
                access_token: accessToken,
                refresh_token: refreshToken,
            },
        };
    }

    async refreshTokens(refreshToken, fingerprint = "default") {
        const sessionRepo = AppDataSource.getRepository(RefreshSession);
        const userRepo = AppDataSource.getRepository(User);

        const session = await sessionRepo.findOne({where: {refreshToken}});
        if (!session) throw new Error("Invalid refresh token");

        if (session.fingerprint !== fingerprint) {
            throw new Error("Fingerprint mismatch");
        }

        if (session.expiresIn < new Date()) {
            await sessionRepo.remove(session);
            throw new Error("Refresh token expired");
        }

        const user = await userRepo.findOne({where: {id: session.userId}});
        if (!user) throw new Error("User not found");

        const accessToken = this._genToken(user.telegram_id, "30m");

        const newRefreshToken = uuid_v4();
        session.refreshToken = newRefreshToken;
        session.expiresIn = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        await sessionRepo.save(session);

        return {
            user,
            tokens: {
                access_token: accessToken,
                refresh_token: newRefreshToken,
            },
        };
    }

    _genToken(userId, expiresIn = "60d") {
        return jwt.sign(
            {sub: String(userId)},
            process.env.JWT_SECRET,
            {
                algorithm: process.env.JWT_ALG || "HS256",
                expiresIn,
            }
        );
    }

    async checkTelegramAuth(hashStr, initData, token, cStr = "WebAppData") {
        const params = initData
            .split("&")
            .filter((chunk) => !chunk.startsWith("hash="))
            .map((chunk) => chunk.split("="))
            .sort((a, b) => a[0].localeCompare(b[0]));

        const dataCheckString = params.map((rec) => `${rec[0]}=${rec[1]}`).join("\n");

        const secretKey = crypto.createHmac("sha256", cStr).update(token).digest();
        const hmacDigest = crypto.createHmac("sha256", secretKey).update(dataCheckString).digest("hex");

        return crypto.timingSafeEqual(Buffer.from(hmacDigest, "hex"), Buffer.from(hashStr, "hex"));
    }

    checkAdminToken(token) {
        return token === process.env.API_TOKEN;
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
