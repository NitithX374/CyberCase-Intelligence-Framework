import { expect, test } from "@playwright/test";

test.describe("public authentication boundary", () => {
  test("renders sign in and redirects protected workspace access", async ({ page }) => {
    await page.goto("/login");
    await page.waitForTimeout(1500);
    await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();

    await page.goto("/case");
    await page.waitForTimeout(1500);
    await expect(page).toHaveURL(/\/login\?redirect=%2Fcase$/);
  });
});
