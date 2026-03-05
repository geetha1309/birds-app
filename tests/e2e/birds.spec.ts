import { test, expect } from "@playwright/test";

test("homepage renders and shows 5 cards", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Birds of Wonder" })).toBeVisible();

  // Each bird card has a scientific name line in italics -> count articles instead
  const cards = page.locator("article");
  await expect(cards).toHaveCount(5);
});

test("metrics endpoint responds", async ({ page }) => {
  const res = await page.request.get("/metrics");
  expect(res.ok()).toBeTruthy();
  const body = await res.text();
  expect(body).toContain("http_requests_total");
});