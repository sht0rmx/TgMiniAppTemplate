/// <reference path="../pb_data/types.d.ts" />

onBootstrap((e) => {
  e.next();
  console.log("tg_login_mini_app init!");
});

routerAdd("POST", "/api/auth/telegram", (c) => {
  function parseInitData(initData) {
    const params = {};
    initData.split("&").forEach((pair) => {
      const [k, v] = pair.split("=");
      if (k) params[decodeURIComponent(k)] = decodeURIComponent(v || "");
    });
    return params;
  }

  function b64ToHex(b64) {
    const chars =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let bin = "";
    for (let i = 0; i < b64.length; i++) {
      if (b64[i] === "=") continue;
      bin += chars.indexOf(b64[i]).toString(2).padStart(6, "0");
    }
    let hex = "";
    for (let i = 0; i < bin.length; i += 8) {
      const byte = bin.slice(i, i + 8);
      if (byte.length === 8)
        hex += parseInt(byte, 2).toString(16).padStart(2, "0");
    }
    return hex;
  }

  console.log("Request Auth /api/auth/telegram");

  let initData;

  try {
    const body = c.requestInfo().body;
    initData = body["initData"];
  } catch (error) {
    console.error(error);
  }

  const result = new DynamicModel({
    value: "",
  });

  let botToken;
  try {
    $app
      .db()
      .newQuery("SELECT value FROM env WHERE key = 'BOT_TOKEN'")
      .one(result);

    botToken = result.value;
  } catch (err) {
    console.error(error);
  }

  let params;

  try {
    params = parseInitData(initData);
    const hash = params.hash;

    const sorted = Object.keys(params)
      .sort()
      .map((k) => `${k}=${params[k]}`)
      .join("\n");

    const secretKey = $security.hs256(botToken, "WebAppData");

    const expectedHash = $security.hs256(sorted, secretKey);

    if (!b64ToHex(expectedHash) == hash) {
      return c.json(400, { error: "invalid hash" });
    }
  } catch (err) {
    console.error("Hash validation error:", err);
    return c.json(500, { error: "Hash validation failed" });
  }

  let record;
  let user;
  try {
    user =
      typeof params.user === "string" ? JSON.parse(params.user) : params.user;
    const tgId = user["id"];
    const username = user["username"];

    try {
      let userRecord = new DynamicModel({
        id: "",
      });
      $app
        .db()
        .select("id")
        .from("users")
        .andWhere($dbx.like("telegram_id", tgId))
        .one(userRecord)

      record = $app.findRecordById("users", userRecord.id);
    } catch (e) {
      if (e.message.includes("no rows in result set")) {
        const usersColl = $app.findCollectionByNameOrId("users");
        record = new Record(usersColl);

        let fakeEmail;
        if (username && username.trim() !== "") {
          fakeEmail = username + "@telegram.local";
        } else {
          fakeEmail = tgId + "@telegram.local";
        }

        record.set("telegram_id", tgId);
        record.set("username", username || "");

        record.set("email", fakeEmail);
        record.set("password", $security.randomString(32));

        if (user.photo_url) {
          record.set("avatar_url", user["photo_url"]);
        }
        $app.save(record);
      } else {
        throw e;
      }
    }
  } catch (err) {
    console.error("User save error:", err);
    return c.json(500, { error: "User creation failed" });
  }

  try {
    const token = record.newAuthToken();
    console.log("Authorised uid:",user["id"],"authdate:",params.auth_date);
    return c.json(200, { token, record });
  } catch (err) {
    console.error("Token gen error:", err);
    return c.json(500, { error: "Auth token generation failed" });
  }
});
