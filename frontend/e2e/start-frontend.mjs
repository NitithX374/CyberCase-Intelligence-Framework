import path from "node:path";
import { spawn } from "node:child_process";

const frontendDirectory = path.resolve(import.meta.dirname, "..");
const child = spawn(
  process.platform === "win32" ? process.env.ComSpec ?? "cmd.exe" : "npm",
  process.platform === "win32"
    ? ["/d", "/s", "/c", "npm run dev -- --webpack --port 3100"]
    : ["run", "dev", "--", "--webpack", "--port", "3100"],
  {
    cwd: frontendDirectory,
    env: {
      ...process.env,
      NEXT_PUBLIC_API_URL: "http://localhost:18000/api/v1",
      NEXT_TELEMETRY_DISABLED: "1",
    },
    stdio: "inherit",
    windowsHide: true,
  },
);

const stop = () => {
  child.kill();
  process.exit(0);
};
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
child.on("exit", (code) => process.exit(code ?? 1));
