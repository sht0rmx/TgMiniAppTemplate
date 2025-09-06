/// <reference path="../pb_data/types.d.ts" />

routerAdd("GET", "/api/ping", (c) => {
  return c.json(200, { pong: true })
})
