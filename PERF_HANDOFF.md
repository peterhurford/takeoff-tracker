# Performance handoff (2026-11-12)

For whoever picks this up next (a Claude Code session on Peter's laptop, most likely).
Nothing in the app has been changed yet: this is the diagnosis, the plan, and the scripts
to reproduce the numbers.

## The question and the answer so far

Peter asked whether to migrate off Streamlit to something custom. Answer after profiling:
**no, not yet.** The slowness is one Python function, `takeoff_model.simulate`, made 3–5×
worse by Streamlit Community Cloud's throttled CPU. A custom frontend over the same Python
would save about 1.5–3s per page load and leave the 11–56s waits untouched.

The order to try things is: make `simulate` faster, re-measure on the live site, and only
then decide on hosting. A rewrite comes back on the table only if both fail.

## What was measured

Production sample count (`N_SAMPLES` = 2,000), measured 2026-11-12. "Local" is a 4-core
Linux container; "live" is https://takeoff-tracker.streamlit.app/.

| Scenario | Local | Live |
|---|---|---|
| Takeoff, first load after server start (server-side only) | 13.5s | not measured |
| Pacing, first load after server start (server-side only) | 12.7s | not measured |
| China, first load after server start | 22.3s server-side | 18.9s in browser |
| Other nine tabs, first load (server-side only) | 1.7–3.0s | not measured |
| Takeoff, change *Returns to research (r)* (browser) | 11.4s | 30.0s, then 56.5s on a second change |
| Takeoff, change *Ultraintelligence threshold (ECI)* (browser) | 11.4s | 24.2s |
| Takeoff, rerun with everything cached (server-side only) | 1.6s | not measured |
| Takeoff, page load with server cache warm (browser) | 5.6s | 5.5–7.4s |
| China, page load with server cache warm (browser) | 4.1s | 6.2s |
| Release Lag (trivial tab), first visit (browser) | 2.9s | 7.8s |
| Release Lag, repeat visit with HTTP cache (browser) | 1.7s | not measured |

Where the time goes:

- **`takeoff_model.simulate` is about 90% of every slow load.** Takeoff's cold load calls it
  three times (the pairing run, the full US run, China's run), about 12s of 13.5s. The China
  tab calls it five times, about 25s of 27s under the profiler.
- **One call at the app's size (1,000 draws, 14 years) takes 4.5s.** Roughly 0.9s of that is
  per-step numpy call overhead (it is the same at 50 draws); the rest is array arithmetic.
  It scales worse than linearly with draws: 500 draws 1.9s, 1,000 draws 4.5s, 2,000 draws
  16.4s (these three at 14 years; `python perf/bench_simulate.py`).
- **Splitting 1,000 draws across 4 processes took 1.55s** against 4.45s in one. Running the
  same chunks one after another in one process is slower (5.9s), because of the per-step
  overhead.
- **Streamlit's own floor is about 1.7–3s per page load locally**, more on the live site.
- **Chart payload is not a problem.** Takeoff sends 1.6 MB over the websocket for 27 charts.
  The `~4 MB` in `.streamlit/config.toml`'s comment is out of date.
- **A warm Takeoff rerun is 1.6s**, of which `render_rsi` (the evidence half) is about 40%.

About the live host: Streamlit's docs give Community Cloud's limits as 0.078 cores minimum
and 2 maximum, with throttling at the limit (figures as of February 2024), and apps sleep
after 12 hours without traffic. The 30s-then-56s spread on the same kind of change looks
like that throttling; the CPU allocation itself was not visible.

## Corrections to things said in the chat

- **The ultraintelligence threshold re-simulating is by design, not a cache bug.** In
  `_tk_run`, `coding_level = ultra - (eci_now + eci_start_dev)` is passed to `simulate` as
  `coding_capability`, so the threshold is a model input. There is no free fix there.
- **The US ship lag also triggered an 11.5s rerun** on Takeoff. Why was not traced. It may
  be legitimate in the same way; check before assuming it is a wasted run.
- **Fragments (`st.fragment`) are a modest win**, about a second off interactions that do
  not re-simulate. They are not the main fix.

## Plan, in order

### 1. Make `simulate` faster (the main job)

Read `docs/takeoff.md` and `TAKEOFF_MODEL.md` first; `test_takeoff_model.py` (1,200 lines)
is the parity suite.

The loop is `while np.any(t < p["years"] - 1e-12)` at `takeoff_model.py:1094`, weekly steps
over per-draw arrays, calling `humans`, `workflow_state`, `advance`, `ceiling_step`,
`_ces_log`, `pays_off`, `at` and `_paths_at` each step.

Options, cheapest first:

- **Profile by line and remove waste in place.** `[self]` time in `simulate` is 2.2s of 5.0s,
  and `pays_off` / `at` / `_paths_at` interpolate over history every step. Preallocating,
  dropping temporaries and avoiding repeated `np.errstate` entries may be worth 1.5–2×
  with no new dependency. Untested guess.
- **Numba on the step loop.** Guess: 3–6× single-threaded, more with `prange` over draws.
  Untested. It adds a dependency and a compile on first call (cache it with `cache=True`;
  check the cache directory is writable on Community Cloud). The closures inside `simulate`
  will need restructuring into plain functions over arrays.
- **Process pool over draws.** Measured 2.9× on 4 cores, but Community Cloud has at most 2
  throttled cores, so this only pays off after a hosting move. `simulate` draws from
  `np.random.default_rng(int(p["seed"]))` at line 680, so chunking needs per-chunk seeds
  and the numbers shift once.

Constraints that must survive:

- Same settings must give the same numbers (CLAUDE.md, *Random seed*). No cached function
  may draw unseeded. `test_toggling_a_box_back_restores_the_numbers` guards it.
- `_tk_simulate` and `_cn_tk_simulate` are `st.cache_data` wrappers keyed on
  `_TK_SOURCE_DIGEST`, which invalidates when the model source changes. Keep that working.
- If results change at all (float reordering counts), say so plainly and update the tests
  that pin numbers, rather than loosening tolerances quietly.

Done when: the app's own `simulate` calls run about 3× faster than the baseline, the takeoff
tests pass, and a Takeoff setting change on the live site is under about 8s. Judge by the
multiple, not a fixed time, since machines differ about 2×. `perf/bench_simulate.py` runs bare
`DEFAULTS` (no per-draw human curve, compute rates or follower), so it misses most of
what the app runs: time the app's real calls instead (capture them by wrapping
`takeoff_model.simulate` under `AppTest`).

**Status (2026-11-11, laptop):** done locally. The step loop is compiled with numba
(`docs/takeoff.md`, *Two copies of the step loop*), on top of an in-place cleanup that was
bit-identical. At 2 threads, the live host's most: US run 2.02 → 0.33s, China's follower
runs 2.44 → 0.23s; a browser setting change 6.2 → ~2.1s; cold Takeoff server-side
6.95 → 3.1s, China 10.9 → 3.0s. Numbers moved only by float reordering (a draw or two per
run, relative 1e-8). Still open: the live re-measure, and the one-time compile (~15s here,
likely 2-3× that on the live host) the first visitor after each deploy pays, which step 2's
server-start warm-up should absorb. Whether numba's cache survives a Community Cloud
sleep is unknown.

### 2. Warm the default-settings cache

The first visitor after a deploy or a wake-up pays 13–22s per heavy tab. Options: run the
default-settings simulations once at server start in a background thread, or ship the
default results on disk. Mind the seed rule above, and that `_tk_simulate` has
`max_entries=12`.

Done when: first load of Takeoff, Pacing and China after a restart is within a second or
two of the warm load.

### 3. Re-measure on the live site, then decide on hosting

Run `node perf/time_browser.js https://takeoff-tracker.streamlit.app/~/+/` after deploying
steps 1 and 2. If a setting change is still over about 8s, move the same Streamlit app to
a host with 2–4 dedicated cores (a small VM or container host). At that point the process
pool from step 1 also becomes worth doing. Peter decides this one; it costs money and
changes the URL unless a redirect is set up.

### 4. Optional: fragments on the evidence half

Wrap `render_rsi`'s sections in `st.fragment` so their widgets do not rerun the Takeoff
half. The catch: seeding lives in the dispatch (`with _seeded_rng(_APP_SEED)` at the end of
`visualize_projection.py`), so a fragment-only rerun needs its own seeded scope or the
numbers drift. Worth about a second per interaction; skip it if steps 1–3 are enough.

### Not worth doing

- Thinning chart traces or downsampling fan bands: payload is 1.6 MB and not the bottleneck.
- A FastAPI-plus-React frontend over the same Python: keeps the slow part, loses the widgets.

## When a rewrite would be right

If, after steps 1–3, the app still needs to be a public artifact with instant first paint,
mobile support and link previews. The target then is a static site with precomputed
default results and the model ported to run in the browser (JS or WASM), so the visitor's
machine does the work. That means re-validating 1,662 lines of model against its tests and
rebuilding 169 widgets, 65 charts and the URL/reset/seed machinery. Weeks, not days.

## Reproducing the numbers

```bash
pip install -r requirements-dev.txt pyinstrument

# Server-side time per tab: cold, then two warm reruns, plus chart payload.
_VP_SAMPLES=2000 python perf/time_tab.py takeoff

# Function-level profile of one run: cold | warm | set:<widget kind>:<key>:<value>
python perf/profile_tab.py takeoff cold 7000
python perf/profile_tab.py china cold 9000
python perf/profile_tab.py takeoff set:number_input:tk_returns:1.1 7000

# The simulation alone.
python perf/bench_simulate.py

# Real browser, local server (start `streamlit run visualize_projection.py` first) or live.
node perf/time_browser.js
node perf/time_browser.js https://takeoff-tracker.streamlit.app/~/+/
```

Notes on the scripts:

- `time_tab.py` and `profile_tab.py` use `AppTest` with the shared script cache from
  `conftest.py`. Each invocation is a fresh process, so "cold" really is cold.
- `profile_tab.py` wraps `LocalScriptRunner._run_script` because the script runs in its own
  thread, where a profiler started on the main thread sees nothing. Times under the
  profiler run about 1.5–2× the unprofiled ones.
- `time_browser.js` changes *Returns to research (r)* by 0.07 and 0.13. `st.cache_data` is
  shared across visitors, so reuse of a value someone already tried returns instantly;
  change the increments if the numbers look too good.
- The live app's real page is under `/~/+/`; the bare URL redirects through
  `share.streamlit.io` for auth.

## Open questions for Peter

- Who is the audience: a few colleagues, or public readers? Public readers raise the value
  of fast first paint, which is the one thing Streamlit cannot give.
- Is a paid host acceptable if step 1 does not get the live site under about 8s?
- Is a one-time shift in the Takeoff numbers acceptable if the faster simulation reorders
  floating-point work or reseeds per chunk?
