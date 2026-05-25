# Command Prompt — VIP Choice Service Website Audit & Fix

Copy everything inside the code block below and paste it to your coworker agent as its task.

It is written to be **self-contained** (the agent does not need this conversation),
tailored to a **WordPress** site, and works whether the agent only has **browser access**
(diagnose + produce a fix list) or also has **WordPress dashboard access** (apply fixes directly).

---

```text
ROLE
You are a senior web QA + WordPress engineer. Audit and fix the website
https://vipchoiceservice.com/ — a Dallas, TX small-business site offering tax
preparation, bookkeeping, notary, and business services. The site is built on
WordPress. Be thorough, specific, and practical. Do not guess: verify everything
by actually loading pages and interacting with them.

ACCESS RULES
- If you only have browser access: DIAGNOSE everything and produce a prioritized,
  copy-paste fix list with exact WordPress steps for each issue. Do not claim a fix
  is done unless you actually applied it.
- If you also have WordPress admin (wp-admin) / page-builder access: apply the fixes
  directly, then re-test in the browser to confirm. Make a backup or note what you
  changed before editing.

GOAL (in priority order)
1. Every button, link, and call-to-action works (no dead links, no 404s, no broken anchors).
2. Every form submits correctly and the submission is actually received.
3. No console/JavaScript errors, no broken images, no mixed-content (http on an https page).
4. The mobile experience is fully functional and comfortable (menu, tap targets, no
   horizontal scrolling, readable text, working click-to-call).
5. The site is "super efficient" — fast load, good Core Web Vitals, optimized images,
   caching, minimal render-blocking.

=== STEP 1: BUILD A PAGE INVENTORY ===
- Start at the homepage. Click through the main menu, footer menu, and every visible
  link to list ALL pages (Home, Services, About, Contact, Booking/Appointment, Pricing,
  Blog, Privacy, Terms, etc.). Note each page URL.
- Note any pages that are linked but return 404 or redirect oddly.

=== STEP 2: TEST EVERY BUTTON & LINK (DESKTOP) ===
For each page, click/activate every button, menu item, CTA ("Book Now", "Get a Quote",
"Call Us", "Schedule", "Learn More", social icons, footer links). For each, record:
- Button/link text and the page it's on.
- Where it points (URL or #anchor) and whether it actually goes there.
- PASS or FAIL. For FAIL, note the symptom: dead link, 404, scrolls nowhere, opens
  blank, points to "#", points to localhost/staging, or points to the wrong page.
Pay special attention to common WordPress problems:
- Buttons set to "#" or with no link configured in the page builder (Elementor/Divi/Gutenberg).
- Links pointing to a staging/old domain instead of vipchoiceservice.com.
- Smooth-scroll anchors whose target section ID no longer exists.
- Social icons pointing to empty or default profiles.

=== STEP 3: TEST EVERY FORM ===
For each form (contact, quote/estimate request, appointment booking, newsletter):
- List every field and which are required.
- Submit with realistic TEST data (use a name like "Test Audit" and an email you control,
  e.g., the site owner's email or a temp inbox). Note: this may send a real email.
- Confirm: does it show a success message? Does it clear/redirect? Does it show validation
  errors correctly when required fields are empty or email is malformed?
- Check the likely plugin (Contact Form 7, WPForms, Gravity Forms, Fluent Forms, Forminator,
  Ninja Forms) and whether email delivery is configured. Flag if the site lacks an SMTP
  plugin (WP Mail SMTP) — default WordPress email often silently fails to deliver, which is
  one of the most common "my contact form doesn't work" causes.
- For booking/scheduling buttons (Calendly, Acuity, Bookly, Amelia), confirm the embed or
  popup actually loads and a time can be selected.

=== STEP 4: ERRORS, BROKEN ASSETS, MIXED CONTENT ===
On each page, open browser DevTools:
- Console tab: record any red JavaScript errors (with the message and source file).
- Network tab: record any request returning 404/403/500, and any http:// asset loaded on
  the https:// site (mixed content — causes the padlock to break and images/scripts to fail).
- Images: list any broken images (broken-image icon) and any image missing alt text.
- Check the favicon loads and the browser tab title is correct (not "Just another
  WordPress site" or a leftover placeholder).

=== STEP 5: MOBILE / RESPONSIVE AUDIT (do this for real, not assumed) ===
Use the browser device toolbar (emulate iPhone and a small Android, e.g., 375px and 360px
wide) and also a tablet width (768px). On the key pages (Home, Services, Contact, Booking):
- Hamburger menu: opens, closes, all items reachable and tappable.
- Horizontal scroll: there should be NONE. Flag any element wider than the screen that
  causes left-right scrolling (a very common WordPress/page-builder bug).
- Tap targets: buttons/links should be at least ~44x44px and not overlapping.
- Text legibility: body text not tiny (>=16px), no text overflowing its container.
- Phone numbers are click-to-call (tel: links) and email is mailto:.
- Sticky header/footer or chat widgets do not cover content or buttons.
- Forms: fields are full-width, keyboard type is sensible (email field shows email keyboard),
  and the submit button is reachable.
- Confirm there is a proper viewport meta tag (width=device-width, initial-scale=1).
- Pop-ups/cookie banners are dismissable on mobile and don't trap the user.

=== STEP 6: PERFORMANCE / "SUPER EFFICIENT" ===
Run Lighthouse (Chrome DevTools) in BOTH mobile and desktop modes, and/or Google
PageSpeed Insights (pagespeed.web.dev) for the homepage and one service page. Report:
- Performance score, LCP, CLS, INP/TBT, and the top opportunities listed.
Then give concrete WordPress fixes for the biggest wins, typically:
- Images: convert large JP/PNG to WebP, compress, set explicit width/height to prevent
  layout shift, enable lazy-loading. (Plugins: ShortPixel, Smush, EWWW, or Imagify.)
- Caching + minify: install/configure a caching plugin (WP Rocket, LiteSpeed Cache, or
  W3 Total Cache) — page cache, GZIP/Brotli, minify CSS/JS, defer non-critical JS.
- Render-blocking: defer/async JavaScript, eliminate unused CSS/JS (page builders like
  Elementor/Divi often load heavy assets site-wide).
- Fonts: limit web fonts, preload the main font, use font-display: swap.
- Reduce plugin bloat: list active plugins and flag obviously redundant/abandoned ones.
- Confirm a CDN is in use (Cloudflare is free and easy) if the site is slow globally.
- Check for excessive redirects and a slow Time To First Byte (hosting/cache issue).

=== STEP 7: LOCAL-BUSINESS / TRUST QUICK CHECKS ===
Since this is a local Dallas service business:
- Is the business Name, Address, Phone (NAP) consistent and visible? Is the phone a
  working tel: link?
- Is there a 404 page that helps users get back (not a blank WordPress default)?
- HTTPS valid (no certificate warning)? Does http:// redirect to https://?
- Is there a Privacy Policy / Terms link in the footer (often legally needed for tax/
  financial services)?
- Title tags and meta descriptions present and not duplicated across pages.

=== OUTPUT FORMAT ===
Produce a single prioritized report:

1) SUMMARY: counts of issues by severity (Critical / High / Medium / Low) and the top 5
   things to fix first.

2) ISSUE TABLE with these columns:
   | # | Severity | Page / Location | What's wrong (with the exact button/link/error text) |
   How I verified it | Exact fix (WordPress steps) |
   - Critical = broken core function (form doesn't send, booking broken, site/page down,
     payment/contact path broken, mobile menu won't open).
   - High = dead CTA/link, 404 on a linked page, broken image on a key page, mixed content,
     horizontal scroll on mobile.
   - Medium = performance issues, missing alt text, minor mobile spacing, missing meta.
   - Low = polish, nice-to-haves.

3) MOBILE SECTION: a dedicated list of mobile-only findings and fixes.

4) PERFORMANCE SECTION: current scores + the prioritized fix list with the expected impact.

5) If you have wp-admin access: a CHANGELOG of what you actually changed and the re-test
   result for each. If browser-only: clearly mark the report as "diagnosis — fixes not yet
   applied" so the owner knows these still need to be executed in WordPress.

RULES
- Verify by doing, not by assuming. Quote the exact broken link/error text you saw.
- Never delete pages, plugins, or content without explicit approval.
- Use test data for forms; do not submit anything misleading or spammy.
- Keep fix instructions specific to WordPress and beginner-followable (name the plugin,
  the menu path, and the setting).
```

---

## Notes for you (the owner)
- I could not test the live site or its code from my environment: this cloud session's
  network is locked to GitHub only, and the source code isn't in this repo (just the
  README), so the prompt above is the deliverable rather than a list of confirmed bugs.
- If you want the coworker agent to actually *apply* fixes (not just list them), give it
  your WordPress login (wp-admin). The prompt already handles both cases.
- Fastest single thing to check yourself right now: submit your own contact form and see if
  the email arrives. A missing **WP Mail SMTP** setup is the #1 cause of "my form button
  doesn't work" on WordPress.
