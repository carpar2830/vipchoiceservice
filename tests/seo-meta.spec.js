// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('SEO and meta', () => {
  test('has a meta description', async ({ page }) => {
    await page.goto('/');
    const desc = await page.locator('meta[name="description"]').getAttribute('content');
    expect(desc, 'meta description should exist').not.toBeNull();
    expect((desc || '').trim().length, 'meta description should be non-empty').toBeGreaterThan(0);
  });

  test('has a viewport meta tag (mobile-friendly)', async ({ page }) => {
    await page.goto('/');
    const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
    expect(viewport, 'viewport meta tag should exist').not.toBeNull();
    expect((viewport || '').toLowerCase()).toContain('width=');
  });

  test('html has lang attribute', async ({ page }) => {
    await page.goto('/');
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang, 'html should have a lang attribute').not.toBeNull();
    expect((lang || '').trim().length).toBeGreaterThan(0);
  });

  test('serves a favicon', async ({ page, request }) => {
    await page.goto('/');
    const iconHref = await page
      .locator('link[rel~="icon"]')
      .first()
      .getAttribute('href')
      .catch(() => null);
    const url = iconHref ? new URL(iconHref, page.url()).toString() : new URL('/favicon.ico', page.url()).toString();
    const res = await request.get(url);
    expect(res.status(), `favicon ${url} returned ${res.status()}`).toBeLessThan(400);
  });
});
