import dotenv from "dotenv";
dotenv.config();

import "reflect-metadata";
import { DataSource } from "typeorm";
import { User } from "./entities/User.js";
import { RefreshSession } from "./entities/RefreshSession.js";

/** @type {DataSource} */
export const AppDataSource = new DataSource({
    type: "postgres",
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    username: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_TABLE,
    synchronize: true,
    logging: false,
    entities: [User, RefreshSession],
});

export default AppDataSource;
