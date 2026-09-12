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
    await expect(page).toHaveURL(/\/case$/, { timeout: 30_000 });
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

    await page.getByRole("button", { name: "Open chat" }).click();
    const chat = page.getByRole("complementary", { name: "Case Chat Assistant" });
    await expect(chat).toBeVisible();
    const composerInput = chat.getByLabel("Chat message");
    await expect(composerInput).toBeEnabled({ timeout: 15_000 });
    await composerInput.fill("What was reported in the case?");
    await expect(chat.getByRole("button", { name: "Send message" })).toBeEnabled({ timeout: 15_000 });
    await chat.getByRole("button", { name: "Send message" }).click();
    await expect(chat.getByText("The deterministic test provider answered from the persisted case analysis.")).toBeVisible({ timeout: 60_000 });
  });

  test("clarification follow-up: displays in overview and chat, answers from chat as clarification without ask analysis message, and resolves case", async ({ page }) => {
    const unique = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const caseTitle = `Clarification Case ${unique}`;
    const narrative = `The security team observed conflicting account activity needs-clarification for host ${unique}.`;

    await page.goto("/register");
    await page.getByLabel("Name").fill("Clarification Analyst");
    await page.getByLabel("Email").fill(`clarify-${unique}@gmail.com`);
    await page.getByLabel("Password").fill("E2E-Playwright-Password-123!");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page).toHaveURL(/\/case$/, { timeout: 30_000 });

    const sidebar = page.locator("aside").first();
    await sidebar.getByRole("button", { name: "New case", exact: true }).click();
    await expect(sidebar.getByRole("button", { name: /^New case,/ })).toBeVisible();
    await sidebar.getByRole("button", { name: /^New case,/ }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/(?:intake|overview)$/);
    if (page.url().endsWith("/overview")) await page.locator("#workspace-tab-intake").click();
    await page.getByLabel(/Case title/).fill(caseTitle);
    await page.getByLabel("Case narrative or additional information").fill(narrative);
    await page.getByRole("button", { name: /Analyze case/ }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/overview$/);

    const caseId = page.url().match(/\/case\/([^/]+)\/overview$/)?.[1];
    expect(caseId).toBeTruthy();

    await expect.poll(async () => {
      const response = await page.request.get(`${apiBaseUrl}/cases/${caseId}`);
      if (!response.ok()) return `http-${response.status()}`;
      const caseRecord = await response.json();
      return caseRecord?.status;
    }, { timeout: 60_000, intervals: [500, 1000, 2000] }).toBe("awaiting_followup");

    await expect(page.getByText("Clarification needed", { exact: false })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Which identification is correct: the primary operator or the secondary contractor?")).toBeVisible();

    await page.getByRole("button", { name: "Open chat" }).click();
    const chat = page.getByRole("complementary", { name: "Case Chat Assistant" });
    await expect(chat).toBeVisible();

    await expect(chat.getByText("Which identification is correct: the primary operator or the secondary contractor?").first()).toBeVisible({ timeout: 10_000 });

    const clarificationAnswer = "Primary operator confirmed as legitimate account.";
    const composer = chat.getByLabel("Chat message");
    await composer.fill(clarificationAnswer);
    await expect(chat.getByRole("button", { name: "Send message" })).toBeEnabled();
    await chat.getByRole("button", { name: "Send message" }).click();

    await expect(chat.getByText(clarificationAnswer)).toBeVisible({ timeout: 15_000 });
    await expect(chat.getByText("The deterministic test provider answered from the persisted case analysis.")).not.toBeVisible();

    await expect.poll(async () => {
      const response = await page.request.get(`${apiBaseUrl}/cases/${caseId}`);
      if (!response.ok()) return `http-${response.status()}`;
      const caseRecord = await response.json();
      return {
        status: caseRecord?.status,
        has_pending_clarification: caseRecord?.has_pending_clarification,
        processing_status: caseRecord?.processing_status,
      };
    }, { timeout: 60_000, intervals: [500, 1000, 2000] }).toEqual({
      status: "answered",
      has_pending_clarification: false,
      processing_status: "idle",
    });

    await expect(page.locator(".section-eyebrow", { hasText: "CLARIFICATION NEEDED" })).not.toBeVisible({ timeout: 15_000 });
    await expect(chat.getByText("Clarification needed")).not.toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("heading", { name: "Executive Summary" })).toBeVisible({ timeout: 15_000 });
  });
});
