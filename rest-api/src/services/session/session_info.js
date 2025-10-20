import {AppDataSource} from "../../database/index.js";
import {RefreshSession} from "../../database/entities/RefreshSession.js";


export async function currentDevice(session_id) {
    const repo = AppDataSource.getRepository(RefreshSession)

    let session = await repo.findOne({where: {id: session_id}});

    let ua = session.user_agent.toLowerCase();

    let os = 'unknown', browser = 'unknown', dev = 'unknown', type = 'desktop';

    if (/android/i.test(ua)) os = 'android';
    else if (/windows nt/i.test(ua)) os = 'windows';
    else if (/linux/i.test(ua)) os = 'linux';
    else if (/mac os x/i.test(ua)) os = 'macos';
    else if (/iphone|ipad|ipod/i.test(ua)) os = 'ios';

    if (/mobile/i.test(ua)) type = 'mobile';
    else if (/tablet/i.test(ua)) type = 'tablet';

    if (/edg/i.test(ua)) browser = 'edge';
    else if (/chrome/i.test(ua)) browser = 'chrome';
    else if (/safari/i.test(ua) && !/chrome/i.test(ua)) browser = 'safari';
    else if (/firefox/i.test(ua)) browser = 'firefox';
    else if (/telegram/i.test(ua)) browser = 'telegram';

    let m = ua.match(/\(([^)]+)\)/g);
    if (m) {
        for (let x of m) {
            if (x.includes('honor') || x.includes('xiaomi') || x.includes('samsung') || x.includes('pixel'))
                dev = x.replace(/[()]/g, '').split(';').find(s => /honor|xiaomi|samsung|pixel/i.test(s))?.trim() || dev;
        }
    }

    return {
        "info": {"os": os, "browser": browser, "dev": dev, "type": type},
        "lastUsed": session.lastUsed,
        "ip": session.ip
    };
}

export async function getAllSessions(user_id) {
    const repo = AppDataSource.getRepository(RefreshSession)

    let sessions_list = await repo.find({where: {user_id: user_id}});
    console.log(sessions_list);
}