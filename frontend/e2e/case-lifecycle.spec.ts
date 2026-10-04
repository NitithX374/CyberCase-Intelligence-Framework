import { expect, test, type Page } from "@playwright/test";

const apiBaseUrl = "http://localhost:18000/api/v1";

async function addCaseNarrative(page: Page, narrative: string) {
  await page.getByRole("button", { name: "Write narrative" }).click();
  await page.getByLabel("Narrative", { exact: true }).fill(narrative);
  await page.getByRole("button", { name: "Add narrative" }).click();
}

test.describe("case lifecycle", () => {
  test.afterEach(async ({ page }) => {
    const match = page.url().match(/\/case\/([^/]+)\//);
    if (!match) return;
    await page.request.delete(`${apiBaseUrl}/cases/${match[1]}`);
  });

  test("registers, receives, analyzes, reports, downloads, and asks", async ({ page }) => {
    const unique = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const narrative = `The operator reported a suspicious login from workstation ${unique}.`;

    await page.goto("/register");
    await page.getByLabel("Name").fill("Playwright E2E Analyst");
    await page.getByLabel("Email").fill(`playwright-${unique}@gmail.com`);
    await page.getByLabel("Password", { exact: true }).fill("E2E-Playwright-Password-123!");
    await page.getByLabel("Confirm password", { exact: true }).fill("E2E-Playwright-Password-123!");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page).toHaveURL(/\/case$/, { timeout: 30_000 });
    await expect(page.getByRole("heading", { name: "No saved cases yet" })).toBeVisible();

    await page.getByRole("button", { name: "Create your first case", exact: true }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/(?:sources|analysis)$/, { timeout: 45_000 });
    if (page.url().endsWith("/analysis")) await page.locator("#workspace-tab-sources").click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/sources$/);
    await addCaseNarrative(page, narrative);
    await page.getByRole("button", { name: /^Analyze/ }).click();
    await expect(page).toHaveURL(/\/case\/[^/]+\/analysis$/);

    const caseId = page.url().match(/\/case\/([^/]+)\/analysis$/)?.[1];
    expect(caseId).toBeTruthy();
    await expect
      .poll(
        async () => {
          const response = await page.request.get(`${apiBaseUrl}/cases/${caseId}/analysis`);
          if (!response.ok()) return `http-${response.status()}`;
          const result = await response.json();
          return result?.status ?? "missing";
        },
        { timeout: 60_000, intervals: [500, 1000, 2000] },
      )
      .toBe("validated");

    await page.reload();
    const sections = page.getByRole("navigation", { name: "Analysis sections" });
    await expect(page.getByRole("heading", { name: "Summary", exact: true })).toBeVisible();
    const summary = page.getByRole("region", { name: "Summary", exact: true });
    await expect(summary).toContainText(`${narrative} [A-01]`);
    const claimLink = summary.getByRole("link", { name: "A-01", exact: true });
    await expect(claimLink).toHaveAttribute("href", /\/analysis\/findings\?finding=A-01$/);
    await claimLink.click();
    await expect(page).toHaveURL(/\/analysis\/findings\?finding=A-01$/, { timeout: 60_000 });
    await expect(page.locator("#finding-A-01")).toBeInViewport();
    await sections.getByRole("link", { name: "Summary", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Summary", exact: true })).toBeVisible();
    await sections.getByRole("link", { name: /^Findings/ }).click();
    await expect(page).toHaveURL(/\/analysis\/findings$/, { timeout: 60_000 });
    await expect(page.getByText(narrative, { exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Case narrative #1" }).first().click();
    const drawer = page.getByRole("dialog", { name: "Source: Case narrative #1" });
    await expect(drawer.getByRole("heading", { level: 3, name: "Quoted" })).toBeVisible();
    await expect(drawer.getByText(narrative, { exact: true }).first()).toBeVisible();
    await drawer.getByRole("button", { name: "Close source" }).click();
    await expect(drawer).toBeHidden();

    await sections.getByRole("link", { name: "Details" }).click();
    await expect(page.getByRole("region", { name: "Technical Context" })).toBeVisible({
      timeout: 60_000,
    });
    await sections.getByRole("link", { name: "Report" }).click();
    const report = page.getByRole("region", { name: "Case report" });
    await expect(report.getByRole("heading", { name: "Report", exact: true })).toBeVisible({
      timeout: 60_000,
    });

    await page.locator("#workspace-tab-sources").click();
    await expect(page.getByRole("tabpanel", { name: "Case sources" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Case narrative" })).toBeVisible();
    await page.locator("#workspace-tab-analysis").click();
    await sections.getByRole("link", { name: "Report" }).click();
    await page.getByRole("button", { name: "Generate report" }).first().click();
    await expect(page.getByRole("article", { name: "Persisted report" })).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByRole("button", { name: "Download PDF" })).toBeVisible();

    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download PDF" }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^CyberCase-Report-v\d+\.pdf$/);

    const chat = page.getByRole("complementary", { name: "Ask about this case" });
    if (!(await chat.isVisible())) {
      await page.getByRole("button", { name: "Open Ask" }).click();
    }
    await expect(chat).toBeVisible();
    const composerInput = chat.getByLabel("Chat message");
    await expect(composerInput).toBeEnabled({ timeout: 15_000 });
    await composerInput.fill("What was reported in the case?");
    await expect(chat.getByRole("button", { name: "Send message" })).toBeEnabled({
      timeout: 15_000,
    });
    await chat.getByRole("button", { name: "Send message" }).click();
    await expect(
      chat.getByText("The deterministic test provider answered from the persisted case analysis."),
    ).toBeVisible({ timeout: 60_000 });
  });
});
