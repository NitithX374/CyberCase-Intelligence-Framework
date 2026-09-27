import path from "node:path";

const frontendDirectory = path.resolve(import.meta.dirname, "..");
const repositoryDirectory = path.resolve(frontendDirectory, "..");
export const backendDirectory = path.join(repositoryDirectory, "backend");
const pythonExecutable =
  process.platform === "win32"
    ? path.join(repositoryDirectory, "env_mitre", "Scripts", "python.exe")
    : path.join(repositoryDirectory, "env_mitre", "bin", "python");
const databaseUrl =
  process.env.E2E_DATABASE_URL ??
  "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/cybercase_framework";

export const backendEnvironment = {
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
  RAG_SERVICE_URL: "http://127.0.0.1:8001",
  PYTHONUNBUFFERED: "1",
};

export function migrateThenServe({ run, start }) {
  const options = {
    cwd: backendDirectory,
    env: backendEnvironment,
    stdio: "inherit",
    windowsHide: true,
  };
  const migration = run(pythonExecutable, ["-m", "alembic", "upgrade", "head"], options);
  if (migration.status !== 0) return { exitCode: migration.status ?? 1, server: null };
  const server = start(
    pythonExecutable,
    ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "18000"],
    options,
  );
  return { exitCode: 0, server };
}
