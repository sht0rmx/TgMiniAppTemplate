import fs from "fs";
import path from "path";
import swaggerAutogen from "swagger-autogen";

const outputFile = "./swagger.json";

function findJsFiles(dir) {
  let res = [];
  for (const f of fs.readdirSync(dir)) {
    const full = path.join(dir, f);
    if (fs.statSync(full).isDirectory()) res = res.concat(findJsFiles(full));
    else if (full.endsWith(".js")) res.push(full);
  }
  return res;
}

const endpointsFiles = findJsFiles("./v1/routes");

const doc = {
  info: {
    title: "TgMiniApp API Documentation",
    description: "Backend part of https://github.com/sht0rmx/TgMiniAppTemplate",
  },
  host: "localhost:8080",
  schemes: ["http", "https"],
};

const swaggerAutogenInstance = swaggerAutogen();

swaggerAutogenInstance(outputFile, endpointsFiles, doc).then(() => {
  console.log("OK!");
});
