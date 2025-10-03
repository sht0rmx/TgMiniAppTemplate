import swaggerAutogen from "swagger-autogen";

const outputFile = "./swagger.json";
const endpointsFiles = ["./index.js"];

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
