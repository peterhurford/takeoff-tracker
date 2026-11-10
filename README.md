# AI Capability Projections

This interactive Streamlit dashboard has eleven tabs covering benchmark capability,
labor automation, cyber offense, revenue, compute buildout, takeoff to ultraintelligence,
and public frontier-risk assessments. Empirical panels project trends with uncertainty
bands; Takeoff explores scenarios; Frontier Thresholds records reported assessments
and safeguard changes.

> Note: In many cases, these are **projections**, not forecasts: they assume the current trend continues.

## Quick start

```bash
pip install -r requirements.txt
streamlit run visualize_projection.py     # or: make app
```

Opens at http://localhost:8501. Python 3.11 (`.python-version`).

Pick a tab from the sidebar radio (the last five sit under *More*). Every tab deep-links:
`?tab=pacing` opens the Pacing tab, a URL with no `?tab=` opens Takeoff,
and the sidebar's *Share view* button copies a URL carrying your current control settings.

## The tabs

| Tab | `?tab=` | Data source | What it measures |
|---|---|---|---|
| ECI | `eci` | `epoch_capabilities_index.csv` | Epoch's Capabilities Index, a pooled benchmark score: where each lab stands, a projection, and how many months one entity trails another |
| Remote Labor Index | `rli` | `_RLI_RAW` (hardcoded) | Share of real remote-work projects completed. Fitted in logit space |
| Data Centers | `datacenters` | `data_centers.csv` + `data_center_timelines.csv` | H100-equivalents, power, cost, time-to-train; a US-vs-China buildout panel, world compute share by region, then Compute ⟷ ECI and the ECI forecast |
| China | `china` | Data centers + ECI, `china_compute_sources.csv`, `cts_duv_production.csv` | How far behind China is in compute and in capability, and whether the gap is closing |
| Takeoff | `takeoff` | `takeoff_model.py`; the evidence half reads `_RSI_RAW` / `_RSI_SURVEY`, `openai_experiment_velocity.csv`, `anthropic_rd_automation.csv`, `metr_aeci.csv` | A research-automation simulation from today, with coding automation inherited from the blended milestone projection; below it, the AI R&D evidence and the *Capabilities Milestones* cards |
| Pacing | `pacing` | Data centers + ECI, Takeoff's run | If the US slows or pauses frontier training, when China reaches the US frontier |
| METR Horizon | `metr` | `benchmark_results_1_1.yaml` | Task horizon length, the longest task a model completes reliably. log₂(minutes) |
| Revenue | `revenue` | `_OPENAI_REVENUE` / `_ANTHROPIC_REVENUE` / `_CN_REVENUE` (hardcoded) | OpenAI, Anthropic and Chinese-lab ARR |
| UK Cyber | `ukcyber` | `aisi_cyber_narrow.csv`, `aisi_cyber_tlo.csv` | AISI cyber success rates, and how many months open-weight models trail the closed frontier |
| Employment | `employment` | RLI frontier + assumptions | Unemployment / jobs displaced under slider assumptions |
| Frontier Thresholds | `thresholds` | `frontier_thresholds.json` | Lab/domain event timeline separating assessments, precautions, alerts, policy changes, reassessments, and operational responses |

An unknown `?tab=` opens the default tab; retired slugs get no special handling.

Each tab has its own render function (`grep '^def render_'`), its own sidebar controls, and a
reset button backed by per-tab defaults and tracked keys.

### Takeoff scenarios

Open `?tab=takeoff`. Research starts **today with partial automation**, and full coding
automation inherits the final blended milestone projection from the tab's evidence half.
The simulation and every card run to the end of `_TK_SIM_END_YEAR`; the horizon control only
crops the charts. China's takeoff runs beside it as a follower.

See [TAKEOFF_MODEL.md](TAKEOFF_MODEL.md) for equations, interpretation, and remaining limits,
and `docs/takeoff.md` for the design record.
Tests: `pytest test_takeoff_model.py test_integration.py::TestTakeoffTab`.

### Frontier threshold timeline

Open `?tab=thresholds`. Choose one risk category: Cybersecurity, Biological /
chemical, Autonomy / AI R&D, or Persuasion. Each lab has a separate bordered panel
with a category-specific summary and a small timeline of selected milestones.
Labels and hovers use domain-specific wording, even when the underlying source
record covers several domains. No range slider or legend is shown. Each panel includes a compact milestone table
and a visible explanation for the selected event. Additional context appears as
small chart points; only the main milestones receive inline labels. The full
chronology remains collapsed. Category and archive filters round-trip
through Share view; CSV export retains complete records.

The event records in `frontier_thresholds.json` transcribe a supplied timeline (its
`as_of` field gives the date), without independent source verification. Some source rows are split by
assessment type or configuration. Edit that file to update the chronology; keep status,
model/configuration, domain, policy version, date qualifications, and safeguards together.
`frontier_thresholds.py` provides filtering, charting, CSV export, and the tab UI.

### Projection engine

Three bases, offered per tab where they make sense:

- **Linear** — one OLS fit, extrapolated.
- **Piecewise linear** — multi-segment OLS at user-chosen breakpoints; the last segment is extrapolated.
- **Superexponential** — doubling time itself decays (`superexp_trajectory()`), with a floor.

All of them sample `N_SAMPLES` (5,000) trajectories into a Plotly fan chart with 50/80/90%
bands. Bounded metrics (RLI, UK Cyber, CoBench) are fitted in **logit** space so the
trend can't run through 100%; unbounded ones (METR horizon, revenue, survey speedup) are
fitted in log space.

"Project as of" backtests: it projects from a historical vantage point and colors later
actual models by which CI band they landed in (`_backtest_stats()`).

## Repository layout

```
visualize_projection.py   the whole app — loaders, engines, the render functions
test_visualize_projection.py   unit tests against a fake Streamlit module
test_integration.py            integration tests through Streamlit's AppTest runtime
takeoff_model.py          the takeoff simulation
frontier_thresholds.py    the Frontier Thresholds tab
test_*.py                 the other test files (takeoff model, thresholds, ECI converter)
conftest.py               test-speed setup (see below)
CLAUDE.md, docs/          the design record (CLAUDE.md indexes docs/) — read before changing anything non-trivial
.claude/commands/update_data.md   the data-refresh recipe
*.csv, *.yaml             the data feeds
```

There is no build system and no CI. Runtime deps are `streamlit`, `numpy`, `plotly`,
`pyyaml`.

The app is deliberately one file. It is large, but every tab shares the helpers at the top
(`pretty()`, `fit_line()`, the samplers, `_ss_number_input()`, `_fn_caption()`), and
splitting it has not been worth the import churn. Navigate by `grep`, not by scrolling.

## Development

```bash
pip install -r requirements-dev.txt
pytest -v                     # or: make tests
pytest -v -n0                 #     make tests-serial (needed for --pdb or live output)
_VP_SAMPLES=5000 pytest -v    #     make tests-full   (production sample count)
pytest test_visualize_projection.py::TestPretty::test_known_name -v
```

Two environment variables shape a test run:

- `_VP_TESTING=1` skips the render dispatch at the bottom of the file, so the module imports
  without a Streamlit server. Handy for poking at a loader directly:
  ```bash
  _VP_TESTING=1 python3 -c "import visualize_projection as v; print(len(v.load_eci_frontier()))"
  ```
- `_VP_SAMPLES` sets the Monte Carlo trajectory count. `conftest.py` turns it down to 400 for
  tests; nothing asserted depends on the count.

### The suite is fast on purpose

`conftest.py` shares one bytecode cache across every
`AppTest.run()` (patching **both** places Streamlit constructs a `ScriptCache` — patch one
and the win vanishes), shrinks the Monte Carlo, and `pytest.ini` runs `-n auto`. An
`AppTest` case costs about 0.1s, so prefer adding one to skipping coverage. What is
expensive is defeating the shared cache: don't write a test that mutates
`visualize_projection.py` on disk or builds its own runner out of `streamlit.testing`
internals.

### Seeded runs

Every tab's rerun draws its Monte Carlo inside `_seeded_rng(_APP_SEED)`, so the same
settings give the same numbers; Takeoff reseeds from its own `tk_seed`. No cached function
may draw unseeded (`test_toggling_a_box_back_restores_the_numbers`).

## Data

Local data files and hardcoded tables supply the indicators. `.claude/commands/update_data.md` has
the full refresh recipe, including the AISI cyber data that is deliberately *not* ingested.

| File / table | Source | Type |
|---|---|---|
| `benchmark_results_1_1.yaml` | METR Horizon v1.1 | download |
| `epoch_capabilities_index.csv` | Epoch AI ECI scores + AI models (training compute) | download, converted by `convert_eci.py` |
| `data_centers.csv` / `data_center_timelines.csv` | Epoch AI Frontier Data Centers | download |
| `_RLI_RAW` | Scale Labs Remote Labor Index | hand-edited |
| `_RSI_RAW` / `_RSI_SURVEY` | Anthropic, Redacted Risk Report §3.4; Fable 5.1 system card (CoBench, rescaled) | hand-edited, read off a figure |
| `openai_experiment_velocity.csv` | OpenAI, *Research acceleration*, “Experiment velocity has increased” | 32 weekly browser-hover tooltip values; 2025 = 1× |
| `_OPENAI_REVENUE` / `_ANTHROPIC_REVENUE` / `_CN_REVENUE` | Press reports, company disclosures, a third-party tracker | hand-edited |
| `anthropic_rd_automation.csv` | Anthropic R&D Automation Index | read off a figure |
| `metr_aeci.csv` | METR's AI R&D acceleration assessment (AECI) | **chart-digitized** |
| `china_compute_sources.csv` | China's AI compute by source: Epoch, IFP, then a projection | hand-assembled, derivations in its `#` header |
| `cts_duv_production.csv` | CTS lithography report, Table 45 | transcribed |
| `frontier_thresholds.json` | A supplied lab/domain event timeline | hand-edited |
| `aisi_cyber_narrow.csv` / `aisi_cyber_tlo.csv` | UK AISI cyber blog posts | **digitized from published PNGs** |

Three things to know before touching data:

1. **Some of it is digitized, not published.** AISI prints no numbers for its cyber figures;
   both CSVs were recovered from the images by pixel analysis, and each file's `#` header
   records the calibration and the checks that validate it. Refreshing them is a
   *figure-unchanged check*, not a download. `test_optimistic_bracket_reproduces_aisi_published_lags`
   and friends are the calibration guards — if you change the digitization, they must still pass.
2. **Epoch recomputes ECI live**, so existing rows drift on every pull. That's expected. What
   isn't expected is losing rows: diff by key column before overwriting any CSV
   (ECI = `Model version`, DC metadata = `Name`, timelines = `Data center` + `Date`).
3. **Every timeline row needs a metadata row.** After overwriting the data-center CSVs,
   `set(timelines['Data center']) - set(metadata['Name'])` must be empty (see
   `docs/data-sources.md`).

After any data change, sanity-check the relevant loader with `_VP_TESTING=1 python3 -c ...`,
then run the tests.

## Contributing

**Read `CLAUDE.md` first**, then the `docs/` file it names for the area you are changing. Together they are the design record: for every non-obvious choice in the app
it says what the choice is, what the wrong-looking alternative was, and which test holds the
line. Most surprising-looking code in this repo is deliberate and documented there.

Conventions that will come up:

- **Every claim gets a guarding test.** The suite is large because the app's charts encode
  judgment calls; a change that alters a number should move a test with it.
- **Caveats hang on the thing they qualify**, not in a paragraph. Use `st.metric(help=…)`
  where a metric exists, `_fn_caption(text, (phrase, note))` to make a phrase in a caption
  hoverable in place, and `_fn_line()` for a line that must not read as fine print.
  `test_footnotes_anchor_to_their_phrase` holds the app at zero unanchored footnotes.
- **Don't fork shared machinery.** The Pacing and China tabs are built from the
  Data Centers tab's aggregation functions on purpose — two tabs quoting different numbers for
  the same quantity reads as a bug. Several tests exist only to keep the engines honest across
  tabs.
- **Adding a tab** means: a `render_*()` function, an entry in `_TAB_OPTIONS` and
  `_SLUG_FOR_TAB`, a branch in the dispatch block at the bottom of the file, and a
  `_<TAB>_DEFAULTS` / `_<TAB>_RESET_KEYS` pair. Session-state number inputs go through
  `_ss_number_input()` so they survive a rerun and round-trip through the URL.
- **Adding a company to the ECI tabs** is one row in `_ECI_COMPANIES` — the maps both tabs use
  are derived from it at import. Don't hand-write them.
Run `pytest` before opening a PR. Data refreshes and code changes are easier to review apart,
so please keep them in separate commits.

## Units

| Context | Internal unit |
|---|---|
| METR | log₂(minutes), displayed as hours. Work-time: 1d = 8h, 1w = 40h, 1mo = 176h, 1y = 2000h |
| ECI | Linear score. DPP = days per +1 ECI point |
| RLI / UK Cyber / CoBench | 0–100, projected in logit space |
| Revenue | ARR, billions USD |
| Data centers | H100-equivalents, MW, USD, and training runs per 2-month window (displayed as time-to-train-one-model) |

## License

None yet — the repo ships no license file, so default copyright applies. Ask before reusing
or redistributing.
