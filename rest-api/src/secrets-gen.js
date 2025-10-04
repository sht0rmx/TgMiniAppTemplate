import fs from "fs";
import path from "path";
import crypto from "crypto";

function randomHex(len = 32) {
    return crypto.randomBytes(len).toString("hex");
}

function generateApiKey() {
    return `sk_${randomHex(16)}`;
}

function hashApiKey(key) {
    return crypto.createHash("sha256").update(key).digest("hex");
}

function ensureEnv() {
    const envPath = path.resolve(".env");
    if (!fs.existsSync(envPath)) {
        const examplePath = path.resolve(".env.example");
        if (!fs.existsSync(examplePath)) {
            console.error("[!] .env.example not found! Cannot create .env");
            process.exit(1);
        }
        fs.copyFileSync(examplePath, envPath);
        console.log("[!] .env not found. Copied from .env.example");
    }
}

function updateEnv(vars) {
    const envPath = path.resolve(".env");
    let content = fs.readFileSync(envPath, "utf8");

    for (const [key, value] of Object.entries(vars)) {
        const regex = new RegExp(`${key}=.*`, "i");
        if (content.match(regex)) {
            content = content.replace(regex, `${key}="${value}"`);
        } else {
            content += `\n${key}="${value}"`;
        }
    }

    fs.writeFileSync(envPath, content, "utf8");
}

console.log("[-] Check .env file");
ensureEnv();

const apiKey = generateApiKey();
console.log("[-] Generated API key:", apiKey);

const apiHash = hashApiKey(apiKey);
console.log("[-] Computed API_TOKEN_HASH:", apiHash);

const fpSecret = randomHex(16);
console.log("[-] Generated FP_SECRET:", fpSecret);

const jwtSecret = randomHex(32);
console.log("[-] Generated JWT_SECRET:", jwtSecret);

updateEnv({
    API_TOKEN_HASH: apiHash,
    FP_SECRET: fpSecret,
    JWT_SECRET: jwtSecret,
});
console.log("[-] Changes written to .env");

console.log("[!] Save the API key somewhere safe! It won't be recoverable from the hash.");
