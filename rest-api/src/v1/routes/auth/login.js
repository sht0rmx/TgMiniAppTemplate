import {Router} from "express";
import {body} from "express-validator";
import {Utils, Tokens, Users} from "../../../services/auth/index.js";

const router = Router();


router.post("/webapp", body("initData").exists(), async (req, res) => {
      /*
      #swagger.path = '/api/v1/auth/login/webapp'
      #swagger.tags = []
      #swagger.description = 'get session token by login with InitData param from TgMiniapp'
      */
    try {
        const {initData} = req.body;
        const botToken = process.env.BOT_TOKEN;

        const params = Utils.parseInitData(initData);
        const hashStr = params.hash;
        delete params.hash;

        if (!hashStr || !(await Utils.checkValidateInitData(hashStr, initData, botToken))) {
            return res.status(401).json({detail: "Invalid Telegram initData"});
        }

        const userInfo = params.user || {};
        const telegramId = parseInt(userInfo.id || 0);
        const username = userInfo.username || "";
        const firstname = userInfo.first_name || "";
        const photo = userInfo.photo_url || null;

        const ua = req.headers["user-agent"] || "web";
        const ip = req.ip || req.headers["x-forwarded-for"]?.split(",")[0] || "0.0.0.0";

        let fpToken = req.cookies.fp;
        if (!fpToken || !Tokens.checkFingerprintToken(fpToken, ua, ip)) {
            fpToken = Tokens.makeFingerprintToken(ua, ip);
            res.cookie("fp", fpToken, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "strict",
                maxAge: 7 * 24 * 60 * 60 * 1000,
            });
        }

        const {user, _, tokens} = await Users.updateUser({
            telegramId,
            username,
            firstname,
            photo,
            ua,
            ip,
            fpToken,
        });

        if (tokens.refresh_token) {
            res.cookie("refreshToken", tokens.refresh_token, {
                httpOnly: true,
                secure: process.env.NODE_ENV === "production",
                sameSite: "strict",
                maxAge: 7 * 24 * 60 * 60 * 1000,
            });
        }
        res.json({
            tokens,
            user: {
                id: user.id,
                telegram_id: user.telegram_id,
                username: user.username,
                name: user.name,
                avatar_url: user.avatar_url,
                role: user.role,
            },
        });

    } catch (err) {
        console.error(err);
        res.status(500).json({detail: "Internal server error"});
    }
});

router.get("/otp/get", async (req, res) => {

})

router.post("/otp/check", async (req, res) => {

})

export default router;