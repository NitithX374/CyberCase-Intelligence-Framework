import { spawn, spawnSync } from "node:child_process";
import { migrateThenServe } from "./backend.mjs";

const { exitCode, server } = migrateThenServe({ run: spawnSync, start: spawn });
if (!server) {
  console.error("alembic upgrade head failed, so the e2e database is not at the current schema.");
  process.exit(exitCode);
}

const stop = () => {
  server.kill();
  process.exit(0);
};
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
server.on("exit", (code) => process.exit(code ?? 1));
