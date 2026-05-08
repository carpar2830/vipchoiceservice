// @ts-check
const { test, expect } = require('playwright/test');

const WP_USER = process.env.WP_USER;
const WP_PASS = process.env.WP_PASS;

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

  test('rejects invalid credentials', async ({ page }) => {
    await page.goto('/wp-login.php');
    await page.locator('#user_login').fill('not-a-real-user-xyz');
    await page.locator('#user_pass').fill('definitely-wrong-password');
    await page.locator('#wp-submit').click();
    await expect(page.locator('#login_error, .login .message')).toBeVisible({ timeout: 15000 });
    expect(page.url()).toContain('wp-login.php');
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

  test('can log out cleanly', async ({ page, context }) => {
    await page.goto('/wp-login.php');
    await page.locator('#user_login').fill(WP_USER);
    await page.locator('#user_pass').fill(WP_PASS);
    await Promise.all([
      page.waitForURL(/\/wp-admin\/?/, { timeout: 30000 }),
      page.locator('#wp-submit').click(),
    ]);
    const logout = page.locator('#wp-admin-bar-logout a').first();
    await logout.click();
    await expect(page.locator('#loginform')).toBeVisible({ timeout: 15000 });
  });
});
