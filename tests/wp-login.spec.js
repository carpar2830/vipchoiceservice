// @ts-check
const { test, expect } = require('@playwright/test');

const WP_USER = process.env.WP_USER;
const WP_PASS = process.env.WP_PASS;
// Bluehost / Cloudflare-style bot protection on /wp-login.php commonly
// blocks scripted form submissions even when manual login works fine, so
// the form-submission tests below are off by default. Set
// RUN_LOGIN_FORM_TESTS=true locally to run them while debugging.
const RUN_FORM_TESTS = process.env.RUN_LOGIN_FORM_TESTS === 'true';

test.describe('WordPress admin login', () => {
  test.skip(!WP_USER || !WP_PASS, 'Set WP_USER and WP_PASS env vars to run login tests');

  test('login page renders', async ({ page }) => {
    const res = await page.goto('/wp-login.php');
    expect(res?.status(), 'wp-login.php should respond 200').toBe(200);
    await expect(page.locator('#loginform')).toBeVisible();
    await expect(page.locator('#user_login')).toBeVisible();
    await expect(page.locator('#user_pass')).toBeVisible();
    await expect(page.locator('#wp-submit')).toBeVisible();
  });

  test.describe('form submission', () => {
    test.skip(
      !RUN_FORM_TESTS,
      'Set RUN_LOGIN_FORM_TESTS=true to run; many hosts block scripted /wp-login.php submissions',
    );

    test('rejects invalid credentials', async ({ page }) => {
      await page.goto('/wp-login.php');
      await page.locator('#user_login').fill('not-a-real-user-xyz');
      await page.locator('#user_pass').fill('definitely-wrong-password');
      await page.locator('#wp-submit').click();
      await page.waitForTimeout(3000);
      expect(page.url(), 'invalid creds must not reach the admin').not.toContain('/wp-admin/');
      await expect(page.locator('#wpadminbar')).toHaveCount(0);
    });

    test('valid credentials reach the dashboard', async ({ page }) => {
      await page.goto('/wp-login.php');
      await page.locator('#user_login').fill(WP_USER);
      await page.locator('#user_pass').fill(WP_PASS);
      await Promise.all([
        page.waitForURL(/\/wp-admin\/?/, { timeout: 30000 }),
        page.locator('#wp-submit').click(),
      ]);
      await expect(page.locator('#wpadminbar')).toBeVisible();
      await expect(page).toHaveURL(/\/wp-admin\/?/);
    });

    test('can log out cleanly', async ({ page }) => {
      await page.goto('/wp-login.php');
      await page.locator('#user_login').fill(WP_USER);
      await page.locator('#user_pass').fill(WP_PASS);
      await Promise.all([
        page.waitForURL(/\/wp-admin\/?/, { timeout: 30000 }),
        page.locator('#wp-submit').click(),
      ]);
      const logoutHref = await page.locator('#wp-admin-bar-logout a').getAttribute('href');
      expect(logoutHref, 'logout link should have an href').toBeTruthy();
      await page.goto(logoutHref);
      await expect(page.locator('#loginform')).toBeVisible({ timeout: 15000 });
    });
  });
});
