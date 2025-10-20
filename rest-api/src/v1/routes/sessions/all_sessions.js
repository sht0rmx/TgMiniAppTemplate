import { Router } from "express";
import { SessionInfo } from "../../../services/session/index.js"
import {authMiddleware} from "../../../middleware/auth.js";

const router = Router();

router.get("/", authMiddleware , async (req, res) => {
    /*
    #swagger.path = '/api/v1/session/all_sessions'
    #swagger.tags = ["Auth"]
    #swagger.description = 'get all authorized sessions'
    */
    try {
        console.log(req.session)
    } catch (err) {
        console.error(err);
        res.status(500).json({ detail: "Internal server error" });
    }
})

export default router;