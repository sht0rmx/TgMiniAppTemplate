import jwt from "jsonwebtoken";
import dotenv from "dotenv";
dotenv.config();

export function generateAccessToken(user, expiresIn = "30m") {
  const payload = {
    sub: user.id,
    telegram_id: user.telegram_id,
    username: user.username
  };

  return jwt.sign(payload, process.env.JWT_SECRET, { expiresIn });
}

export function verifyAccessToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET);
  } catch (err) {
    throw new Error("Invalid or expired token");
  }
}
