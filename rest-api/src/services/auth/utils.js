import crypto from "crypto";

export function checkApiKey(rawKey, apiKeyHash) {
    if (!rawKey) return false;
    const hash = crypto.createHash("sha256").update(rawKey).digest("hex");
    return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(apiKeyHash));
}

export async function checkValidateInitData(hashStr, initData, token, cStr = "WebAppData") {
    const sortedData = initData
        .split("&")
        .filter((x) => !x.startsWith("hash="))
        .map((x) => x.split("="))
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([k, v]) => `${k}=${decodeURIComponent(v)}`)
        .join("\n");

    const secretKey = crypto.createHmac("sha256", cStr).update(token).digest();
    const dataCheck = crypto.createHmac("sha256", secretKey).update(sortedData).digest("hex");

    return dataCheck === hashStr;
}

export function parseInitData(initData) {
    const params = Object.fromEntries(initData.split("&").map(x => x.split("=")).filter(x => x.length === 2));
    if (params.user) {
        try {
            params.user = JSON.parse(decodeURIComponent(params.user));
        } catch { params.user = null; }
    }
    return params;
}
