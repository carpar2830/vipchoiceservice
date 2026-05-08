// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('vipchoiceservice.com homepage', () => {
  test('loads successfully with HTTP 200', async ({ page }) => {
    const response = await page.goto('/');
    expect(response, 'navigation response should exist').not.toBeNull();
    expect(response?.status(), 'expected HTTP 200').toBe(200);
  });

  test('has a non-empty title', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.trim().length, `page title should not be empty, got "${title}"`).toBeGreaterThan(0);
  });

  test('renders visible body content', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
    const text = (await page.locator('body').innerText()).trim();
    expect(text.length, 'body should contain visible text').toBeGreaterThan(50);
  });

  test('mentions core service keywords', async ({ page }) => {
    await page.goto('/');
    const body = (await page.locator('body').innerText()).toLowerCase();
    const keywords = ['tax', 'bookkeeping', 'notary'];
    const found = keywords.filter((k) => body.includes(k));
    expect(
      found.length,
      `expected at least one of [${keywords.join(', ')}] in page text; found: [${found.join(', ')}]`,
    ).toBeGreaterThan(0);
  });

  test('has at least one heading', async ({ page }) => {
    await page.goto('/');
    const headings = page.locator('h1, h2, h3');
    const count = await headings.count();
    expect(count, 'expected at least one h1/h2/h3').toBeGreaterThan(0);
  });

  test('has no broken images', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    const broken = await page.evaluate(() =>
      Array.from(document.images)
        .filter((img) => img.complete && img.naturalWidth === 0)
        .map((img) => img.src),
    );
    expect(broken, `broken images: ${JSON.stringify(broken)}`).toEqual([]);
  });

  test('does not log severe console errors', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', (err) => errors.push(`pageerror: ${err.message}`));
    await page.goto('/', { waitUntil: 'networkidle' });
    expect(errors, `console errors: ${errors.join(' | ')}`).toEqual([]);
  });

  test('has internal navigation links', async ({ page }) => {
    await page.goto('/');
    const links = page.locator('a[href]');
    const count = await links.count();
    expect(count, 'expected at least one link on the homepage').toBeGreaterThan(0);
  });
});
