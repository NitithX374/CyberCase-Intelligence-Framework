import path from "node:path";
import { spawn } from "node:child_process";

const frontendDirectory = path.resolve(import.meta.dirname, "..");
const repositoryDirectory = path.resolve(frontendDirectory, "..");
const backendDirectory = path.join(repositoryDirectory, "backend");
const pythonExecutable = process.platform === "win32"
  ? path.join(repositoryDirectory, "env_mitre", "Scripts", "python.exe")
  : path.join(repositoryDirectory, "env_mitre", "bin", "python");
const databaseUrl = process.env.E2E_DATABASE_URL ?? "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework";

const child = spawn(
  pythonExecutable,
  ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "18000"],
  {
    cwd: backendDirectory,
    env: {
      ...process.env,
      DATABASE_URL: databaseUrl,
      POSTGRES_HOST: "127.0.0.1",
      POSTGRES_PORT: "5433",
      POSTGRES_USER: "postgres",
      POSTGRES_PASSWORD: "postgres",
      POSTGRES_DB: "cybercase_framework",
      JWT_SECRET_KEY: "e2e-local-secret-key-for-playwright-tests",
      OPENROUTER_CYBERCASE: "e2e-local-key",
      OPENROUTER_BASE_URL: "http://127.0.0.1:8099/v1",
      OPENROUTER_MESSAGES_URL: "http://127.0.0.1:8099/v1/messages",
      CORE_LLM_PROVIDER: "openrouter",
      CASE_ANALYSIS_PIPELINE: "raw_direct",
      CORS_ORIGINS: "http://127.0.0.1:3100,http://localhost:3100",
      FRONTEND_BASE_URL: "http://127.0.0.1:3100",
      AUTH_DEV_LOGIN_ENABLED: "true",
      RAG_SERVICE_URL: "http://127.0.0.1:8001",
      PYTHONUNBUFFERED: "1",
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
