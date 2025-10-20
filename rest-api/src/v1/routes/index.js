import {Router} from "express";
import authRouter from "./auth/index.js";
import sessionsRouter from "./sessions/index.js";

const router = Router();

router.use("/auth", authRouter)
router.use("/session", sessionsRouter)

router.get('/ping', (req, res) => {
    /*
    #swagger.path = '/api/v1/ping'
    #swagger.description = 'check api health'
    */
    res.send({"message": "pong"});
});

export default router;
