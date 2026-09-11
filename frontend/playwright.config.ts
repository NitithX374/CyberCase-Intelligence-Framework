import path from "node:path";
import { defineConfig } from "@playwright/test";

const frontendDirectory = __dirname;
const backendUrl = "http://localhost:18000";
const frontendUrl = "http://localhost:3100";
const providerUrl = "http://127.0.0.1:8099";

export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: frontendUrl,
    browserName: "chromium",
    channel: "chrome",
    headless: true,
    actionTimeout: 20_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  webServer: [
    {
      command: "node e2e/provider-stub.mjs",
      cwd: frontendDirectory,
      url: `${providerUrl}/health`,
      timeout: 120_000,
      reuseExistingServer: false,
      env: { PROVIDER_PORT: "8099" },
    },
    {
      command: "node e2e/start-backend.mjs",
      cwd: frontendDirectory,
      url: `${backendUrl}/api/v1/health`,
      timeout: 180_000,
      reuseExistingServer: false,
    },
    {
      command: "node e2e/start-frontend.mjs",
      cwd: frontendDirectory,
      url: `${frontendUrl}/login`,
      timeout: 180_000,
      reuseExistingServer: false,
    },
  ],
});
