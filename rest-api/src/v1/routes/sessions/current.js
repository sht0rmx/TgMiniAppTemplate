import { Router } from "express";
import { SessionInfo } from "../../../services/session/index.js"
import {authMiddleware} from "../../../middleware/auth.js";

const router = Router();

router.get("/", authMiddleware , async (req, res) => {
    /*
    #swagger.path = '/api/v1/session/current'
    #swagger.tags = ["Auth"]
    #swagger.description = 'get current session'
    */
    try {
        let data = await SessionInfo.currentDevice(req.session.id)
        return res.status(200).json(data)
    } catch (err) {
        console.error(err);
        res.status(500).json({ detail: "Internal server error" });
    }
})

export default router;