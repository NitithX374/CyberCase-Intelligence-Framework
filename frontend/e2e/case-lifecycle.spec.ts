import { expect, test } from "@playwright/test";

const apiBaseUrl = "http://localhost:18000/api/v1";

test.describe("case lifecycle", () => {
  test.afterEach(async ({ page }) => {
    const match = page.url().match(/\/case\/([^/]+)\//);
    if (!match) return;
    await page.request.delete(`${apiBaseUrl}/cases/${match[1]}`);
  });

  test("registers, analyzes, reviews, reports, downloads, and asks", async ({ page }) => {
    const unique = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const caseTitle = `Playwright case ${unique}`;
    const narrative = `The operator reported a suspicious login from workstation ${unique}.`;

    await page.goto("/register");
    await page.getByLabel("Name").fill("Playwright E2E Analyst");
    await page.getByLabel("Email").fill(`playwright-${unique}@gmail.com`);
    await page.getByLabel("Password").fill("E2E-Playwright-Password-123!");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page).toHaveURL(/\/case$/);
    await expect(page.getByText("No saved cases yet.")).toBeVisible();

    const sidebar = page.locator("aside").first();
    await sidebar.getByRole("button", { name: "New case", exact: true }).click();
    await expect(sidebar.getByRole("button", { name: /^New case,/ })).toBeVisible();
    await sidebar.getByRole("button", { name: /^New case,/ }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/(?:intake|overview)$/);
    if (page.url().endsWith("/overview")) await page.locator("#workspace-tab-intake").click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/intake$/);
    await expect(page.getByRole("heading", { name: "Prepare case analysis" })).toBeVisible();
    await page.getByLabel(/Case title/).fill(caseTitle);
    await page.getByLabel("Case narrative or additional information").fill(narrative);
    await page.getByRole("button", { name: /Analyze case/ }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/overview$/);

    const caseId = page.url().match(/\/case\/([^/]+)\/overview$/)?.[1];
    expect(caseId).toBeTruthy();
    await expect.poll(async () => {
      const response = await page.request.get(`${apiBaseUrl}/cases/${caseId}/analysis`);
      if (!response.ok()) return `http-${response.status()}`;
      const result = await response.json();
      return result?.status ?? "missing";
    }, { timeout: 60_000, intervals: [500, 1000, 2000] }).toBe("validated");

    await page.reload();
    await expect(page.getByRole("heading", { name: "Executive Summary" })).toBeVisible();
    await expect(page.getByText(narrative, { exact: true })).toBeVisible();

    await page.locator("#workspace-tab-materials").click();
    await expect(page.getByRole("heading", { name: "Saved case material" })).toBeVisible();
    await expect(page.getByText(narrative, { exact: true })).toBeVisible();

    await page.locator("#workspace-tab-report").click();
    await expect(page.getByRole("heading", { name: "Case Analysis Report" })).toBeVisible();
    await page.getByRole("button", { name: "Generate report" }).first().click();
    await expect(page.getByRole("article", { name: "Persisted report" })).toBeVisible({ timeout: 30_000 });
    await expect(page.getByRole("button", { name: "Download PDF" })).toBeVisible();

    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download PDF" }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^CyberCase-Report-v\d+\.pdf$/);

    const chatDetailResponse = page.waitForResponse((response) =>
      response.request().method() === "GET" &&
      response.url().includes(`/chats/${caseId}`) &&
      response.ok(),
    );
    await page.getByRole("button", { name: "Open chat" }).click();
    await chatDetailResponse;
    const chat = page.getByRole("complementary", { name: "Case Chat Assistant" });
    await expect(chat).toBeVisible();
    await chat.getByLabel("Chat message").fill("What was reported in the case?");
    await expect(chat.getByRole("button", { name: "Send message" })).toBeEnabled();
    await chat.getByRole("button", { name: "Send message" }).click();
    await expect(chat.getByText("The deterministic test provider answered from the persisted case analysis.")).toBeVisible({ timeout: 60_000 });
  });
});
