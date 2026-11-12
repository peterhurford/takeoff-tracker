// Time page loads and a Takeoff setting change in a real browser.
//   node perf/time_browser.js                       # http://localhost:8501/
//   node perf/time_browser.js https://takeoff-tracker.streamlit.app/~/+/
// Needs `playwright` (npm i playwright && npx playwright install chromium).
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://localhost:8501/';
async function waitRun(page, t0, max = 240000) {
  // Seconds until Streamlit's "running" indicator has shown and cleared.
  let seen = false;
  while (Date.now() - t0 < max) {
    const r = await page.locator('[data-testid="stStatusWidget"]').count();
    if (r) seen = true; else if (seen || Date.now() - t0 > 2500) return (Date.now() - t0) / 1000;
    await page.waitForTimeout(50);
  }
  return null;
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  for (const tab of ['releaselag', 'takeoff', 'china', 'pacing', 'eci']) {
    const t0 = Date.now();
    await page.goto(BASE + '?tab=' + tab);
    await page.waitForSelector('.js-plotly-plot', { state: 'attached', timeout: 240000 });
    console.log(`${tab}: loaded in ${await waitRun(page, t0)} s`);
  }
  await page.goto(BASE + '?tab=takeoff');
  await page.waitForSelector('.js-plotly-plot', { state: 'attached', timeout: 240000 });
  await page.waitForTimeout(8000);
  // Use values nobody has tried, or the server's cache answers instantly.
  for (const [label, d] of [['Returns to research (r)', 0.07], ['Returns to research (r)', 0.13]]) {
    const inp = page.getByLabel(label, { exact: true }).first();
    await inp.scrollIntoViewIfNeeded();
    const v = parseFloat(await inp.inputValue());
    await inp.fill(String(+(v + d).toFixed(2)));
    const t = Date.now(); await inp.press('Enter');
    console.log(`change "${label}" to ${+(v + d).toFixed(2)}: ${await waitRun(page, t)} s`);
    await page.waitForTimeout(2000);
  }
  await browser.close();
})();
