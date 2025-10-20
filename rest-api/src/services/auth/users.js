import { AppDataSource } from "../../database/index.js";
import { User } from "../../database/entities/User.js";
import { RefreshSession } from "../../database/entities/RefreshSession.js";
import { fingerprintHash } from "./tokens.js";
import { reuseSession, createSession } from "../session/auth_session.js";

export async function updateUser({ telegramId, username, firstname, photo, ua, ip, fpToken }) {
    const repo = AppDataSource.getRepository(User);
    let u = await repo.findOne({ where: { telegram_id: telegramId } });

    if (!u) {
        u = repo.create({ telegram_id: telegramId, name: firstname, username, avatar_url: photo, role: "user" });
    } else {
        u.username = username;
        u.name = firstname;
        u.avatar_url = photo;
    }

    u = await repo.save(u);

    const fpHash = fingerprintHash(fpToken || "");
    const sessRepo = AppDataSource.getRepository(RefreshSession);
    const exist = await sessRepo.findOne({ where: { userId: u.id, fingerprint: fpHash, revoked: false } });

    if (exist) return await reuseSession(exist, u);
    return await createSession(u, ua, ip, fpToken);
}
