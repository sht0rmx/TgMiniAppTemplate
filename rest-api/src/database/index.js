import "reflect-metadata";
import { DataSource } from "typeorm";
import { User } from "./entities/User.js";
import { RefreshSession } from "./entities/RefreshSession.js";
import dotenv from "dotenv";
dotenv.config();

export const AppDataSource = new DataSource({
  type: "postgres",
  url: process.env.DB_URL,
  synchronize: true,
  logging: true,
  entities: [User, RefreshSession],
});

export default AppDataSource;