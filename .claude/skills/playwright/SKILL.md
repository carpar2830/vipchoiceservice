---
name: playwright
description: Drive a real browser via Playwright for debugging and verifying website changes. Use this skill whenever the user asks to debug a page, verify a UI change, take a screenshot, check console errors, inspect network requests, test responsive layouts, or reproduce a frontend bug. Works by running `npx playwright` scripts via Bash — no MCP server required, so it works in any Claude Code environment (local or web sandbox).
---

# Playwright debugging skill

Use this skill to drive a real Chromium/Firefox/WebKit browser to debug and verify website changes for this project. It does **not** depend on the Playwright MCP — it uses `npx playwright` via Bash, so it works in any environment.

## When to invoke

Auto-invoke when the user asks to:
- Debug a page (rendering, layout, console errors, JS errors)
- Verify a UI change visually (screenshots before/after)
- Check console / network during a flow
- Reproduce a frontend bug
- Test responsive breakpoints
- Inspect DOM, computed styles, accessibility tree of a live page
- Smoke-test a deployed URL or local dev server

## One-time setup (do on first use, then cache)

```bash
# Inside the repo
npm init -y >/dev/null 2>&1 || true
npm i -D @playwright/test >/dev/null 2>&1
# Install only chromium to save time/space; add others if needed
npx playwright install chromium --with-deps 2>&1 | tail -5
```

If `--with-deps` fails (no sudo), drop it: `npx playwright install chromium`.

## Standard recipes

Write a one-off script to a temp file, run it, capture output and screenshots. Don't hand-craft long inline JS strings.

### Recipe 1: Smoke a URL — screenshot + console + errors

```bash
cat > /tmp/pw-smoke.mjs <<'EOF'
import { chromium } from 'playwright';
const url = process.argv[2];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const logs = [], errors = [], failedReqs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => errors.push(String(e)));
page.on('requestfailed', r => failedReqs.push(`${r.failure()?.errorText} ${r.url()}`));
const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
await page.screenshot({ path: '/tmp/pw-smoke.png', fullPage: true });
console.log(JSON.stringify({
  status: resp?.status(), url: page.url(),
  title: await page.title(),
  console: logs, pageErrors: errors, failedRequests: failedReqs,
}, null, 2));
await browser.close();
EOF
node /tmp/pw-smoke.mjs "https://example.com"
ls -la /tmp/pw-smoke.png
```

Then `Read /tmp/pw-smoke.png` to view the screenshot.

### Recipe 2: Responsive screenshots (mobile / tablet / desktop)

```bash
cat > /tmp/pw-responsive.mjs <<'EOF'
import { chromium, devices } from 'playwright';
const url = process.argv[2];
const targets = [
  { name: 'mobile',  ...devices['iPhone 13'] },
  { name: 'tablet',  viewport: { width: 768,  height: 1024 } },
  { name: 'desktop', viewport: { width: 1440, height: 900  } },
];
const browser = await chromium.launch();
for (const t of targets) {
  const ctx = await browser.newContext(t);
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `/tmp/pw-${t.name}.png`, fullPage: true });
  await ctx.close();
}
await browser.close();
console.log('Wrote /tmp/pw-{mobile,tablet,desktop}.png');
EOF
node /tmp/pw-responsive.mjs "https://example.com"
```

### Recipe 3: Interact with a page (click / fill / wait) and capture state

```bash
cat > /tmp/pw-flow.mjs <<'EOF'
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage();
page.on('console', m => console.error(`[console.${m.type()}] ${m.text()}`));
page.on('pageerror', e => console.error(`[pageerror] ${e}`));
await page.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
// EXAMPLE — adapt to the real flow:
// await page.getByRole('button', { name: /sign in/i }).click();
// await page.getByLabel('Email').fill('test@example.com');
// await page.getByRole('button', { name: 'Submit' }).click();
// await page.waitForURL(/dashboard/);
await page.screenshot({ path: '/tmp/pw-flow.png', fullPage: true });
console.log('Final URL:', page.url());
await browser.close();
EOF
node /tmp/pw-flow.mjs "https://example.com"
```

### Recipe 4: Network inspection (capture requests/responses)

```bash
cat > /tmp/pw-net.mjs <<'EOF'
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage();
const reqs = [];
page.on('response', async r => {
  reqs.push({ status: r.status(), method: r.request().method(), url: r.url() });
});
await page.goto(process.argv[2], { waitUntil: 'networkidle' });
console.log(JSON.stringify(reqs.filter(r => r.status >= 400 || /api|graphql/i.test(r.url)), null, 2));
await browser.close();
EOF
node /tmp/pw-net.mjs "https://example.com"
```

### Recipe 5: Local dev server

If the project has a dev server (Vite, Next, etc.):

```bash
# Start dev server in background, then point Playwright at it.
# Use Bash run_in_background; never block on the dev server process.
# Wait until the server responds before launching the browser:
until curl -sf http://localhost:3000 >/dev/null; do sleep 1; done
node /tmp/pw-smoke.mjs "http://localhost:3000"
```

## Operating rules

- **Always capture a screenshot** when reporting on a UI change so the user can see what you saw. After the script writes to `/tmp/pw-*.png`, `Read` the file so the image is shown to the user.
- **Always capture console + pageerror + requestfailed** during navigation. Surface anything non-empty to the user — silent failures are the most common cause of bad debugging.
- **Use role/label selectors** (`getByRole`, `getByLabel`, `getByText`) over CSS selectors. They survive markup changes.
- **Never sleep blindly** — use `waitForURL`, `waitForSelector`, `waitForLoadState('networkidle')`, or `expect(locator).toBeVisible()`.
- **Headless by default**, since the sandbox has no display. If the user wants to watch, mention they'd need to run locally with `headless: false`.
- **Clean up**: always `await browser.close()` so the process exits.
- **Cache the install**: if `node_modules/playwright` already exists, skip reinstall. Check with `[ -d node_modules/playwright ] || npm i -D @playwright/test`.

## When to NOT use this skill

- Pure backend / API work with no browser involved → use `curl` instead.
- Unit tests for components → use the project's existing test runner.
- Static file inspection → just `Read` the file.

## Note on the Playwright MCP

This project also has `.mcp.json` declaring the Playwright MCP server. If the environment loads it, you'll see `mcp__playwright__*` tools (e.g. `browser_navigate`, `browser_click`, `browser_snapshot`) — prefer those when available because they're faster than spawning Node scripts. If those tools are NOT visible in the session, the MCP isn't active and you should fall back to the recipes above. **Both paths achieve the same result; never block on the MCP being active.**
