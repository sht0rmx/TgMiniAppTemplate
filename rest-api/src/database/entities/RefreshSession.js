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
    refreshTokenHash: {
      type: "varchar",
      length: 200,
      nullable: false,
      unique: true,
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
      length: 45,
    },
    revoked: {
      type: "boolean",
      default: false,
    },
    expiresIn: {
      type: "timestamptz",
    },
    lastUsed: {
      type: "timestamptz",
      nullable: true,
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