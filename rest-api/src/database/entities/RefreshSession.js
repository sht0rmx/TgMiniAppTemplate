import { EntitySchema } from "typeorm";

export const RefreshSession = new EntitySchema({
  name: "RefreshSession",
  tableName: "refresh_sessions",
  columns: {
    id: {
      primary: true,
      type: "int",
      generated: true,
    },
    userId: {
      type: "uuid",
    },
    refreshToken: {
      type: "uuid",
    },
    user_agent: {
      type: "varchar",
      length: 200,
    },
    fingerprint: {
      type: "varchar",
      length: 200,
    },
    ip: {
      type: "varchar",
      length: 15,
    },
    expiresIn: {
      type: "bigint",
    },
    createdAt: {
      type: "timestamptz",
      createDate: true,
      default: () => "NOW()",
    },
  },
  relations: {
    user: {
      type: "many-to-one",
      target: "User",
      joinColumn: { name: "userId" },
      onDelete: "CASCADE",
      inverseSide: "refresh_tokens",
    },
  },
});
