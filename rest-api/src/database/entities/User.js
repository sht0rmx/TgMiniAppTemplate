import { EntitySchema } from "typeorm";

export const User = new EntitySchema({
  name: "User",
  tableName: "users",
  columns: {
    id: {
      primary: true,
      type: "uuid",
      generated: "uuid",
    },
    telegram_id: {
      type: "bigint",
      unique: true,
    },
    name: {
      type: "varchar",
      length: 30,
    },
    username: {
      type: "varchar",
      length: 30,
    },
    role: {
      type: "varchar",
      length: 30,
    },
    avatar_url: {
      type: "text",
      nullable: true,
    },
  },
  relations: {
    refresh_tokens: {
      type: "one-to-many",
      target: "RefreshSession",
      inverseSide: "user",
    },
  },
});
