"""AI research from today through takeoff; assumptions and explicit calibration.

Times are years after today; coding automation is an inherited milestone.
Natural logs represent capability and efficiency relative to today's system.
All randomness is local and seeded; every setting uses the same base draws.
"""

import hashlib
from collections import namedtuple
from statistics import NormalDist
from pathlib import Path

import numpy as np


MODEL_VERSION = "takeoff-v32-followers"
SOURCE_DIGEST = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORKFLOW_STAGES = ("Research direction", "Experiment design and interpretation",
                   "Verification and integration")
WORKFLOW_KEYS = ("direction", "experiments", "verification")
# Share of an unassisted researcher's time in each stage (the app's `_TK_ACTIVITIES`).
WORKFLOW_WEIGHTS = np.array([0.2, 0.7, 0.1])
# What R&D compute is used for; a `compute_cut` can differ by use.
COMPUTE_USES = ("training", "experiments", "agents")
# RSI: research direction (the stage that chooses what to try next) needs at
# most `full_human`% of baseline human hours, once coding is automated.
# Capability past it is read as ECI.
MILESTONES = ("RSI",)
DEFAULTS = {
    "onset_low": 6, "onset_high": 24, "years": 10, "seed": 42,
    "software_months": 8.4, "compute_growth": 2.0,
    "training_months": 3.0, "validation_months": 1.0,
    "training_share": 40, "experiment_share": 40,
    "taste_slope": 0.8, "coding_slope": 0.8,
    "transfer": 60, "difficulty": 0.5, "parallelization": 0.5,
    "uncertainty": 40,
    "human_direction": 40.0, "human_experiments": 30.0, "human_verification": 50.0,
    "half_direction": 6.0, "half_experiments": 9.0, "half_verification": 12.0,
    "human_floor": 0.0, "full_human": 5.0,
    # Autopilot: from a draw's RSI, no research stage needs people at all (the
    # hours left in other stages are dropped). 0 keeps each stage's own decline.
    "rsi_autopilot": 1.0,
    # `fast_share` is each draw's median: logit-normal per draw, its spread
    # 1-sigma of the log-odds times 100 (100 is about 8-55% around 25%).
    "fast_share": 25.0, "fast_months": 1.0, "fast_share_spread": 100.0,
    "coding_today": 70.0,
    # Steady state: the next model ships with one full cycle (training +
    # validation) of discoveries not yet deployed.
    "pipeline_months": 4.0,
    "rsi_trend_weight": 50.0, "rsi_trend_months": 12.0, "rsi_useful_growth": 100.0,
    # Labor and experiment compute combine as a CES mean with this exponent:
    # -1 is the harmonic mean (strong complements), 0 Cobb-Douglas.
    "substitution": -0.2,
    # Speed of AI on work it has taken over, relative to the people it
    # replaced; sets how much a falling human share speeds research (Amdahl).
    "ai_speed": 30.0,
    # More copies: AI's share of research labor scales with the deployed
    # model's algorithmic efficiency to this power, as the same inference
    # compute runs more AI researchers. 0 leaves the number of copies fixed.
    "ai_copies": 1.0,
    # Share of the non-AI input growth that would hold today's pace with AI
    # frozen; 0 leaves compute the only growing input (no hiring, experiment
    # compute growing with the frontier).
    "baseline_inputs": 100.0,
    # Human research staff growth a year until a draw's RSI, and after it.
    # More staff speed the human share of the work (Amdahl), so they matter
    # until autopilot and not after.
    "hiring_growth": 30.0, "staff_after_rsi": -30.0,
    # Change in the judgment elasticity per 10x gain in capability (%): above 0
    # judgment gains compound as AI gets more capable (b falls), below 0 they
    # fade (b rises). 0 keeps today's measured rate throughout.
    "judgment_drift": 0.0,
    # Ceiling on AI research judgment, as a multiple of today's AI judgment;
    # 0 is no ceiling. AI Futures caps AI research taste near 4x the best human.
    "judgment_cap": 0.0,
    # Delegation follows judgment: research direction moves along its
    # human-hours curve J^k times as fast, J being AI research judgment over
    # today's AI's (1 today), so labs hand direction over sooner as AI picks
    # experiments better. Unmeasured; 0 keeps the curve's own pace.
    "direction_adoption": 0.5,
    # AI research judgment against people's today, on the direction AI does.
    # Quality is normalized to 1 today, so it only changes what handing
    # direction over buys; 1 counts AI and people alike.
    "judgment_today": 1.0,
    # Serial speed-up: validation shrinks as AI takes over verification, and a
    # new training run shortens as capability grows faster than today (a run
    # should not outlast the time better methods take to beat it). 0 holds
    # both at their settings.
    "serial_speedup": 1.0,
    # Reallocation: labs re-split the non-training compute between running AI
    # researchers and experiments as AI changes what each is worth, by the
    # labor-compute mean's first-order condition, anchored at today's split.
    # 0 keeps the split fixed.
    "reallocate_compute": 1.0,
    # Per-draw spread on the four settings that decide whether takeoff runs
    # away (TAKEOFF_MODEL.md, *Parameter uncertainty*): 1-sigma of ln r,
    # 1-sigma of ln(judgment elasticity), 1-sigma of the drift in percentage
    # points, and 1-sigma of ln(elasticity of substitution 1 / (1 - rho)).
    "returns_spread": 65.0, "judgment_spread": 70.0,
    "drift_spread": 15.0, "substitution_spread": 80.0,
    # Compute growth keeps this share of its log rate from `compute_slow_years`
    # after today (the app sets end-2030, where Epoch's feasibility analysis
    # stops); an assumption, not a fitted rate.
    "compute_slowdown": 50.0, "compute_slow_years": 4.0,
    # Multiplier on each draw's log compute growth after its own RSI date: AI
    # speeding chip design, fabs and spending. It waits `rsi_compute_delay`
    # months (a chip generation, a fab's build), then ramps in linearly over
    # `rsi_compute_ramp` months. 1 leaves compute as projected; the size is an
    # assumption, with no published estimate.
    "rsi_compute_boost": 2.0, "rsi_compute_delay": 18.0, "rsi_compute_ramp": 12.0,
    # Software ceiling (Forethought): returns to research fall linearly to 0
    # as algorithmic efficiency nears a limit drawn uniformly this many orders
    # of magnitude above today's. A high of 0 removes it.
    "ceiling_low_oom": 6.0, "ceiling_high_oom": 16.0,
    # Correlation between a draw's returns to research r and how far its
    # ceiling is: algorithms near their limits buy less per unit of effort.
    "ceiling_returns_corr": 0.5,
    # Share of algorithmic gains that pay off only at scale (Gundlach et al.
    # 2025): that share counts in full once training compute has grown
    # `scale_lag_oom` orders of magnitude past where it was when the gain was
    # found. Before today history is taken as balanced, so until compute has
    # grown one lag past today the lag cancels and that share is held to
    # history's software-per-compute ratio. Logit-normal share and lognormal
    # lag per draw; spreads are each 1-sigma (log-odds, log) times 100.
    "scale_dependent": 50.0, "scale_dependent_spread": 100.0,
    # Correlation between a draw's labor-compute elasticity and its
    # scale-dependent share, both readings of how compute-bound algorithmic
    # progress is: where labor stands in for compute, fewer gains need scale.
    "compute_bound_corr": 0.5,
    "scale_lag_oom": 0.3, "scale_lag_spread": 70.0,
}
# Every spread at zero: each draw uses the settings themselves.
POINT_ESTIMATE = {"uncertainty": 0, "returns_spread": 0, "judgment_spread": 0,
                  "drift_spread": 0, "substitution_spread": 0, "scale_dependent_spread": 0,
                  "scale_lag_spread": 0, "fast_share_spread": 0}
PRESETS = {
    "Central": {},
    "Fast": {"software_months": 6.0, "training_months": 1.0,
             "validation_months": 0.5, "taste_slope": 1.2,
             "transfer": 90, "difficulty": 0.2},
    "Bottlenecked": {"software_months": 18.0, "compute_growth": 1.3,
                     "training_months": 6.0, "validation_months": 2.0,
                     "taste_slope": 0.4,
                     "transfer": 20, "difficulty": 1.0},
}


def validate(params):
    """Reject invalid model inputs, including values from shared URLs."""
    p = dict(DEFAULTS, **params)
    if not all(np.isfinite(v) for v in p.values()):
        raise ValueError("All takeoff settings must be finite numbers.")
    if not 0 <= p["onset_low"] <= p["onset_high"] <= 120:
        raise ValueError("Coding automation dates must be ordered within 0–120 months.")
    if not 0 < p["years"] <= 30:
        raise ValueError("The simulation horizon must be between 0 and 30 years.")
    if p["training_share"] <= 0 or p["experiment_share"] <= 0 \
            or p["training_share"] + p["experiment_share"] >= 100:
        raise ValueError("Reserve positive compute shares for training, experiments, and agents.")
    if not 0 <= p["transfer"] <= 100 or not 0 <= p["uncertainty"] <= 100:
        raise ValueError("Transfer and uncertainty must be between 0 and 100%.")
    if not all(0 <= p[k] <= 200 for k in ("returns_spread", "judgment_spread",
                                          "drift_spread", "substitution_spread")):
        raise ValueError("Parameter spreads must be between 0 and 200%.")
    if p["software_months"] <= 0 or p["training_months"] <= 0 \
            or p["validation_months"] < 0 or p["compute_growth"] < 1:
        raise ValueError("Use positive doubling/run times and compute growth of at least 1×.")
    if p["taste_slope"] < 0 or p["coding_slope"] <= 0:
        raise ValueError("Research quality slope must be nonnegative and coding slope positive.")
    if p["difficulty"] < 0 or not 0 < p["parallelization"] <= 1:
        raise ValueError("Use nonnegative difficulty and parallelization in (0, 1].")
    if int(p["seed"]) != p["seed"] or not 0 <= p["seed"] < 2**32:
        raise ValueError("Seed must be an integer between 0 and 2³²−1.")
    if not 0 <= p["human_floor"] <= 100 or not 0 <= p["full_human"] <= 100:
        raise ValueError("Human-work floor and automation threshold must be between 0 and 100%.")
    for stage in WORKFLOW_KEYS:
        if not p["human_floor"] <= p["human_" + stage] <= 100 or p["half_" + stage] <= 0:
            raise ValueError("Each workflow's starting human work must be at least its floor, "
                             "and its halving time must be positive.")
    if not 0 <= p["fast_share"] <= 100 or p["fast_months"] <= 0 \
            or not 0 <= p["fast_share_spread"] <= 400:
        raise ValueError("Fast feedback needs a share in [0, 100] and a positive validation cycle.")
    if not 0 <= p["coding_today"] < 95:
        raise ValueError("Today's coding automation must be below the 95% coding milestone.")
    if not 0 <= p["pipeline_months"] <= 12:
        raise ValueError("Initial research pipeline must be between 0 and 12 months of progress.")
    if not 0 <= p["rsi_trend_weight"] <= 100 or not 0 <= p["rsi_useful_growth"] <= 100 \
            or p["rsi_trend_months"] <= 0:
        raise ValueError("RSI trend weights must be percentages and their half-life positive.")
    checks = (
        (-5 <= p["substitution"] <= 0.9, "Substitution must be between -5 and 0.9."),
        (p["ai_speed"] >= 1, "AI speed must be at least 1x."),
        (0 <= p["baseline_inputs"] <= 200, "Baseline input growth must be between 0 and 200%."),
        (-90 <= p["judgment_drift"] <= 300, "Judgment drift must be between -90 and 300%."),
        (0 <= p["compute_slowdown"] <= 100 and p["compute_slow_years"] >= 0,
         "Compute slowdown must be between 0 and 100% over a non-negative number of years."),
        (0.5 <= p["rsi_compute_boost"] <= 5 and 0 <= p["rsi_compute_delay"] <= 60
         and 0 <= p["rsi_compute_ramp"] <= 60,
         "RSI compute boost must be between 0.5x and 5x, with delay and ramp each 0 to 60 months."),
        (0 <= p["ceiling_high_oom"] <= 60
         and (p["ceiling_high_oom"] == 0 or 0 < p["ceiling_low_oom"] <= p["ceiling_high_oom"]),
         "The software ceiling's low end must be positive and at most its high end (at most 60 OOM)."),
        (p["rsi_autopilot"] in (0, 1) and 0 <= p["ai_copies"] <= 2,
         "Autopilot must be on or off, and AI copies between 0 and 2."),
        (p["judgment_cap"] == 0 or p["judgment_cap"] >= 1,
         "The judgment cap must be 0 (off) or at least 1x."),
        (0 <= p["direction_adoption"] <= 2 and 0.25 <= p["judgment_today"] <= 4,
         "Direction adoption must be between 0 and 2, and today's judgment between 0.25x and 4x."),
        (p["serial_speedup"] in (0, 1) and p["reallocate_compute"] in (0, 1),
         "Serial speedup and compute reallocation must each be on or off."),
        (0 <= p["compute_bound_corr"] <= 1 and 0 <= p["ceiling_returns_corr"] <= 1,
         "Correlations must be between 0 and 1."),
        (-90 <= p["hiring_growth"] <= 200 and -90 <= p["staff_after_rsi"] <= 200,
         "Hiring growth and staff after RSI must be between -90 and 200%."),
        (0 <= p["scale_dependent"] <= 100 and 0 <= p["scale_dependent_spread"] <= 400
         and 0 < p["scale_lag_oom"] <= 10 and 0 <= p["scale_lag_spread"] <= 400,
         "Scale-dependent share must be 0 to 100%, its lag above 0 and at most 10 OOM, "
         "and each spread 0 to 400%."),
    )
    for ok, message in checks:
        if not ok:
            raise ValueError(message)
    return p


def calibrate_feedback(experiment_growth, compute_growth, capability_growth,
                       yield_change=1.0, validated_growth=None, transfer=.6,
                       coding_slope=.8, parallel=.5, substitution=-0.5,
                       automation_growth=1.0):
    """Effective quality elasticity after the model's own research equation
    has accounted for compute, coding help and `automation_growth` (the
    Amdahl labor gain from people's falling share over the same window).

    Aggregate experiments are a proxy, not causal identification. A supplied
    validated-progress ratio supersedes that proxy. Ratios compare matched
    periods; current assistance is already in today's starting progress rate.
    """
    values = [experiment_growth, compute_growth, capability_growth, yield_change]
    if validated_growth is not None:
        values.append(validated_growth)
    values.append(automation_growth)
    if not all(np.isfinite(v) and v > 0 for v in values) or capability_growth <= 1:
        raise ValueError("Calibration needs positive ratios and capability growth above 1×.")
    if not 0 < transfer <= 1 or not 0 < parallel <= 1 or coding_slope < 0:
        raise ValueError("Calibration requires positive transfer and valid elasticities.")
    useful_growth = experiment_growth * yield_change if validated_growth is None else validated_growth
    residual = useful_growth / compute_growth ** parallel
    coding = ((1 - transfer + transfer * capability_growth ** coding_slope)
              * (1 - transfer + transfer * automation_growth)) ** parallel
    quality = residual / _ces(coding, 1.0, substitution)
    slope = np.log(max(1.0, (quality - 1 + transfer) / transfer)) / np.log(capability_growth)
    return dict(quality_slope=float(slope), resource_adjusted_growth=float(residual),
                useful_growth=float(useful_growth), coding_factor=float(coding),
                labor_part=float(_ces(coding, 1.0, substitution)), quality=float(quality),
                boundary=bool(quality < 1),
                basis="validated progress" if validated_growth is not None else "experiment proxy")


def calibrate_workflow(baseline_hours, before_hours, now_hours, capability_growth,
                       baseline_rate, floor):
    """Fit one matched stage, including intervention/rescue hours in its totals."""
    values = [baseline_hours, before_hours, now_hours, capability_growth, baseline_rate]
    if not all(np.isfinite(v) and v > 0 for v in values) or capability_growth <= 1:
        raise ValueError("Enter positive matched-project hours and capability growth above 1×.")
    before, now = 100 * before_hours / baseline_hours, 100 * now_hours / baseline_hours
    if not 0 <= floor < now < before <= 100:
        raise ValueError("Matched human hours must decline, remain above the floor, and not exceed baseline.")
    equivalent_months = 12 * np.log(capability_growth) / baseline_rate
    half_months = equivalent_months / np.log2((before - floor) / (now - floor))
    return dict(human_now=now, half_months=half_months)


def after_coding(samples, onset):
    """Durations only where both calendar events are modeled; retain censoring."""
    return np.subtract(samples, onset, out=np.full_like(samples, np.inf),
                       where=np.isfinite(samples) & np.isfinite(onset))


def judgment_gain_log(effective, slope, drift):
    """Log judgment gain at capability `effective` (natural log of effective
    compute): the integral of an elasticity that starts at `slope` and changes
    by `drift` (a fraction) per 10x of capability."""
    k = np.log1p(drift) / np.log(10)
    flat = np.abs(k) < 1e-12
    safe = np.where(flat, 1.0, k)
    # Capped short of overflow: a draw that far out has already diverged.
    return np.where(flat, slope * effective,
                    slope * np.expm1(np.minimum(safe * effective, 700)) / safe)


def ai_judgment_log(effective, slope, drift, transfer, cap=0.0):
    """Log of AI research judgment at capability `effective`, over today's AI's
    (0 today): the judgment gain through the transfer discount, held under
    `cap` (a multiple of today's; 0 for none). Zero without transfer."""
    if not transfer:
        return np.zeros(np.shape(effective))
    out = np.logaddexp(np.log1p(-transfer) if transfer < 1 else -np.inf,
                       np.log(transfer) + judgment_gain_log(effective, slope, drift))
    return np.minimum(out, np.log(cap)) if cap else out


def _ces_log(x, y, rho):
    """Log of the CES mean of exp(x) and exp(y), equal to 1 when both are 1."""
    flat = np.abs(rho) < 1e-9
    if not np.any(flat):        # the usual case: skip the branch np.where drops
        return (np.logaddexp(rho * x, rho * y) - np.log(2)) / rho
    safe = np.where(flat, 1.0, rho)
    return np.where(flat, (x + y) / 2,
                    (np.logaddexp(safe * x, safe * y) - np.log(2)) / safe)


def _ces(a, b, rho):
    return np.exp(_ces_log(np.log(a), np.log(b), rho))


def normal_scores(uniform):
    """Standard-normal quantiles of draws uniform on [-1, 1]: the same
    rank in every draw, so paired scenarios stay paired."""
    u = np.clip((np.asarray(uniform) + 1) / 2, 1e-12, 1 - 1e-12)
    return np.vectorize(NormalDist().inv_cdf, otypes=[float])(u)


# Points the leak's absorption window is read at (its arrival spread evenly).
LEAK_POINTS = 4
# A follower's inflow channels, in the order the app stacks them.
FOLLOW_CHANNELS = ("distillation", "leak", "theft", "weights")
# What `simulate(follower=...)` takes. Paths are (draws x months) on `years`
# (years from today, increasing); levels are ECI.
FOLLOWER_KEYS = {
    "years": "the leader's monthly grid",
    "eci": "the leader's modeled ECI per draw, non-decreasing (its hours' index)",
    "capability": "the leader's log capability on the same grid",
    "rate": "the leader's log capability growth a year today, per draw",
    "ppy": "the leader's ECI growth a year today",
    "teacher": "the leader's released ECI, which distillation closes on",
    "software_eci": "the leader's algorithmic ECI (released), which leaks",
    "software_ppy": "the leader's algorithmic ECI a year before today",
    "eci_now": "the follower's ECI today, per draw",
    "weights": "(ECI per unit log compute, per unit log software) for the follower",
    "distill": "share of the ECI gap distillation closes a year (or one per draw)",
    "leak": "share of the leader's algorithmic progress that leaks, each idea "
            "arriving spread evenly over `absorb` years (or one per draw)",
    "theft": "share of the leader's algorithmic progress stolen at once",
    "absorb": "years over which a leaked idea reaches the follower, evenly",
}
# Optional follower inputs, for policy that changes the channels over time.
# Scales are (months,) or (draws x months) on `years`; times are years from
# today (+inf for never).
FOLLOWER_OPTIONAL = {
    "distill_scale": "multiplies distillation at each month",
    "leak_scale": "multiplies the leak by the month an idea left the leader",
    "theft_scale": "multiplies the share stolen at each month",
    "trained": "the leader's trained ECI, which leaked and stolen ideas close on",
    "theft_jump": "(time, share, ECI gap not to copy, ECI lift): a one-off jump of share "
                  "of the gap to the trained leader past that, plus the lift (per draw)",
    "weight_theft": "(time, ongoing): stolen weights lift the follower to the trained "
               "leader then, and each month after if ongoing",
}


def _row_interp(paths, years, back):
    """u (one time per draw) -> each row of `paths` at its own u: linear inside
    the grid, held past its end, run back at `back` a year before it."""
    paths = np.asarray(paths, dtype=float)
    rows = np.arange(len(paths))
    dt = years[1] - years[0]
    last = len(years) - 2

    def at(u):
        u = np.asarray(u, dtype=float)
        x = np.clip(u, 0.0, years[-1]) / dt
        i = np.minimum(x.astype(int), last)
        f = x - i
        v = paths[rows, i] * (1 - f) + paths[rows, i + 1] * f
        return np.where(u < 0, paths[:, 0] + back * u, v)
    return at


def _paths_at(paths, years, u, rows):
    """Rows `rows` of `paths` (draws x `years`) each at its own time `u`:
    linear inside, held past the ends."""
    dt = years[1] - years[0]
    x = np.clip(np.asarray(u, dtype=float), years[0], years[-1])
    i = np.clip(np.searchsorted(years, x, side="right") - 1, 0, len(years) - 2)
    f = (x - years[i]) / (years[i + 1] - years[i]) if dt > 0 else 0.0
    return paths[rows, i] * (1 - f) + paths[rows, i + 1] * f


def _check_path(path, n, label):
    years, logs = (np.asarray(v, dtype=float) for v in path)
    if years.ndim != 1 or len(years) < 2 or np.any(np.diff(years) <= 0) \
            or logs.shape != (n, len(years)) or not np.isfinite(logs).all():
        raise ValueError(f"A {label} path needs one finite row per draw on an increasing grid.")
    return years, logs


def _follower_inputs(follower, n, step=1.0, span=600.0):
    """Check `follower` (`FOLLOWER_KEYS`) and build what `simulate` reads:
    'eci' (capability, software -> the follower's ECI), 'equivalent' (an ECI ->
    the leader's capability there, per draw, from a table every `step` ECI over
    `span` above the lowest start, linear past it at today's rate), 'rate', and
    'teacher' / 'software' (time per draw -> the leader's released ECI and
    algorithmic ECI then)."""
    missing = [k for k in FOLLOWER_KEYS if k not in follower]
    if missing:
        raise ValueError("A follower needs " + ", ".join(missing) + ".")
    years = np.asarray(follower["years"], dtype=float)
    shaped = {k: np.asarray(follower[k], dtype=float)
              for k in ("eci", "capability", "teacher", "software_eci")}
    if len(years) < 2 or np.any(np.diff(years) <= 0) or any(
            v.shape != (n, len(years)) or not np.isfinite(v).all() for v in shaped.values()):
        raise ValueError("Follower paths need one finite row per draw on an increasing grid.")
    per_draw = {k: np.broadcast_to(np.asarray(follower[k], dtype=float), (n,)).copy()
                for k in ("rate", "eci_now")}
    ppy = float(follower["ppy"])
    w = tuple(float(v) for v in follower["weights"])
    # Distillation and the leak may be one share per draw.
    shares = [np.broadcast_to(np.asarray(follower[k], dtype=float), (n,)).copy()
              if k in ("distill", "leak") else float(follower[k])
              for k in ("distill", "leak", "theft", "absorb")]
    if not all(np.isfinite(v).all() for v in per_draw.values()) or (per_draw["rate"] <= 0).any() \
            or not ppy > 0 or len(w) != 2 or not min(w) > 0 \
            or not all(np.isfinite(v).all() for v in shares[:2]) \
            or min(float(np.min(v)) for v in shares) < 0 \
            or not (shares[1] <= 1).all() or not shares[2] <= 1:
        raise ValueError("Follower rates, weights and ECI must be positive and finite; "
                         "shares must be in [0, 1].")
    lead_eci = np.maximum.accumulate(np.minimum(shaped["eci"], 1e5), axis=1)
    cap = shaped["capability"]
    slope = per_draw["rate"] / ppy          # leader capability per ECI point today
    lo = min(float(per_draw["eci_now"].min()), float(lead_eci[:, 0].min())) - 50.0
    grid = lo + step * np.arange(int(span / step) + 1)
    table = np.empty((n, len(grid)))
    for i in range(n):
        top = np.searchsorted(lead_eci[i], grid, side="right")
        inside = np.interp(grid, lead_eci[i], cap[i])
        below = cap[i, 0] + (grid - lead_eci[i, 0]) * slope[i]
        above = cap[i, -1] + (grid - lead_eci[i, -1]) * slope[i]
        table[i] = np.where(grid < lead_eci[i, 0], below,
                            np.where(top >= len(years), np.maximum(above, inside), inside))
    rows = np.arange(n)

    def equivalent(e):
        pos = (np.asarray(e, dtype=float) - lo) / step
        i = np.clip(pos.astype(int), 0, len(grid) - 2)
        f = np.clip(pos - i, 0.0, 1.0)
        inside = table[rows, i] * (1 - f) + table[rows, i + 1] * f
        past = table[rows, -1] + (np.asarray(e) - grid[-1]) * slope
        before = table[rows, 0] + (np.asarray(e) - grid[0]) * slope
        return np.where(pos > len(grid) - 1, past, np.where(pos < 0, before, inside))

    def eci(capability, software):
        return per_draw["eci_now"] + w[0] * (capability - software) + w[1] * software

    raw = {"table": table, "grid": grid, "lo": lo, "step": step, "slope": slope,
           "years": years, "teacher": shaped["teacher"], "software": shaped["software_eci"],
           "ppy": ppy, "software_ppy": float(follower["software_ppy"])}

    def scale(key):
        v = follower.get(key)
        if v is None:
            raw[key] = None
            return lambda u: 1.0
        v = np.broadcast_to(np.asarray(v, dtype=float), (n, len(years)))
        if not np.isfinite(v).all() or (v < 0).any():
            raise ValueError(f"Follower {key} must be finite and non-negative.")
        raw[key] = np.ascontiguousarray(v)
        inside = _row_interp(np.ascontiguousarray(v), years, 0.0)
        # Policy starts today: before it (an idea that left the leader
        # earlier) nothing is scaled.
        return lambda u: np.where(np.asarray(u) < 0, 1.0, inside(u))

    trained = follower.get("trained")
    if trained is not None:
        trained = np.asarray(trained, dtype=float)
        if trained.shape != (n, len(years)) or not np.isfinite(trained).all():
            raise ValueError("The follower's trained leader path needs one row per draw.")
    jump, weights = follower.get("theft_jump"), follower.get("weight_theft")
    if (jump is not None or weights is not None) and trained is None:
        raise ValueError("Theft needs the leader's trained path.")
    raw["trained"] = trained
    return {"eci": eci, "equivalent": equivalent, "rate": per_draw["rate"], "raw": raw,
            "distill_scale": scale("distill_scale"), "leak_scale": scale("leak_scale"),
            "theft_scale": scale("theft_scale"),
            "trained": _row_interp(trained, years, ppy) if trained is not None else None,
            "theft_jump": jump, "weight_theft": weights,
            "eci_now": per_draw["eci_now"], "w": w,
            "teacher": _row_interp(shaped["teacher"], years, ppy),
            "software": _row_interp(shaped["software_eci"], years,
                                    float(follower["software_ppy"])),
            "distill": shares[0], "leak": shares[1], "theft": shares[2],
            "absorb": shares[3]}


def workflow_state(capability_log, baseline_rate, starts, half_months, floor,
                   curve=None, reference_half=None, direction_pace=None, backward=False):
    """Human hours per stage relative to a fixed baseline project.

    Capability progress is measured in years at today's effective-compute
    growth rate. Without `curve`, each stage halves its hours above the floor
    every `half_months`. With `curve` = (years, share), each stage follows that
    shape instead (share relative to its start), at `reference_half` /
    `half_months` its pace: the halving times then only set each stage's
    speed along the curve. `share` is one curve, or one per draw (rows) on an
    evenly spaced `years` grid; further elements give the stages in order
    (research direction first) their own curves of the same form. `direction_pace`, one
    multiple per draw, moves research direction that much faster.

    `backward` reads a capability below today's (negative), as a country
    behind the frontier stands: each stage's hours run back up at its own
    halving time, to at most all of them (1).
    """
    equivalent_years = (np.asarray(capability_log, dtype=float) if backward
                        else np.maximum(capability_log, 0)) / baseline_rate
    stage_years = np.repeat(equivalent_years[:, None], np.shape(starts)[-1], axis=1)
    if direction_pace is not None:
        stage_years[:, 0] = stage_years[:, 0] * direction_pace
    if backward:
        behind = np.exp(-np.log(2) * np.minimum(stage_years, 0) * 12 / half_months)
        ahead = workflow_state(np.maximum(capability_log, 0), baseline_rate, starts,
                               half_months, floor, curve, reference_half, direction_pace)
        return np.minimum(floor + (ahead - floor) * behind, 1.0)
    if curve is None:
        decline = np.exp(-np.log(2) * stage_years * 12 / half_months)
    else:
        years, share = curve[0], curve[1]
        along = stage_years * reference_half / half_months

        def follow(shape, at):
            if np.ndim(shape) == 1:
                return np.interp(at, years, shape / shape[0])
            # One curve per draw on a shared, evenly spaced grid; flat
            # indices pick the same cells as shape[rows, i0], faster.
            last = len(years) - 1
            pos = np.clip(at / (years[1] - years[0]), 0, last)
            i0 = np.minimum(pos.astype(int), last - 1)
            w = pos - i0
            flat = np.ravel(shape)
            cell = np.arange(len(shape))[:, None] * shape.shape[1] + i0
            return (flat[cell] * (1 - w) + flat[cell + 1] * w) / shape[:, :1]
        # Stages with their own curves are overwritten below, so the shared
        # curve is read only for the rest.
        if len(curve[2:]) >= along.shape[1]:
            decline = np.empty_like(along)
        else:
            decline = follow(share, along)
        for i, own in enumerate(curve[2:]):     # stages with their own curves
            decline[:, i:i + 1] = follow(own, along[:, i:i + 1])
    return floor + (starts - floor) * decline


def progress_multiple(previous_software, new_software, cycle_years, baseline_rate):
    """Delivered fixed-quality software-efficiency progress per calendar year.

    Log efficiency is proportional to training-compute savings at fixed quality.
    Physical compute growth is excluded. Baseline is the already AI-assisted
    validated software progress rate today.
    """
    return np.maximum(new_software - previous_software, 0) / (cycle_years * baseline_rate)


def log_level(t, early, late, at):
    """Log of an input growing at `early` a year until `at`, then `late`."""
    return early * np.minimum(t, at) + late * np.maximum(np.subtract(t, at), 0)


def grown(t, early, late, at):
    """Integral from 0 to t of exp(log_level): the input accumulated."""
    def e(g, x):
        x = np.asarray(x, dtype=float) * np.ones_like(g)
        return np.divide(np.expm1(g * x), g, out=x.copy(), where=g != 0)
    head = np.minimum(t, at)
    return e(early, head) + np.exp(early * head) * e(late, np.maximum(np.subtract(t, at), 0))


def ceiling_step(log_x, log_amount, k, ceiling):
    """Log of x = 1 - S / ceiling after research `amount` (log_amount) under
    dS/dt = A x^k: returns to research falling linearly to 0 at the ceiling
    (k = difficulty x ceiling). Exact for any k; x reaches 0 only for k < 1."""
    k = np.asarray(k, dtype=float) * np.ones_like(np.asarray(log_x, dtype=float))
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        above = -np.logaddexp(-(k - 1) * log_x, np.log(np.abs(k - 1))
                              + log_amount - np.log(ceiling)) / (k - 1)
        if np.all(k > 1 + 1e-9):    # every draw on the k > 1 branch
            return above
        m = 1 - k
        left = np.exp(m * log_x) - m * np.exp(np.minimum(log_amount, 700)) / ceiling
        below = np.where(left > 0, np.log(np.maximum(left, 1e-300)) / m, -np.inf)
        unit = log_x - np.exp(np.minimum(log_amount, 700)) / ceiling
    return np.where(np.abs(k - 1) < 1e-9, unit, np.where(k > 1, above, below))


def reference_software(years, rate, compute_rate, parallel, initial_throughput, difficulty,
                       late_rate=None, at=np.inf, ceiling=np.inf):
    """Exact software progress with the same resources and frozen AI skills;
    inputs grow at `compute_rate`, then `late_rate` from `at`, under a
    software `ceiling` (natural log; inf for none)."""
    late = compute_rate if late_rate is None else late_rate
    effort = grown(years, parallel * np.asarray(compute_rate, dtype=float),
                   parallel * np.asarray(late, dtype=float), at)
    amount = rate * initial_throughput * effort
    if not np.all(difficulty > 0):
        return amount
    if np.all(np.isinf(ceiling)):
        return np.log1p(difficulty * amount) / difficulty
    with np.errstate(divide="ignore"):
        log_x = ceiling_step(np.zeros_like(np.asarray(amount, dtype=float)), np.log(amount),
                             difficulty * ceiling, ceiling)
    return -ceiling * np.expm1(log_x)


# ---------------------------------------------------------------------------
# Compiled step loop. `simulate`'s weekly loop, one draw at a time in scalar
# code (draws never interact, except through the lockstep-only `theft_jump` /
# `weight_theft`, which keep the numpy loop). The numpy loop below stays the
# reference: `test_the_compiled_loop_matches_the_numpy_loop` holds the two
# together, so a change to one is made in both.
# ---------------------------------------------------------------------------
try:
    import numba as _numba
except ImportError:          # the numpy loop runs instead
    _numba = None


def _jit(f):
    if _numba is None:
        return f
    return _numba.njit(cache=True, error_model="numpy")(f)


_LN2 = 0.6931471805599453
_W0, _W1, _W2 = (float(w) for w in WORKFLOW_WEIGHTS)


@_jit
def _k_lae(x, y):
    """np.logaddexp, scalar, by numpy's own branches."""
    if x == y:
        return x + _LN2
    tmp = x - y
    if tmp > 0:
        return x + np.log1p(np.exp(-tmp))
    if tmp <= 0:
        return y + np.log1p(np.exp(tmp))
    return tmp


@_jit
def _k_min(a, b):            # np.minimum: NaN propagates
    return a if (a < b or a != a) else b


@_jit
def _k_max(a, b):
    return a if (a > b or a != a) else b


@_jit
def _k_clip(x, lo, hi):
    return _k_min(_k_max(x, lo), hi)


@_jit
def _k_ss_right(xs, x):
    """np.searchsorted(xs, x, side="right")."""
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


@_jit
def _k_paths_at(row, years, u):
    """`_paths_at` for one row."""
    x = _k_clip(u, years[0], years[-1])
    j = min(max(_k_ss_right(years, x) - 1, 0), len(years) - 2)
    f = (x - years[j]) / (years[j + 1] - years[j])
    return row[j] * (1 - f) + row[j + 1] * f


@_jit
def _k_row_interp(row, years, back, u):
    """`_row_interp`'s `at` for one row."""
    if u < 0:
        return row[0] + back * u
    x = _k_clip(u, 0.0, years[-1]) / (years[1] - years[0])
    j = min(int(x), len(years) - 2)
    f = x - j
    return row[j] * (1 - f) + row[j + 1] * f


@_jit
def _k_interp(x, xp, fp, norm):
    """np.interp(x, xp, fp / norm)."""
    m = len(xp)
    if x != x:
        return x
    if x < xp[0]:
        return fp[0] / norm
    if x > xp[m - 1]:
        return fp[m - 1] / norm
    j = _k_ss_right(xp, x) - 1
    if j >= m - 1:
        return fp[m - 1] / norm
    if xp[j] == x:
        return fp[j] / norm
    lo, hi = fp[j] / norm, fp[j + 1] / norm
    return (hi - lo) / (xp[j + 1] - xp[j]) * (x - xp[j]) + lo


@_jit
def _k_follow(curve, row, two_d, years, at):
    """`workflow_state`'s `follow` for one draw's stage."""
    if not two_d:
        return _k_interp(at, years, curve[0], curve[0, 0])
    last = len(years) - 1
    pos = _k_clip(at / (years[1] - years[0]), 0.0, float(last))
    i0 = min(int(pos), last - 1)
    w = pos - i0
    return (curve[row, i0] * (1 - w) + curve[row, i0 + 1] * w) / curve[row, 0]


@_jit
def _k_ces_log(x, y, rho):
    if abs(rho) < 1e-9:
        return (x + y) / 2
    return (_k_lae(rho * x, rho * y) - _LN2) / rho


@_jit
def _k_judgment_log(effective, slope, drift, transfer, cap):
    """`ai_judgment_log` for one draw."""
    if not transfer:
        return 0.0
    k = np.log1p(drift) / np.log(10.0)
    if abs(k) < 1e-12:
        gain = slope * effective
    else:
        gain = slope * np.expm1(_k_min(k * effective, 700.0)) / k
    out = _k_lae(np.log1p(-transfer) if transfer < 1 else -np.inf, np.log(transfer) + gain)
    return _k_min(out, np.log(cap)) if cap else out


@_jit
def _k_ceiling_step(log_x, log_amount, k, ceiling):
    if abs(k - 1) < 1e-9:
        return log_x - np.exp(_k_min(log_amount, 700.0)) / ceiling
    if k > 1:
        return -_k_lae(-(k - 1) * log_x, np.log(abs(k - 1)) + log_amount
                       - np.log(ceiling)) / (k - 1)
    m = 1 - k
    left = np.exp(m * log_x) - m * np.exp(_k_min(log_amount, 700.0)) / ceiling
    return np.log(_k_max(left, 1e-300)) / m if left > 0 else -np.inf


@_jit
def _k_grown(t, early, late, at):
    head = _k_min(t, at)
    tail = _k_max(t - at, 0.0)
    a = np.expm1(early * head) / early if early != 0 else head
    b = np.expm1(late * tail) / late if late != 0 else tail
    return a + np.exp(early * head) * b


@_jit
def _k_hours(cap, rate, start, half, floor, use_pace, pace, s, a, i, out):
    """Forward `workflow_state` for one draw into `out` (3 stages)."""
    eq = _k_max(cap, 0.0) / rate
    for k in range(3):
        sy = eq * pace if (k == 0 and use_pace) else eq
        if s.has_curve:
            cv = a.cv0 if k == 0 else (a.cv1 if k == 1 else a.cv2)
            dec = _k_follow(cv, i if cv.shape[0] > 1 else 0, a.cv_2d[k], a.cyears,
                            sy * s.reference_half / half[k])
        else:
            dec = np.exp(-_LN2 * sy * 12 / half[k])
        out[k] = floor + (start[k] - floor) * dec


@_jit
def _k_draw(i, d, s, a, o):
    """One draw of `simulate`'s step loop; reads `d` (per draw), `s`
    (settings), `a` (paths); writes row i of `o`."""
    G = len(a.grid)
    big = 1e6
    start = d.starts[i]
    half = d.halves[i]
    today2 = d.today_hours[i, 2]
    sr, cr, cl = d.software_rate[i], d.compute_rate[i], d.compute_late[i]
    ff, init = d.fast_fraction[i], d.initial_stock[i]
    beta, ceil, rho = d.beta[i], d.ceiling[i], d.rho[i]
    capped = np.isfinite(ceil)
    par = s.parallel
    sh0, sh1, sh2 = s.sh0, s.sh1, s.sh2
    log_sh2, log_sh1 = np.log(sh2 / 0.2), np.log(sh1 / 0.4)
    h = np.empty(3)
    hb = np.empty(3)
    seen = np.full(G, np.inf)
    seen[0] = 0.0
    stock = np.zeros(G)
    stock[0] = init
    fol = s.follower

    def frontier(u):
        if s.has_cpath:
            v = _k_paths_at(a.cpath_logs[i], a.cpath_years, u)
        else:
            v = cr * _k_min(u, s.slow_at) + cl * _k_max(u - s.slow_at, 0.0)
        if s.has_cut:
            v -= _k_paths_at(a.cut_logs[i], a.cut_years, u)
        return v

    def uncut(u):
        if s.has_cpath:
            return _k_paths_at(a.cpath_logs[i], a.cpath_years, u)
        return cr * _k_min(u, s.slow_at) + cl * _k_max(u - s.slow_at, 0.0)

    def cut_at(u):
        return _k_paths_at(a.cut_logs[i], a.cut_years, u) if s.has_cut else 0.0

    def shift(logs, u):
        if not s.has_use_cut:
            return 0.0
        return cut_at(u) - _k_paths_at(logs[i], a.cut_years, u)

    def review(x):
        return (x >= s.review_from - 1e-12) and (x < s.review_to - 1e-12)

    def humans(cap, sw, t, has_t, rsi_t, out):
        rate = d.bcr[i]
        if fol:
            e = d.fol_eci_now[i] + s.fol_w0 * (cap - sw) + s.fol_w1 * sw
            tg = a.fol_grid
            nt = len(tg)
            pos = (e - s.fol_lo) / s.fol_step
            j = int(_k_clip(pos, 0.0, nt - 2.0))
            f = _k_clip(pos - j, 0.0, 1.0)
            if pos > nt - 1:
                cap = a.fol_table[i, nt - 1] + (e - tg[nt - 1]) * d.fol_slope[i]
            elif pos < 0:
                cap = a.fol_table[i, 0] + (e - tg[0]) * d.fol_slope[i]
            else:
                cap = a.fol_table[i, j] * (1 - f) + a.fol_table[i, j + 1] * f
            rate = d.fol_rate[i]
        use_pace = s.adoption != 0
        pace = 1.0
        if use_pace:
            pace = np.exp(_k_min(s.adoption * _k_judgment_log(
                cap, d.taste_slope[i], d.drift[i], s.transfer, s.judgment_cap), 30.0))
        _k_hours(cap, rate, start, half, s.floor, use_pace, pace, s, a, i, out)
        if fol:      # behind today's level, hours run back up
            eqb = cap / rate
            for k in range(3):
                sy = eqb * pace if (k == 0 and use_pace) else eqb
                behind = np.exp(-_LN2 * _k_min(sy, 0.0) * 12 / half[k])
                out[k] = _k_min(s.floor + (out[k] - s.floor) * behind, 1.0)
        if has_t and o.coding[i] > t + 1e-12:
            out[0] = _k_max(out[0], s.full_human)

    def pays_off(t, software, boost_log, scale_now, trained, fast, reference_trained):
        lag = d.scale_lag[i]
        target = scale_now - lag
        x = _k_min(target, big - 1)
        lo, hi = 0, G          # last index with seen (inf read as 1e6) <= x
        while lo < hi:
            mid = (lo + hi) // 2
            v = seen[mid] if np.isfinite(seen[mid]) else big
            if v <= x:
                lo = mid + 1
            else:
                hi = mid
        idx = lo - 1
        last = G - 1
        c0 = seen[max(idx, 0)]
        s0 = stock[max(idx, 0)]
        c1 = seen[min(idx + 1, last)]
        s1 = stock[min(idx + 1, last)]
        if (not np.isfinite(c1)) or idx >= last:
            c1 = frontier(t) + boost_log
            s1 = software
        ratio = d.scale_ratio[i]
        frac = _k_clip((target - c0) / (c1 - c0) if c1 > c0 else 0.0, 0.0, 1.0)
        earlier = s0 + frac * (s1 - s0) if idx >= 0 else init + ratio * target
        if np.isinf(ratio):
            due = np.inf
        else:
            due = _k_max((1 - ff) * (earlier + ratio * lag), reference_trained)
        return fast + trained - d.scale_share[i] * _k_max(trained - due, 0.0)

    def difficulty(progress):
        if capped:
            lx = np.log1p(-_k_min(progress / ceil, 1.0))
            return lx, -beta * ceil * lx
        return 0.0, beta * progress

    def advance(progress, plx, amount):
        if s.difficulty_on:
            if capped:
                return -ceil * np.expm1(_k_ceiling_step(plx, amount, beta * ceil, ceil))
            return _k_lae(beta * progress, np.log(beta) + amount) / beta
        return progress + np.exp(_k_min(amount, 100.0))

    # State, as the numpy loop's arrays hold it for this draw.
    software = init
    deployed = 0.0
    fast_next = s.fast_time
    fast_snapshot = init
    fast_deployed = 0.0
    reference_fast = 0.0
    last_validated = 0.0
    last_reference = 0.0
    snapshot = init
    run_compute = 0.0
    training_used = 0.0
    run_start = 0.0
    reference_gained = 0.0
    reference_at_run_start = 0.0
    reference_at_fast_start = 0.0
    run_len = d.train_time[i]
    eval_len = d.eval_time[i]
    pending = 0.0
    pending_software = 0.0
    deployed_software = 0.0
    last_deploy = 0.0
    delivered_rate = 0.0
    reference_delivered = 0.0
    reference_deployed = 0.0
    reference_pending_software = 0.0
    reference_pending_capability = 0.0
    advantage = 0.0
    finished = False
    last_labor = 1.0
    last_experiments = 1.0
    run_start_scale = 0.0
    pending_scale = 0.0
    deployed_scale = 0.0
    obs = 1
    last_pace = d.initial_throughput[i]
    last_reference_pace = d.initial_throughput[i]
    lf0, lf1, lf2 = o.factor[0, i, 0], o.factor[1, i, 0], o.factor[2, i, 0]
    lf3, lf4, lf5 = o.factor[3, i, 0], o.factor[4, i, 0], o.factor[5, i, 0]
    t = 0.0
    stopped_at = np.inf
    boost_log = 0.0
    follow_log = 0.0
    fe0 = fe1 = fe2 = fe3 = 0.0
    held0 = held1 = held2 = held3 = 0.0
    coding_recorded = o.coding[i] <= 0
    rsi = o.rsi[i]
    tr = s.transfer
    # The deployed model (`realized`).
    now0 = deployed - deployed_software
    now1 = pays_off(t, software, boost_log, deployed_scale, deployed_software, fast_deployed,
                    reference_delivered)
    now2 = now0 + now1
    years = s.years
    carried = False
    while t < years - 1e-12:
        coding = o.coding[i]
        train_end = run_start + run_len
        deploy_end = train_end + eval_len
        ne = _k_min(deploy_end if finished else train_end, fast_next)
        ne = _k_min(ne, coding if coding > t + 1e-12 else np.inf)
        next_obs = a.grid[min(obs, G - 1)]
        ne = _k_min(ne, next_obs)
        end = _k_min(_k_min(t + s.step, ne), years)
        dt = _k_max(end - t, 0.0)
        mid = t + dt / 2
        base = frontier(mid)
        since = mid - rsi - s.rsi_delay
        boosting = np.isfinite(rsi) and t >= rsi - 1e-12
        in_force = 0.0
        if boosting:
            if s.rsi_ramp > 0:
                in_force = _k_clip(since / s.rsi_ramp, 0.0, 1.0)
            else:
                in_force = 1.0 if since >= 0 else 0.0
        if s.has_cpath:
            growth = _k_max(uncut(end) - uncut(t), 0.0)
        else:
            growth = (cr if mid < s.slow_at else cl) * dt
        boost_step = s.boost * in_force * growth if boosting else 0.0
        compute_log = base + boost_log + boost_step / 2
        uncut_base = base + cut_at(mid)
        if s.own_experiments:
            if s.has_epath:
                level = _k_paths_at(a.epath_logs[i], a.epath_years, mid)
            else:
                level = (d.exp_rate[i] * _k_min(mid, s.slow_at)
                         + d.exp_late[i] * _k_max(mid - s.slow_at, 0.0))
            exp_log = (d.exp_share[i] * level - uncut_base if d.has_history[i]
                       else d.exp_growth[i] * mid)
        else:
            exp_log = ((d.exp_share[i] - 1) * uncut_base if d.has_history[i]
                       else d.exp_growth[i] * mid)
        staff_rsi = rsi if tr else np.inf
        head_log = (s.hire_rate * _k_min(mid, staff_rsi)
                    + s.after_rate * _k_max(mid - staff_rsi, 0.0))
        effective = now2 + follow_log
        if carried:          # the last step's closing hours, read at this same point
            h[0], h[1], h[2] = hb[0], hb[1], hb[2]
        else:
            humans(effective, now1 + follow_log, t, True, rsi, h)
        if s.autopilot and np.isfinite(rsi) and t >= rsi - 1e-12 and not review(t):
            h[0] = 0.0
            h[1] = 0.0
            h[2] = 0.0
        share_now = h[0] * _W0 + h[1] * _W1 + h[2] * _W2
        log_speed = np.log(s.ai_speed) + s.ai_copies * _k_max(now1 + follow_log, 0.0)
        amdahl_log = d.amdahl0[i] - _k_lae(np.log(share_now), np.log1p(-share_now) - log_speed)
        staff_share = share_now if tr else d.human0[i]
        staff_speed = log_speed if tr else np.log(s.ai_speed)
        headcount_log = (_k_lae(np.log(staff_share), np.log1p(-staff_share) - staff_speed)
                         - _k_lae(np.log(staff_share) - head_log,
                                  np.log1p(-staff_share) - staff_speed))
        direction = h[0]
        cf = _k_clip(mid / coding if coding > 0 else 1.0, 0.0, 1.0)
        if coding <= 0:
            cf = 0.0
        if fol:
            level_now = (effective if not s.has_coding_weights else
                         s.cw0 * now0 + s.cw1 * (now1 + follow_log))
            cl_i = d.coding_level[i]
            cf = 1.0 if coding <= t + 1e-12 else _k_clip(
                level_now / cl_i if cl_i > 0 else 1.0, 0.0, 1.0)
        rsi_coding_log = np.log((1 - s.coding_today / 100) / .05) * cf
        coding_gain = _k_max(rsi_coding_log, s.coding_slope * effective)
        if tr:
            keep_log = np.log1p(-tr) if tr < 1 else -np.inf
            coding_log = _k_lae(keep_log, np.log(tr) + coding_gain)
            ai_taste_log = np.log(s.judgment_today) + _k_judgment_log(
                effective, d.taste_slope[i], d.drift[i], tr, s.judgment_cap)
            quality_log = (_k_lae(np.log(direction), np.log1p(-direction) + ai_taste_log)
                           - d.quality0_log[i])
            automation_log = _k_lae(keep_log, np.log(tr) + amdahl_log)
        else:
            coding_log = quality_log = automation_log = 0.0
        labor_log = par * (compute_log + log_sh2 + coding_log + automation_log + headcount_log)
        experiment_log = par * (compute_log + exp_log + log_sh1)
        ref_headcount = (d.amdahl0[i] - _k_lae(np.log(d.human0[i]) - s.hire_rate * mid,
                                               np.log1p(-d.human0[i]) - np.log(s.ai_speed)))
        agent_shift = shift(a.agents_logs, mid)
        exp_shift = shift(a.experiments_logs, mid)
        agent_share = sh2
        if s.reallocate:
            gap = (labor_log - experiment_log) - par * (
                log_sh2 + ref_headcount - exp_log - log_sh1)
            log_ratio = np.log(sh2 / sh1) + rho / (1 - par * rho) * gap
            pool = sh1 + sh2
            agent_share = pool / (1 + np.exp(-_k_clip(log_ratio, -700.0, 700.0)))
            agent_share = _k_clip(agent_share, 1e-9 * pool, pool * (1 - 1e-9))
            labor_log = labor_log + par * np.log(agent_share / sh2)
            experiment_log = experiment_log + par * np.log((pool - agent_share) / sh1)
        labor_log = labor_log + par * agent_shift
        experiment_log = experiment_log + par * exp_shift
        research_log = _k_ces_log(labor_log, experiment_log, rho) + quality_log
        judgment_log = quality_log
        exp_in = par * (compute_log + exp_shift + exp_log + log_sh1)
        agent_in = par * (compute_log + agent_shift + log_sh2)
        bare = _k_ces_log(agent_in, exp_in, rho)
        compute_part = bare
        labor_part = _k_ces_log(agent_in + par * headcount_log, exp_in, rho) - bare
        if s.has_slopes:
            it = d.initial_throughput[i]
            resource_log = (np.log(it) + par * d.input_rate[i] * mid
                            - par * (cut_at(mid) - (agent_shift + exp_shift) / 2))
            residual = (d.exp_slope[i] - par * cr) * mid
            proxy_log = resource_log + s.useful / 100 * residual
            weight = s.trend_weight / 100 * np.exp(-_LN2 * mid * 12 / s.trend_months)
            research_log = (1 - weight) * research_log + weight * proxy_log
            judgment_log = (1 - weight) * quality_log
            compute_part = ((1 - weight) * compute_part + weight * (
                np.log(it) + par * mid * (
                    (cr + d.exp_share[i] * d.exp_rate[i]) / 2 if d.has_history[i]
                    else cr + d.exp_growth[i] / 2)))
            labor_part = (1 - weight) * labor_part + weight * par * d.hire_effect[i] / 2 * mid
        gained = software - init
        log_x, penalty = difficulty(gained)
        ref_log_x, ref_penalty = difficulty(reference_gained)
        ref_research = _k_ces_log(
            par * (base + agent_shift + log_sh2 + ref_headcount),
            par * (base + exp_shift + exp_log + log_sh1), rho)
        reference_pace = np.exp(_k_min(ref_research - ref_penalty, 700.0))
        log_dt = np.log(dt) if dt > 0 else -np.inf
        ref_log_amount = np.log(sr) + ref_research + log_dt
        log_amount = np.log(sr) + research_log + log_dt
        pace = np.exp(_k_min(research_log - penalty, 700.0))
        updated = init + advance(gained, log_x, log_amount)
        if fol:
            standing = d.fol_eci_now[i] + s.fol_w0 * now0 + s.fol_w1 * (
                updated - init + follow_log)
            fy = a.fol_years
            gap_f = _k_max(_k_row_interp(a.fol_teacher[i], fy, s.fol_ppy, mid) - standing, 0.0)
            ts = (1.0 if not s.has_theft_scale or mid < 0
                  else _k_row_interp(a.fol_theft_scale[i], fy, 0.0, mid))
            stolen = _k_min(s.fol_theft * ts, 1.0)
            ds = (1.0 if not s.has_distill_scale or mid < 0
                  else _k_row_interp(a.fol_distill_scale[i], fy, 0.0, mid))
            f_dist = d.fol_distill[i] * ds * gap_f * dt
            total = 0.0
            for q in range(LEAK_POINTS):
                lag = s.fol_absorb * (q + 0.5) / LEAK_POINTS
                u = mid - lag
                ls = (1.0 if not s.has_leak_scale or u < 0
                      else _k_row_interp(a.fol_leak_scale[i], fy, 0.0, u))
                total = total + ls * _k_max(
                    _k_row_interp(a.fol_software[i], fy, s.fol_software_ppy, end - lag)
                    - _k_row_interp(a.fol_software[i], fy, s.fol_software_ppy, t - lag), 0.0)
            f_leak = d.fol_leak[i] * (1 - stolen) * total / LEAK_POINTS
            f_theft = stolen * _k_max(
                _k_row_interp(a.fol_software[i], fy, s.fol_software_ppy, end)
                - _k_row_interp(a.fol_software[i], fy, s.fol_software_ppy, t), 0.0)
            f_dist = _k_min(f_dist, gap_f)
            if s.has_trained:
                room = _k_max(_k_row_interp(a.fol_trained[i], fy, s.fol_ppy, mid)
                              - standing, 0.0) - f_dist
            else:
                room = gap_f - f_dist
            ideas = f_leak + f_theft
            keep = _k_min(ideas, _k_max(room, 0.0)) / ideas if ideas > 0 else 0.0
            f_leak, f_theft = f_leak * keep, f_theft * keep
            fe0 += f_dist
            fe1 += f_leak
            fe2 += f_theft
            follow_log = follow_log + (0.0 + f_dist + f_leak + f_theft + 0.0) / s.fol_w1
        reference_gained = advance(reference_gained, ref_log_x, ref_log_amount)
        diverged = updated > big
        if diverged and not np.isfinite(rsi) and s.rsi_possible:
            rsi = end
        software = _k_min(updated, big)
        if s.has_cpath:
            budget = np.exp(uncut_base) * dt
        else:
            budget = (_k_grown(t + dt, cr, cl, s.slow_at) - _k_grown(t, cr, cl, s.slow_at))
        budget = budget * np.exp(boost_log + boost_step / 2 - cut_at(mid))
        boost_log = boost_log + boost_step
        used = 0.0 if finished else sh0 * budget
        run_compute += used
        training_used += used
        done = (not finished) and end >= train_end - 1e-12
        if s.serial_speedup and done:
            hv = h[2]
            eval_len = (d.eval_time[i] * (hv + (1 - hv) / s.ai_speed)
                        / (today2 + (1 - today2) / s.ai_speed))
        if done and review(end):
            eval_len = _k_max(eval_len, s.review_time)
        candidate_compute = np.log(_k_max(run_compute / s.reference_train_compute, 1e-12))
        candidate = (1 - ff) * snapshot + candidate_compute
        reference_snapshot = init + reference_at_run_start
        if done:
            adopted = candidate_compute + pays_off(
                t, software, boost_log, run_start_scale, (1 - ff) * snapshot, fast_deployed,
                (1 - ff) * reference_snapshot) > now2
            if adopted:
                pending, pending_scale = candidate, run_start_scale
                pending_software = (1 - ff) * snapshot
            else:
                pending, pending_scale = deployed, deployed_scale
                pending_software = deployed_software
            reference_candidate = (1 - ff) * reference_snapshot + np.log(
                _k_max(run_compute / s.reference_train_compute, 1e-12))
            reference_pending_capability = _k_max(reference_deployed, reference_candidate)
            reference_pending_software = ((1 - ff) * reference_snapshot
                                          if reference_candidate > reference_deployed
                                          else reference_delivered)
            finished = True
        ready = finished and end >= deploy_end - 1e-12
        if ready:
            behind = (pending - pending_software) + pays_off(
                t, software, boost_log, pending_scale, pending_software, fast_deployed,
                reference_pending_software) < now2 - 1e-12
            if behind:
                pending, pending_software = deployed, deployed_software
                pending_scale = deployed_scale
            deployed, deployed_scale = pending, pending_scale
        fast_ready = end >= fast_next - 1e-12
        if fast_ready:
            fast_deployed = ff * fast_snapshot
            reference_fast = ff * (init + reference_at_fast_start)
            reference_at_fast_start = reference_gained
            fast_snapshot = software
            fast_next += _k_max(s.fast_time, s.review_time) if review(end) else s.fast_time
        validated = (pending_software if ready else deployed_software) + fast_deployed
        reference_validated = ((reference_pending_software if ready else reference_delivered)
                               + reference_fast)
        if ready:
            span = (end - last_deploy) * sr
            delivered_rate = _k_max(validated - last_validated, 0.0) / span
            reference_rate = _k_max(reference_validated - last_reference, 0.0) / span
            advantage = delivered_rate / reference_rate if reference_rate > 0 else 0.0
            last_validated, last_reference = validated, reference_validated
            reference_delivered = reference_pending_software
            reference_deployed = reference_pending_capability
            deployed_software = pending_software
            last_deploy = end
        if ready or fast_ready:
            now0 = deployed - deployed_software
            now1 = pays_off(t, software, boost_log, deployed_scale, deployed_software,
                            fast_deployed, reference_delivered)
            now2 = now0 + now1
        software_now = now1 + follow_log
        effective = now2 + follow_log
        if s.has_coding_capability:
            level = s.cw0 * now0 + s.cw1 * software_now if s.has_coding_weights else effective
            if level >= d.coding_level[i] and o.coding[i] > end:
                o.coding[i] = end
        if ready or fast_ready:
            held0, held1, held2, held3 = effective, software_now, validated, reference_validated
        humans(effective, software_now, end, True, rsi, hb)
        carried = True
        coding = o.coding[i]
        for rec in range(2):
            hit = (end >= coding and not coding_recorded) if rec == 0 else (
                (not diverged) and end >= coding and hb[0] <= s.full_human
                and not np.isfinite(rsi))
            if hit:
                if rec == 0:
                    coding_recorded = True
                else:
                    rsi = end
                dest = o.out_coding if rec == 0 else o.out_rsi
                dest[0, i] = hb[0] * _W0 + hb[1] * _W1 + hb[2] * _W2
                dest[1, i] = _k_max(_k_max(hb[0], hb[1]), hb[2])
                dest[2, i], dest[3, i], dest[4, i] = hb[0], hb[1], hb[2]
                dest[5, i], dest[6, i] = delivered_rate, advantage
        if rsi >= end:
            last_labor, last_experiments = labor_log, experiment_log
        if ready:
            snapshot = software
            run_start = end
            reference_at_run_start = reference_gained
            if s.serial_speedup:
                growth_now = sr * pace + (cr if end < s.slow_at else cl)
                run_len = d.train_time[i] * _k_min(1.0, d.bcr[i] / _k_max(growth_now, 1e-9))
            run_start_scale = frontier(end) + boost_log
            run_compute = 0.0
            finished = False
        if end >= next_obs - 1e-12 and obs < G:
            j = obs
            o.pace[i, j] = pace
            o.agent_share[i, j] = agent_share
            seen[j] = _k_max(frontier(end) + boost_log, seen[max(j - 1, 0)])
            stock[j] = software
            o.capability[i, j], o.realized[i, j] = held0, held1
            o.validated[i, j], o.reference[i, j] = held2, held3
            if fol:
                o.follow[0, i, j], o.follow[1, i, j] = fe0, fe1
                o.follow[2, i, j], o.follow[3, i, j] = fe2, fe3
            o.boost[i, j] = boost_log
            resources = research_log - judgment_log
            o.factor[0, i, j], o.factor[1, i, j] = judgment_log, resources
            o.factor[2, i, j], o.factor[3, i, j] = penalty, compute_part
            o.factor[4, i, j] = labor_part
            o.factor[5, i, j] = resources - compute_part - labor_part
            o.reference_pace[i, j] = reference_pace
            obs += 1
        resources = research_log - judgment_log
        lf0, lf1, lf2, lf3, lf4 = judgment_log, resources, penalty, compute_part, labor_part
        lf5 = resources - compute_part - labor_part
        last_pace, last_reference_pace = pace, reference_pace
        if diverged:
            stopped_at = end
            t = years
        else:
            t = end
    o.rsi[i] = rsi
    o.software[i], o.deployed[i] = software, deployed
    o.deployed_software[i], o.fast_deployed[i] = deployed_software, fast_deployed
    o.training_used[i] = training_used
    o.delivered_rate[i], o.advantage[i] = delivered_rate, advantage
    o.stopped_at[i] = stopped_at
    o.last_labor[i], o.last_experiments[i] = last_labor, last_experiments
    o.last_pace[i], o.last_reference_pace[i] = last_pace, last_reference_pace
    o.last_factors[0, i], o.last_factors[1, i], o.last_factors[2, i] = lf0, lf1, lf2
    o.last_factors[3, i], o.last_factors[4, i], o.last_factors[5, i] = lf3, lf4, lf5
    o.boost_log[i] = boost_log
    o.obs[i] = obs
    o.held[0, i], o.held[1, i], o.held[2, i], o.held[3, i] = held0, held1, held2, held3


def _k_run_py(d, s, a, o):
    for i in _prange(len(d.software_rate)):    # draws are independent
        _k_draw(np.int64(i), d, s, a, o)    # prange's index is unsigned


_prange = _numba.prange if _numba is not None else range
_k_run = (_numba.njit(cache=True, error_model="numpy", parallel=True)(_k_run_py)
          if _numba is not None else _k_run_py)


# False runs the numpy loop everywhere (the parity test flips it).
COMPILED = True


def _cpu_quota():
    """Cores this process may use: the cgroup CPU quota where one is set
    (a container sees the host's cores but is throttled to its quota), else
    its CPU affinity."""
    import os
    cores = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    for path, split in (("/sys/fs/cgroup/cpu.max", None),
                        ("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "/sys/fs/cgroup/cpu/cpu.cfs_period_us")):
        try:
            if split is None:
                quota, period = open(path).read().split()[:2]
            else:
                quota, period = open(path).read().strip(), open(split).read().strip()
            if quota not in ("max", "-1"):
                cores = min(cores, max(1, int(int(quota) / int(period))))
            break
        except (OSError, ValueError):
            continue
    return max(1, cores or 1)


_K_THREADS = (min(_cpu_quota(), _numba.config.NUMBA_NUM_THREADS)
              if _numba is not None else 1)
_K_FACTORS = ("judgment", "resources", "difficulty", "compute", "labor", "ai")
_K_OUTCOMES = ("human_mean", "human_worst", "human_direction", "human_experiments",
               "human_verification", "progress_multiple", "compute_matched_advantage")
_KDraws = namedtuple("_KDraws", (
    "starts", "halves", "today_hours", "software_rate", "compute_rate", "compute_late",
    "exp_rate", "exp_late", "exp_share", "exp_growth", "has_history", "initial_throughput",
    "initial_stock", "train_time", "eval_time", "scale_ratio", "amdahl0", "quality0_log",
    "human0", "hire_effect", "input_rate", "exp_slope", "coding_level", "taste_slope", "drift",
    "rho", "beta", "ceiling", "scale_share", "scale_lag", "fast_fraction", "bcr", "fol_rate",
    "fol_eci_now", "fol_slope", "fol_distill", "fol_leak"))
_KSettings = namedtuple("_KSettings", (
    "years", "step", "boost", "rsi_delay", "rsi_ramp", "slow_at", "transfer", "parallel",
    "sh0", "sh1", "sh2", "ai_speed", "ai_copies", "hire_rate", "after_rate",
    "judgment_today", "judgment_cap", "adoption", "coding_today", "coding_slope",
    "reallocate", "has_slopes", "trend_weight", "trend_months", "useful", "full_human",
    "autopilot", "serial_speedup", "fast_time", "review_from", "review_to", "review_time",
    "difficulty_on", "reference_train_compute", "own_experiments", "floor",
    "reference_half", "has_curve", "has_coding_capability", "has_coding_weights", "cw0",
    "cw1", "rsi_possible", "has_cpath", "has_epath", "has_cut", "has_use_cut", "follower",
    "fol_w0", "fol_w1", "fol_theft", "fol_absorb", "fol_ppy", "fol_software_ppy",
    "has_trained", "fol_lo", "fol_step", "has_distill_scale", "has_leak_scale",
    "has_theft_scale"))
_KPaths = namedtuple("_KPaths", (
    "grid", "cyears", "cv0", "cv1", "cv2", "cv_2d", "cpath_years", "cpath_logs", "epath_years",
    "epath_logs", "cut_years", "cut_logs", "agents_logs", "experiments_logs", "fol_years",
    "fol_grid", "fol_table", "fol_teacher", "fol_software", "fol_trained",
    "fol_distill_scale", "fol_leak_scale", "fol_theft_scale"))
_KOut = namedtuple("_KOut", (
    "coding", "rsi", "capability", "realized", "validated", "reference", "pace",
    "reference_pace", "agent_share", "boost", "factor", "follow", "out_coding", "out_rsi",
    "software", "deployed", "deployed_software", "fast_deployed", "training_used",
    "delivered_rate", "advantage", "stopped_at", "last_labor", "last_experiments",
    "last_pace", "last_reference_pace", "last_factors", "boost_log", "obs", "held"))


def _k_simulate(n, p, step, fol, cpath, epath, cut, use_cut, human_curve, coding, rsi,
                outcomes, histories, pace_history, reference_pace_history,
                agent_share_history, boost_history, factor_history, follow_history,
                experiment_slopes, coding_capability, coding_weights, review, v):
    """Run `simulate`'s step loop compiled. Arrays it is handed (coding,
    rsi, the histories) are filled in place; the rest comes back in `_KOut`."""
    # One array type per argument (C order, writable), so one compiled
    # specialization serves every call.
    f64 = lambda x: np.require(x, dtype=float, requirements=["C", "W"])
    per = lambda x: f64(np.broadcast_to(np.asarray(x, dtype=float), (n,)).copy())
    dummy_years, dummy_logs = np.array([0.0, 1.0]), np.zeros((1, 2))

    def path(pair):
        return (dummy_years, dummy_logs) if pair is None else (f64(pair[0]), f64(pair[1]))
    raw = fol["raw"] if fol is not None else None
    d = _KDraws(
        starts=f64(v["starts"]), halves=f64(v["halves"]), today_hours=f64(v["today_hours"]),
        **{k: per(v[k]) for k in (
            "software_rate", "compute_rate", "compute_late", "exp_rate", "exp_late",
            "exp_share", "exp_growth", "initial_throughput", "initial_stock", "train_time",
            "eval_time", "scale_ratio", "amdahl0", "quality0_log", "human0", "hire_effect",
            "input_rate", "taste_slope", "drift", "rho", "beta", "ceiling", "scale_share",
            "scale_lag", "fast_fraction", "bcr")},
        has_history=per(np.asarray(v["has_history"], dtype=float)),
        exp_slope=np.zeros(n) if experiment_slopes is None else per(experiment_slopes),
        coding_level=(np.full(n, np.inf) if coding_capability is None
                      else per(coding_capability)),
        fol_rate=np.zeros(n) if raw is None else per(fol["rate"]),
        fol_eci_now=np.zeros(n) if raw is None else per(fol["eci_now"]),
        fol_slope=np.zeros(n) if raw is None else per(raw["slope"]),
        fol_distill=np.zeros(n) if raw is None else per(fol["distill"]),
        fol_leak=np.zeros(n) if raw is None else per(fol["leak"]))
    shares = v["shares"]
    s = _KSettings(
        years=float(p["years"]), step=float(step), boost=float(v["boost"]),
        rsi_delay=float(p["rsi_compute_delay"]) / 12, rsi_ramp=float(p["rsi_compute_ramp"]) / 12,
        slow_at=float(v["slow_at"]), transfer=float(v["transfer"]),
        parallel=float(v["parallel"]), sh0=float(shares[0]), sh1=float(shares[1]),
        sh2=float(shares[2]), ai_speed=float(v["ai_speed"]), ai_copies=float(p["ai_copies"]),
        hire_rate=float(v["hire_rate"]), after_rate=float(v["after_rate"]),
        judgment_today=float(p["judgment_today"]), judgment_cap=float(p["judgment_cap"]),
        adoption=float(p["direction_adoption"]), coding_today=float(p["coding_today"]),
        coding_slope=float(p["coding_slope"]), reallocate=bool(p["reallocate_compute"]),
        has_slopes=bool(experiment_slopes is not None and v["transfer"]),
        trend_weight=float(p["rsi_trend_weight"]), trend_months=float(p["rsi_trend_months"]),
        useful=float(p["rsi_useful_growth"]), full_human=float(p["full_human"]) / 100,
        autopilot=bool(p["rsi_autopilot"]), serial_speedup=bool(p["serial_speedup"]),
        fast_time=float(v["fast_time"]), review_from=float(review[0]),
        review_to=float(review[1]), review_time=float(review[2]),
        difficulty_on=bool(p["difficulty"] > 0),
        reference_train_compute=float(v["reference_train_compute"]),
        own_experiments=bool(v["own_experiments"]), floor=float(v["floor"]),
        reference_half=float(v["reference_half"]), has_curve=human_curve is not None,
        has_coding_capability=coding_capability is not None,
        has_coding_weights=coding_weights is not None,
        cw0=float(coding_weights[0]) if coding_weights is not None else 1.0,
        cw1=float(coding_weights[1]) if coding_weights is not None else 1.0,
        rsi_possible=bool(v["floor"] <= p["full_human"] / 100),
        has_cpath=cpath is not None, has_epath=epath is not None, has_cut=cut is not None,
        has_use_cut=use_cut is not None, follower=fol is not None,
        fol_w0=float(fol["w"][0]) if raw else 1.0, fol_w1=float(fol["w"][1]) if raw else 1.0,
        fol_theft=float(fol["theft"]) if raw else 0.0,
        fol_absorb=float(fol["absorb"]) if raw else 0.0,
        fol_ppy=float(raw["ppy"]) if raw else 0.0,
        fol_software_ppy=float(raw["software_ppy"]) if raw else 0.0,
        has_trained=bool(raw and raw["trained"] is not None),
        fol_lo=float(raw["lo"]) if raw else 0.0, fol_step=float(raw["step"]) if raw else 1.0,
        has_distill_scale=bool(raw and raw["distill_scale"] is not None),
        has_leak_scale=bool(raw and raw["leak_scale"] is not None),
        has_theft_scale=bool(raw and raw["theft_scale"] is not None))
    if human_curve is not None:
        own = list(human_curve[2:])
        stage = [own[k] if k < len(own) else human_curve[1] for k in range(3)]
        cv = tuple(f64(np.atleast_2d(c)) for c in stage)
        cv_2d = np.array([np.ndim(c) == 2 for c in stage])
        cyears = f64(human_curve[0])
    else:
        cv, cv_2d, cyears = (dummy_logs,) * 3, np.zeros(3, dtype=bool), dummy_years
    cpy, cpl = path(cpath)
    epy, epl = path(epath)
    cuty, cutl = path(cut)
    ag = f64(use_cut["agents"][1]) if use_cut is not None else dummy_logs
    ex = f64(use_cut["experiments"][1]) if use_cut is not None else dummy_logs

    def fpath(key):
        return dummy_logs if raw is None or raw[key] is None else f64(raw[key])
    a = _KPaths(
        grid=f64(v["grid"]),
        cyears=cyears, cv0=cv[0], cv1=cv[1], cv2=cv[2], cv_2d=cv_2d, cpath_years=cpy, cpath_logs=cpl,
        epath_years=epy, epath_logs=epl, cut_years=cuty, cut_logs=cutl, agents_logs=ag,
        experiments_logs=ex,
        fol_years=dummy_years if raw is None else f64(raw["years"]),
        fol_grid=dummy_years if raw is None else f64(raw["grid"]),
        fol_table=fpath("table"), fol_teacher=fpath("teacher"),
        fol_software=fpath("software"), fol_trained=fpath("trained"),
        fol_distill_scale=fpath("distill_scale"), fol_leak_scale=fpath("leak_scale"),
        fol_theft_scale=fpath("theft_scale"))
    factor = np.stack([factor_history[k] for k in _K_FACTORS])
    follow = (np.stack([follow_history[k] for k in FOLLOW_CHANNELS]) if follow_history
              else np.zeros((4, 1, 1)))
    o = _KOut(
        coding=coding, rsi=rsi, capability=histories[0], realized=histories[1],
        validated=histories[2], reference=histories[3], pace=pace_history,
        reference_pace=reference_pace_history, agent_share=agent_share_history,
        boost=boost_history, factor=factor, follow=follow,
        out_coding=np.stack([outcomes["Full coding automation"][k] for k in _K_OUTCOMES]),
        out_rsi=np.stack([outcomes["RSI"][k] for k in _K_OUTCOMES]),
        software=np.zeros(n), deployed=np.zeros(n), deployed_software=np.zeros(n),
        fast_deployed=np.zeros(n), training_used=np.zeros(n), delivered_rate=np.zeros(n),
        advantage=np.zeros(n), stopped_at=np.zeros(n), last_labor=np.zeros(n),
        last_experiments=np.zeros(n), last_pace=np.zeros(n),
        last_reference_pace=np.zeros(n), last_factors=np.zeros((6, n)),
        boost_log=np.zeros(n), obs=np.zeros(n, dtype=np.int64), held=np.zeros((4, n)))
    for arr in (o.coding, o.rsi) + tuple(histories) + (pace_history, reference_pace_history,
                                                      agent_share_history, boost_history):
        assert arr.flags.c_contiguous and arr.dtype == float
    _numba.set_num_threads(_K_THREADS)
    _k_run(d, s, a, o)
    for k, key in enumerate(_K_FACTORS):
        factor_history[key][:] = factor[k]
    for k, key in enumerate(FOLLOW_CHANNELS if follow_history else ()):
        follow_history[key][:] = follow[k]
    for name, block in (("Full coding automation", o.out_coding), ("RSI", o.out_rsi)):
        for k, key in enumerate(_K_OUTCOMES):
            outcomes[name][key][:] = block[k]
    return o


def simulate(params=None, n=1000, step=1 / 52, onset_years=None, experiment_slopes=None,
             compute_rates=None, historical_compute_rate=None, coding_capability=None,
             coding_weights=None, human_curve=None, software_scale=None,
             experiment_rates=None, historical_experiment_rate=None, follower=None,
             compute_path=None, experiment_path=None, draw_rows=None, compute_cut=None,
             review=None):
    """Weekly research and successor cycles, with censored milestone draws.

    RSI is the first time research direction is at or under `full_human`% of
    baseline human hours with the coding date arrived. Every draw runs to the
    horizon (only a numerically divergent one stops), so its capability path
    (`capability_log`) covers the whole window. `compute_rates`, one log
    growth rate a year per draw, replaces `compute_growth` and its spread;
    `historical_compute_rate` is the compute growth behind today's steady pace
    (default: each draw's own rate). `human_curve` = (years ahead, human
    share), the shape research hours follow (see `workflow_state`); without
    it they decline exponentially. `coding_weights` (w_compute, w_software)
    measures capability as w_compute x its training-compute part plus
    w_software x its algorithmic part (both natural logs vs today's model)
    for that test, so the level can be an ECI gain; default 1 and 1, log
    effective compute. `coding_capability`, a capability level
    (log effective compute), counts coding as automated once a deployed model
    reaches it, ahead of the inherited date; the result's `coding_at`
    (`coding_capability` may be one level per draw).

    `software_scale`, one multiple per draw, scales today's software rate
    (a country whose own research runs slower). `experiment_rates`, one log
    growth rate a year per draw, is the growth of the compute experiments can
    use when it differs from the frontier run's (`compute_rates`), against
    `historical_experiment_rate` behind today's pace: experiment compute keeps
    its fitted steady-state share of that growth. Both default to the
    frontier's, which leaves the model as it was. `compute_path` and
    `experiment_path`, each (years, logs per draw x years), replace those
    constant rates with paths (log compute against today's), as when policy
    bends a country's compute; `compute_rates` / `experiment_rates` then only
    set the history-free parts (the serial speed-up's clock, the reported
    rates). Neither slows from `compute_slow_years`: a path carries its own.
    The post-RSI `rsi_compute_boost` multiplies a compute path's own rise,
    so a flat or falling path gets no boost.

    `compute_cut`, (years, logs: one row, or one per draw), is a log cut (0 =
    none) in the compute this run's R&D gets, off whatever frontier the rates
    or `compute_path` give: training, agents and experiments each lose it
    whole, as does the trend proxy's resource growth, and a cut that ends is
    not a rise the RSI boost multiplies. With logs a dict keyed by
    `COMPUTE_USES`, each use takes its own cut and a negative one is compute
    moved to that use: a model's scale is its training compute, the trend
    proxy takes the mean of the agents' and experiments' cuts, and the cuts
    bind after the labs' own agent/experiment re-split.

    `review`, (start, months) or (start, months, end), is a ban on runaway
    self-improvement from `start` (years) until `end` (for good without
    one): no autopilot, and every capability gain waits for at least
    `months` of human review before research builds on it, a successor
    model's validation and each fast cycle alike.

    `follower` runs a country behind the frontier (see `FOLLOWER_KEYS`): its
    human hours are those of the leader's scenario at the same ECI (run back
    at each stage's halving below today's), and besides its own research it
    gains capability by distilling the leader's released models (a share of
    the ECI gap a year) and by the leader's algorithmic progress leaking (a
    share, each idea arriving spread over the next `absorb` years) or being
    stolen (a share, at once). That
    inflow is its own additive stock: it counts toward capability, AI help and
    hours at once, never into the research stock, so it neither raises
    difficulty nor waits on scale. Distillation never carries the follower
    past the leader's released frontier, leaked and stolen ideas past its
    trained one (`trained`, else the released). The result's `follow_eci` keeps each
    channel's cumulative ECI per month.

    `draw_rows` = (draws in the full run, rows kept): every random draw is
    made for the full run and only these rows simulated (`n` of them), so
    each matches the same row of the full run with the same seed, as a
    follower run on a subset of its leader's scenarios needs.

    A run freezes its algorithm snapshot at its start, integrates allocated
    training compute during the run, then waits for validation before deployment.
    Improvements discovered during either phase enter the next run. A fixed
    effective-compute reference prevents longer runs making the target easier.

    40/40/20 compute shares normalize training/experiments/agents to one today.
    The software doubling input is the initial rate under this reference split.
    Transfer discounts *additional* coding/judgment beyond today, so observed
    assistance is not multiplied into the starting rate a second time.
    """
    p = validate(params or {})
    if n < 1 or not 0 < step <= 0.25:
        raise ValueError("Use at least one draw and a time step in (0, 0.25] years.")
    rng = np.random.default_rng(int(p["seed"]))
    if experiment_slopes is not None:
        experiment_slopes = np.asarray(experiment_slopes, dtype=float)
        if experiment_slopes.shape != (n,) or not np.isfinite(experiment_slopes).all():
            raise ValueError("Provide one finite log experiment-growth rate per year per draw.")
    # Common quantiles preserve paired scenario comparisons. Lognormal
    # variation: `uncertainty`/100 is the 1-sigma of each factor's log.
    total, keep_rows = n, slice(None)
    if draw_rows is not None:
        total, keep_rows = int(draw_rows[0]), np.asarray(draw_rows[1], dtype=int)
        if keep_rows.shape != (n,) or keep_rows.min() < 0 or keep_rows.max() >= total:
            raise ValueError("Keep one row per draw, each inside the full run.")
    onset = rng.uniform(p["onset_low"], p["onset_high"], total)[keep_rows] / 12
    if onset_years is not None:
        onset = np.asarray(onset_years, dtype=float).copy()
        if onset.shape != (n,) or np.isnan(onset).any() or np.isneginf(onset).any():
            raise ValueError("Provide one onset date per draw; dates must be finite or +inf.")
    # Rows fill in order, so appending a factor leaves the earlier draws unchanged.
    # Rows 4, 6, 7 and 11 fed retired milestones; they stay drawn so the others
    # keep their values.
    raw = rng.uniform(-1, 1, (22, total))[:, keep_rows]
    z = normal_scores(raw)
    spread = p["uncertainty"] / 100
    factors = np.exp(spread * z)
    software_rate = np.log(2) * 12 / p["software_months"] * factors[0]
    if software_scale is not None:
        software_scale = np.asarray(software_scale, dtype=float)
        if software_scale.shape != (n,) or not np.isfinite(software_scale).all() \
                or (software_scale <= 0).any():
            raise ValueError("Provide one finite, positive software-rate multiple per draw.")
        software_rate = software_rate * software_scale
    compute_rate = np.log(p["compute_growth"]) * factors[1]
    if compute_rates is not None:
        compute_rate = np.asarray(compute_rates, dtype=float).copy()
        if compute_rate.shape != (n,) or not np.isfinite(compute_rate).all() \
                or (compute_rate < 0).any():
            raise ValueError("Provide one finite, non-negative compute growth rate per draw.")
    exp_rate = compute_rate
    if experiment_rates is not None:
        exp_rate = np.asarray(experiment_rates, dtype=float).copy()
        if exp_rate.shape != (n,) or not np.isfinite(exp_rate).all() or (exp_rate < 0).any():
            raise ValueError("Provide one finite, non-negative experiment-compute growth "
                             "rate per draw.")
    fol = _follower_inputs(follower, n) if follower is not None else None
    if fol is not None and coding_capability is None:
        raise ValueError("A follower needs the capability at which its coding is automated.")
    train_time = p["training_months"] / 12 * factors[2]
    eval_time = p["validation_months"] / 12 * factors[3]
    taste_slope = p["taste_slope"] * np.exp(p["judgment_spread"] / 100 * z[5])
    drift = np.maximum(p["judgment_drift"] / 100 + p["drift_spread"] / 100 * z[16], -0.9)
    # rho through the elasticity of substitution 1 / (1 - rho), lognormal
    # around the setting's, held inside the range `validate` accepts.
    elasticity = np.exp(-np.log1p(-p["substitution"]) + p["substitution_spread"] / 100 * z[17])
    rho = np.clip(1 - 1 / elasticity, -5, 0.9)
    # Human-work priors share the realized capability path, while retaining
    # separate bottlenecks for each critical workflow.
    starts = np.minimum(np.array([p["human_" + s] for s in WORKFLOW_KEYS])[None, :]
                        / 100 * factors[12:15].T, 1)
    floor = p["human_floor"] / 100
    starts = np.maximum(starts, floor)
    halves = np.array([p["half_" + s] for s in WORKFLOW_KEYS])[None, :] * factors[8:11].T
    # Each stage's pace along `human_curve` is the settings' weighted halving
    # time over its own (with its draw's spread).
    reference_half = float(np.array([p["half_" + s] for s in WORKFLOW_KEYS]) @ WORKFLOW_WEIGHTS)

    def humans(capability, t=None, software=None):
        # A follower's hours are its leader's at the same ECI: the leader's
        # capability there, on the leader's clock.
        rate = baseline_capability_rate
        if fol is not None:
            capability = fol["equivalent"](fol["eci"](capability, software))
            rate = fol["rate"]
        # Direction is handed over faster as AI judgment passes today's AI's.
        # Clipped in logs: a runaway's judgment would overflow, and past e^30
        # direction has long since been handed over.
        pace = (np.exp(np.minimum(p["direction_adoption"] * ai_judgment_log(
                    capability, taste_slope, drift, transfer, p["judgment_cap"]), 30))
                if p["direction_adoption"] else None)
        hours = workflow_state(capability, rate, starts, halves, floor,
                               human_curve, reference_half, pace, backward=fol is not None)
        if t is None:
            return hours
        # AI cannot direct research before it can code: direction holds at the
        # RSI bar until the draw's coding date at time(s) `t`.
        uncoded = coding > t + 1e-12
        hours[uncoded, 0] = np.maximum(hours[uncoded, 0], p["full_human"] / 100)
        return hours
    baseline_capability_rate = software_rate + compute_rate
    events = {name: np.full(n, np.inf) for name in MILESTONES}
    outcomes = {name: {key: np.full(n, np.nan) for key in
                      ("human_mean", "human_worst", "human_direction",
                       "human_experiments", "human_verification",
                       "progress_multiple", "compute_matched_advantage")}
                for name in ("Today", "Full coding automation") + MILESTONES}

    def record(name, mask, human, progress, advantage):
        for key, values in (("human_mean", human @ WORKFLOW_WEIGHTS),
                            ("human_worst", human.max(axis=1)),
                            ("human_direction", human[:, 0]),
                            ("human_experiments", human[:, 1]),
                            ("human_verification", human[:, 2]),
                            ("progress_multiple", progress),
                            ("compute_matched_advantage", advantage)):
            outcomes[name][key][mask] = values[mask]

    record("Today", np.ones(n, bool), starts, np.ones(n), np.ones(n))
    coding_recorded = onset <= 0
    # Coding counts as automated at the inherited date, or once a deployed
    # model reaches `coding_capability`, whichever comes first.
    coding = onset.copy()
    record("Full coding automation", onset == 0, starts, np.ones(n), np.ones(n))
    rsi0 = (onset <= 0) & (starts[:, 0] <= p["full_human"] / 100)
    events["RSI"][rsi0] = 0
    record("RSI", rsi0, starts, np.ones(n), np.ones(n))
    # Undeployed discoveries already in progress today. The matched reference
    # receives the identical backlog; it is never a second starting multiplier.
    initial_stock = software_rate * p["pipeline_months"] / 12
    software = initial_stock.copy()
    deployed = np.zeros(n)
    # Monthly observations of available models, never unfinished training runs.
    workflow_grid = np.unique(np.r_[np.arange(0, p["years"], 1 / 12), p["years"]])
    capability_history = np.zeros((n, len(workflow_grid)))
    validated_history = np.zeros_like(capability_history)
    # The deployed model's algorithmic efficiency as it pays off at its scale.
    realized_history = np.zeros_like(capability_history)
    # Share of compute running AI researchers (training's share is fixed).
    agent_share_history = np.full_like(
        capability_history, (100 - p["training_share"] - p["experiment_share"]) / 100)
    # Monthly frontier compute (log, vs today) and the research stock found by
    # then, for the scale-dependent lag; months not yet reached read +inf.
    compute_seen = np.full_like(capability_history, np.inf)
    compute_seen[:, 0] = 0.0
    stock_seen = np.zeros_like(capability_history)
    stock_seen[:, 0] = initial_stock
    row_offset = np.arange(n) * 1e7       # wider than any row's range
    seen_flat = [None]                    # compute_seen flattened, rebuilt on change
    reference_history = np.zeros_like(capability_history)
    # Share of gains that skip the training-run wait, logit-normal per draw
    # (row 21); 0 and 100 stay exact.
    with np.errstate(divide="ignore"):
        fast_logit = (np.log(p["fast_share"]) - np.log(100 - p["fast_share"])
                      if 0 < p["fast_share"] < 100
                      else (np.inf if p["fast_share"] >= 100 else -np.inf))
    fast_fraction = 1 / (1 + np.exp(-(fast_logit + p["fast_share_spread"] / 100 * z[21])))
    fast_time = p["fast_months"] / 12
    fast_next = np.full(n, fast_time)
    fast_snapshot = initial_stock.copy()
    fast_deployed = np.zeros(n)
    reference_fast = np.zeros(n)
    last_validated = np.zeros(n)
    last_reference = np.zeros(n)
    snapshot = initial_stock.copy()
    run_compute = np.zeros(n)
    training_used = np.zeros(n)
    run_start = np.zeros(n)
    # The frozen-AI reference's progress above today's stock, now and when the
    # current run and fast cycle began (it snapshots on the same clock).
    reference_gained = np.zeros(n)
    reference_at_run_start = np.zeros(n)
    reference_at_fast_start = np.zeros(n)
    # This run's training length and the pending model's validation length;
    # both shrink with the serial speed-up (see `serial_speedup`).
    run_len = train_time.copy()
    eval_len = eval_time.copy()
    pending = np.zeros(n)
    pending_software = np.zeros(n)
    deployed_software = np.zeros(n)
    last_deploy = np.zeros(n)
    delivered_rate = np.zeros(n)
    reference_delivered = np.zeros(n)
    reference_deployed = np.zeros(n)
    reference_pending_software = np.zeros(n)
    reference_pending_capability = np.zeros(n)
    advantage = np.zeros(n)
    finished = np.zeros(n, dtype=bool)
    last_labor = np.ones(n)
    last_experiments = np.ones(n)
    shares = np.array([p["training_share"], p["experiment_share"],
                       100 - p["training_share"] - p["experiment_share"]]) / 100
    # Frontier compute (log, vs today) when the current run, the pending
    # model's run and the deployed model's run started: a model's scale.
    run_start_scale = np.zeros(n)
    pending_scale = np.zeros(n)
    deployed_scale = np.zeros(n)
    transfer = p["transfer"] / 100
    # difficulty = lambda / r, so a lognormal r gives a lognormal difficulty.
    beta = p["difficulty"] * np.exp(p["returns_spread"] / 100 * z[15])
    # Software ceiling in natural-log efficiency above today's stock, uniform
    # between the settings (row 18); inf without one.
    # Uniform between the settings, its rank tied to r's draw: higher r (row
    # 15 low, since difficulty = lambda / r) goes with a farther ceiling.
    link = p["ceiling_returns_corr"]
    ceiling_rank = np.array([NormalDist().cdf(v) for v in
                             -link * z[15] + np.sqrt(1 - link ** 2) * z[18]])
    ceiling = (np.log(10) * (p["ceiling_low_oom"] + (p["ceiling_high_oom"] - p["ceiling_low_oom"])
                             * ceiling_rank)
               if p["ceiling_high_oom"] > 0 and p["difficulty"] > 0 else np.full(n, np.inf))
    capped = np.isfinite(ceiling)
    all_capped = bool(capped.all())   # lets the step skip the uncapped branch
    # Scale-dependent share of algorithmic gains, logit-normal per draw (row 19).
    share_pct = p["scale_dependent"]
    with np.errstate(divide="ignore"):
        share_logit = (np.log(share_pct) - np.log(100 - share_pct) if 0 < share_pct < 100
                       else (np.inf if share_pct >= 100 else -np.inf))
    corr = p["compute_bound_corr"]
    share_score = -corr * z[17] + np.sqrt(1 - corr ** 2) * z[19]
    scale_share = 1 / (1 + np.exp(-(share_logit + p["scale_dependent_spread"] / 100 * share_score)))
    # The compute growth (natural log) a scale-dependent gain waits for (row 20).
    scale_lag = np.log(10) * p["scale_lag_oom"] * np.exp(p["scale_lag_spread"] / 100 * z[20])
    parallel = p["parallelization"]
    initial_throughput = np.broadcast_to(_ces((shares[2] / 0.2) ** parallel,
                                              (shares[1] / 0.4) ** parallel, rho), (n,)).copy()
    # Today's pace has held steady while compute grew at its historical rate.
    # The other research inputs grow (or lag) by whatever holds that steady
    # state, d(software)/dt = rate * pace with pace = inputs^parallel /
    # exp(beta * software), so with AI frozen only a change in compute growth
    # from its historical rate moves the pace. Never applied to training.
    hist_rate = (compute_rate if historical_compute_rate is None
                 else np.full(n, float(historical_compute_rate)))
    # Software growth per unit of compute growth in the history behind today's
    # pace: the scale at which scale-dependent gains have paid off so far.
    scale_ratio = np.divide(software_rate, hist_rate, out=np.full(n, np.inf), where=hist_rate > 0)

    def pays_off(rows, scale_now, trained_software, fast_software, reference_trained):
        """For draws `rows`, a model's algorithmic part as it pays off at its
        compute. Fast gains (tooling, kernels: Gundlach et al.'s
        scale-invariant kind) count at once. Of the gains that came through
        training, the scale-dependent share counts in full only for gains
        found while frontier compute was `scale_lag` below the frontier
        compute when this model's run began (before today, history's balanced
        path: today's stock plus `scale_ratio` x that compute), plus what
        history's balanced pace adds over one lag, and never below the
        frozen-AI reference's trained software for the same model, which
        already carries history's own pace. Gains found faster wait until
        models train at that much more compute, then count in full."""
        lag = scale_lag[rows]
        target = scale_now - lag
        # Each row of compute_seen is non-decreasing, so offsetting row i by
        # i x span sorts them all into one array: one search finds every row.
        if seen_flat[0] is None:
            seen_flat[0] = (np.where(np.isfinite(compute_seen), compute_seen, 1e6)
                            + row_offset[:, None]).ravel()
        last = len(workflow_grid) - 1
        idx = np.searchsorted(seen_flat[0], np.minimum(target, 1e6 - 1) + row_offset[rows],
                              side="right") - rows * (last + 1) - 1
        c0 = compute_seen[rows, np.maximum(idx, 0)]
        s0 = stock_seen[rows, np.maximum(idx, 0)]
        c1 = compute_seen[rows, np.minimum(idx + 1, last)]
        s1 = stock_seen[rows, np.minimum(idx + 1, last)]
        # Past the last month recorded, interpolate toward the present.
        ahead = ~np.isfinite(c1) | (idx >= last)
        c1 = np.where(ahead, frontier_log(t[rows], rows) + boost_log[rows], c1)
        s1 = np.where(ahead, software[rows], s1)
        ratio = scale_ratio[rows]
        with np.errstate(invalid="ignore", divide="ignore"):
            frac = np.clip(np.divide(target - c0, c1 - c0, out=np.zeros(len(rows)),
                                     where=c1 > c0), 0, 1)
            earlier = np.where(idx >= 0, s0 + frac * (s1 - s0),
                               initial_stock[rows] + ratio * target)
            due = np.where(np.isinf(ratio), np.inf, np.maximum(
                (1 - fast_fraction[rows]) * (earlier + ratio * lag), reference_trained))
        return (fast_software + trained_software
                - scale_share[rows] * np.maximum(trained_software - due, 0))

    def realized(rows=None):
        """(training-compute part, algorithmic part as it pays off, capability)
        of the deployed model, refreshed in `now` for draws `rows` (all by
        default)."""
        rows = np.arange(n) if rows is None else rows
        compute_part_now = deployed[rows] - deployed_software[rows]
        paid = pays_off(rows, deployed_scale[rows], deployed_software[rows], fast_deployed[rows],
                        reference_delivered[rows])
        now[0][rows], now[1][rows] = compute_part_now, paid
        now[2][rows] = compute_part_now + paid
        return now

    # From `slow_at`, compute keeps `compute_slowdown`% of its log growth.
    slow_at = p["compute_slow_years"]
    compute_late = compute_rate * p["compute_slowdown"] / 100
    cpath = _check_path(compute_path, n, "compute") if compute_path is not None else None
    epath = (_check_path(experiment_path, n, "experiment compute")
             if experiment_path is not None else None)
    all_rows = np.arange(n)
    review_from, review_to, review_time = np.inf, np.inf, 0.0
    if review is not None:
        review_from, review_time = float(review[0]), float(review[1]) / 12
        if len(review) > 2 and review[2] is not None:
            review_to = float(review[2])
        if not np.isfinite(review_from) or review_from < 0 or not review_time >= 0 \
                or not review_to > review_from:
            raise ValueError("A review rule needs a start at or after today, an end "
                             "after it and a review time of zero or more months.")

    def under_review(x):
        return (x >= review_from - 1e-12) & (x < review_to - 1e-12)
    cut = use_cut = None
    if compute_cut is not None:
        by_use = isinstance(compute_cut[1], dict)
        if by_use and set(compute_cut[1]) != set(COMPUTE_USES):
            raise ValueError(f"A compute cut by use needs exactly {COMPUTE_USES}.")
        cut_years = np.asarray(compute_cut[0], dtype=float)

        def cut_path(logs):
            logs = np.asarray(logs, dtype=float)
            return _check_path((cut_years, np.broadcast_to(
                logs, (n, logs.shape[-1]))), n, "compute cut")
        if by_use:
            use_cut = {k: cut_path(v) for k, v in compute_cut[1].items()}
            cut = use_cut["training"]
        else:
            cut = cut_path(compute_cut[1])
            if cut[1].min() < 0:
                raise ValueError("A compute cut is a log reduction, zero or more.")

    def cut_log(u, rows=all_rows):
        """The cut in training compute, which is every use's without a
        by-use cut."""
        return 0.0 if cut is None else _paths_at(cut[1], cut[0], u, rows)

    def use_shift(use, u):
        """Log compute `use` keeps beyond training's under a by-use cut."""
        if use_cut is None:
            return 0.0
        return cut_log(u) - _paths_at(use_cut[use][1], cut_years, u, all_rows)

    def uncut_log(u, rows=all_rows):
        if cpath is None:
            return log_level(u, compute_rate[rows], compute_late[rows], slow_at)
        return _paths_at(cpath[1], cpath[0], u, rows)

    def frontier_log(u, rows=all_rows):
        """Training compute (log, vs today) for draws `rows` at their times
        `u`: the frontier less any `compute_cut`."""
        return uncut_log(u, rows) - cut_log(u, rows)
    # Amdahl: AI labor on research speeds up as the human share h falls, by
    # (h0 + (1 - h0)/s) / (h + (1 - h)/s), normalized to today's share h0.
    ai_speed = p["ai_speed"]
    # Today's human hours: the settings' starts, or a follower's own (its
    # leader's hours at the follower's ECI today, run back if behind).
    today_hours = starts if fol is None else humans(np.zeros(n), None, np.zeros(n))
    human0 = today_hours @ WORKFLOW_WEIGHTS
    if fol is not None:
        record("Today", np.ones(n, bool), today_hours, np.ones(n), np.ones(n))
    amdahl0 = np.log(human0 + (1 - human0) / ai_speed)
    # Today's research quality, so the level of AI judgment moves only what
    # handing direction over buys, not today's calibrated pace.
    quality0_log = np.log(today_hours[:, 0] + (1 - today_hours[:, 0]) * p["judgment_today"])
    # Non-AI inputs. Human staff grow `hiring_growth` a year until RSI and
    # `staff_after_rsi` after, speeding the human share of the work; their
    # effect on labor today is that growth times the human share of the time.
    inputs_on = p["baseline_inputs"] / 100
    hire_rate = inputs_on * np.log1p(p["hiring_growth"] / 100)
    after_rate = inputs_on * np.log1p(p["staff_after_rsi"] / 100)
    hire_effect = hire_rate * human0 / (human0 + (1 - human0) / ai_speed)
    # Experiment compute grows at a fixed share of the frontier's log growth,
    # fitted so that research inputs (labor and experiments, half each at
    # today's normalized shares) grow at the rate that holds today's pace
    # steady with AI frozen, as history had it while compute grew at
    # `hist_rate`: the frontier's 3.1x a year buys more than that, so
    # experiment compute grows slower (about 1.6x a year, a 0.4 share), and
    # slows in step when the frontier does.
    steady = beta * software_rate * initial_throughput / parallel
    exp_growth = np.maximum(
        hist_rate + inputs_on * (2 * steady - 2 * hist_rate) - hire_effect, 0)
    # With no historical compute growth to take a share of, experiment
    # compute grows at the fitted rate itself.
    has_history = hist_rate > 1e-9
    exp_share = np.divide(exp_growth, hist_rate, out=np.ones(n), where=has_history)
    # Experiment compute of its own (`experiment_rates`): the same fitted
    # steady-state share, of its own growth against its own history.
    own_experiments = (experiment_rates is not None or historical_experiment_rate is not None
                       or experiment_path is not None)
    if own_experiments:
        exp_hist = (hist_rate if historical_experiment_rate is None
                    else np.full(n, float(historical_experiment_rate)))
        has_history = exp_hist > 1e-9
        exp_share = np.divide(exp_growth, exp_hist, out=np.ones(n), where=has_history)
    exp_late = exp_rate * p["compute_slowdown"] / 100
    # What research inputs grow by on average, for the trend blend.
    input_rate = compute_rate + (hire_effect + np.where(
        has_history, exp_share * exp_rate - compute_rate, exp_growth)) / 2
    # Ongoing useful research production is distinct from batched deliveries.
    # Today's production baseline already includes existing AI assistance.
    pace_history = np.repeat(initial_throughput[:, None], len(workflow_grid), axis=1)
    reference_pace_history = pace_history.copy()
    # log pace = resources + judgment - difficulty, recorded with the pace so
    # the chart can show what moves it. Resources carry the trend blend and
    # split exactly as compute + labor + ai: CES is homogeneous, so the input
    # growth labor and experiments share (compute, and the non-AI inputs)
    # comes off it whole; the rest is AI help through the CES.
    factor_history = {k: np.zeros_like(capability_history)
                      for k in ("resources", "judgment", "difficulty",
                                "compute", "labor", "ai")}
    factor_history["resources"][:] = np.log(initial_throughput)[:, None]
    factor_history["compute"][:] = np.log(initial_throughput)[:, None]
    last_factors = {k: v[:, 0].copy() for k, v in factor_history.items()}
    observation_index = np.ones(n, dtype=int)
    last_pace = initial_throughput.copy()
    last_reference_pace = initial_throughput.copy()
    # Today's model's training compute: a three-month run at the reference
    # 40% allocation. This constant must not depend on the chosen run duration.
    reference_train_compute = 0.4 * 3 / 12
    # Each draw advances at most one week, stopping exactly at its own run
    # completion/deployment events. This avoids adding a rounding delay every
    # cycle (which could move an entire milestone to the next successor).
    t = np.zeros(n)
    stopped_at = np.full(n, np.inf)
    # Extra log compute from `rsi_compute_boost` after each draw's RSI; the
    # frozen-AI reference never gets it.
    boost = p["rsi_compute_boost"] - 1
    boost_log = np.zeros(n)
    boost_history = np.zeros_like(capability_history)
    now = (np.zeros(n), np.zeros(n), np.zeros(n))
    # A follower's inflow (capability-log units) and its ECI by channel.
    follow_log = np.zeros(n)
    follow_eci = {k: np.zeros(n) for k in FOLLOW_CHANNELS} if fol is not None else {}
    follow_history = {k: np.zeros_like(capability_history) for k in follow_eci}
    theft_jumped = weights_taken = False
    if fol is not None:
        coding_level = np.broadcast_to(np.asarray(coding_capability, dtype=float), (n,)).copy()
    realized()                  # the deployed model, refreshed when it changes
    carried_hours = None
    histories = (capability_history, realized_history, validated_history, reference_history)
    held_now = tuple(np.zeros(n) for _ in histories)
    if COMPILED and _numba is not None and (fol is None or (
            fol["theft_jump"] is None and fol["weight_theft"] is None)):
        # The compiled loop fills the same arrays; the numpy loop then
        # finds every draw at the horizon and does not run.
        o = _k_simulate(
            n=n, p=p, step=step, fol=fol, cpath=cpath, epath=epath, cut=cut, use_cut=use_cut,
            human_curve=human_curve, coding=coding, rsi=events["RSI"],
            outcomes=outcomes, histories=histories, pace_history=pace_history,
            reference_pace_history=reference_pace_history,
            agent_share_history=agent_share_history, boost_history=boost_history,
            factor_history=factor_history, follow_history=follow_history,
            experiment_slopes=experiment_slopes, coding_capability=coding_capability,
            coding_weights=coding_weights, review=(review_from, review_to, review_time),
            v=dict(starts=starts, halves=halves, today_hours=today_hours,
                   software_rate=software_rate, compute_rate=compute_rate,
                   compute_late=compute_late, exp_rate=exp_rate, exp_late=exp_late,
                   exp_share=exp_share, exp_growth=exp_growth, has_history=has_history,
                   initial_throughput=initial_throughput, initial_stock=initial_stock,
                   train_time=train_time, eval_time=eval_time, scale_ratio=scale_ratio,
                   amdahl0=amdahl0, quality0_log=quality0_log, human0=human0,
                   hire_effect=hire_effect, input_rate=input_rate, taste_slope=taste_slope,
                   drift=drift, rho=rho, beta=beta, ceiling=ceiling, scale_share=scale_share,
                   scale_lag=scale_lag, fast_fraction=fast_fraction,
                   bcr=baseline_capability_rate, transfer=transfer, parallel=parallel,
                   shares=shares, ai_speed=ai_speed, hire_rate=hire_rate,
                   after_rate=after_rate, fast_time=fast_time, floor=floor,
                   reference_half=reference_half, slow_at=slow_at,
                   own_experiments=own_experiments, boost=boost,
                   reference_train_compute=reference_train_compute,
                   grid=workflow_grid))
        (software, deployed, deployed_software, fast_deployed, training_used,
         delivered_rate, advantage, stopped_at, last_labor, last_experiments, last_pace,
         last_reference_pace, boost_log) = (
            o.software, o.deployed, o.deployed_software, o.fast_deployed, o.training_used,
            o.delivered_rate, o.advantage, o.stopped_at, o.last_labor, o.last_experiments,
            o.last_pace, o.last_reference_pace, o.boost_log)
        for k, key in enumerate(_K_FACTORS):
            last_factors[key] = o.last_factors[k]
        held_now = tuple(o.held)
        observation_index = o.obs
        t = np.full(n, float(p["years"]))
    while np.any(t < p["years"] - 1e-12):
        train_end = run_start + run_len
        deploy_end = train_end + eval_len
        next_event = np.minimum(np.where(finished, deploy_end, train_end), fast_next)
        next_event = np.minimum(next_event, np.where(coding > t + 1e-12, coding, np.inf))
        next_observation = workflow_grid[np.minimum(observation_index, len(workflow_grid) - 1)]
        next_event = np.minimum(next_event, next_observation)
        end = np.minimum(np.minimum(t + step, next_event), p["years"])
        active = t < p["years"] - 1e-12
        end = np.where(active, end, t)
        dt = np.maximum(end - t, 0)
        base_compute_log = frontier_log(t + dt / 2)
        # Share of the boost in force at mid-step: 0 until the delay after RSI
        # has passed, then rising linearly to 1 over the ramp.
        since = t + dt / 2 - events["RSI"] - p["rsi_compute_delay"] / 12
        ramp = p["rsi_compute_ramp"] / 12
        boosting = np.isfinite(events["RSI"]) & (t >= events["RSI"] - 1e-12)
        in_force = np.where(boosting, np.clip(since / ramp, 0, 1) if ramp > 0
                            else (since >= 0).astype(float), 0.0)
        # The boost scales the frontier's own log growth over the step: the
        # constant rate, or a supplied path's rise (none where it is flat or
        # falls; `test_a_flat_compute_path_stays_flat_under_the_rsi_boost`).
        growth = (np.where(t + dt / 2 < slow_at, compute_rate, compute_late) * dt
                  if cpath is None else np.maximum(uncut_log(end) - uncut_log(t), 0.0))
        boost_step = np.where(boosting, boost * in_force * growth, 0.0)
        compute_log = base_compute_log + boost_log + boost_step / 2
        # Experiment compute's shortfall from the frontier, and staff headcount
        # (vs today) on the draw's own RSI clock.
        # The shortfall is measured off the uncut frontier, so experiments
        # take a `compute_cut` whole.
        uncut_base = base_compute_log + cut_log(t + dt / 2)
        if own_experiments:
            exp_level = (log_level(t + dt / 2, exp_rate, exp_late, slow_at) if epath is None
                         else _paths_at(epath[1], epath[0], t + dt / 2, all_rows))
            exp_log = np.where(has_history, exp_share * exp_level - uncut_base,
                exp_growth * (t + dt / 2))
        else:
            exp_log = np.where(has_history, (exp_share - 1) * uncut_base,
                               exp_growth * (t + dt / 2))
        mid_t = t + dt / 2
        # Without AI transfer nothing changes at RSI, as in the reference.
        staff_rsi = events["RSI"] if transfer else np.inf
        head_log = (hire_rate * np.minimum(mid_t, staff_rsi)
                    + after_rate * np.maximum(mid_t - staff_rsi, 0))
        # The deployed model only changes at the end of a step, where `now`
        # is refreshed, so the last step's reading still holds here.
        effective = now[2] + follow_log
        # The last step's closing hours were read at this same capability and
        # time, so they are reused (unless a draw diverged, which moves its t).
        human_now = (carried_hours if carried_hours is not None
                     else humans(effective, t, now[1] + follow_log))
        if p["rsi_autopilot"]:
            human_now[np.isfinite(events["RSI"]) & (t >= events["RSI"] - 1e-12)
                      & ~under_review(t)] = 0.0
        share_now = human_now @ WORKFLOW_WEIGHTS
        # More copies of the AI researcher on the same compute as its
        # algorithms improve: AI's share of the work speeds up with them.
        # In logs, so a runaway's copies never overflow.
        log_speed = np.log(ai_speed) + p["ai_copies"] * np.maximum(now[1] + follow_log, 0)
        with np.errstate(divide="ignore"):
            amdahl_log = amdahl0 - np.logaddexp(np.log(share_now),
                                                np.log1p(-share_now) - log_speed)
            # More staff finish the human share of the work sooner; none of it
            # once the share is 0. Without AI transfer the share stays today's
            # for labor, as the frozen-AI reference has it.
            staff_share = share_now if transfer else human0
            staff_speed = log_speed if transfer else np.log(ai_speed)
            headcount_log = (np.logaddexp(np.log(staff_share), np.log1p(-staff_share) - staff_speed)
                             - np.logaddexp(np.log(staff_share) - head_log,
                                            np.log1p(-staff_share) - staff_speed))
        # People still directing research keep today's judgment; AI's applies
        # to the rest, so research quality is the direction-weighted mix.
        direction = human_now[:, 0]
        # The RSI anchor supplies a smooth reduction in coding human hours.
        # Its productivity gain and endogenous coding gains overlap: use the
        # larger, not their product. Existing assistance is normalized to 1.
        coding_fraction = np.clip(np.divide(t + dt / 2, coding,
            out=np.ones(n), where=coding > 0), 0, 1)
        coding_fraction = np.where(coding <= 0, 0, coding_fraction)
        if fol is not None:
            # No inherited date: the ramp runs on capability, from today's
            # level to the one that automates coding.
            level_now = (effective if coding_weights is None else
                         coding_weights[0] * now[0] + coding_weights[1] * (now[1] + follow_log))
            coding_fraction = np.where(coding <= t + 1e-12, 1.0, np.clip(np.divide(
                level_now, coding_level, out=np.ones(n), where=coding_level > 0), 0, 1))
        rsi_coding_log = np.log((1 - p["coding_today"] / 100) / .05) * coding_fraction
        coding_gain = np.maximum(rsi_coding_log, p["coding_slope"] * effective)
        if transfer:
            coding_log = np.logaddexp(np.log1p(-transfer) if transfer < 1 else -np.inf,
                                     np.log(transfer) + coding_gain)
            # AI judgment against people's: today's level times its gain.
            ai_taste_log = np.log(p["judgment_today"]) + ai_judgment_log(
                effective, taste_slope, drift, transfer, p["judgment_cap"])
            with np.errstate(divide="ignore"):   # a share of 0 or 1 drops a term
                quality_log = (np.logaddexp(np.log(direction),
                                            np.log1p(-direction) + ai_taste_log)
                               - quality0_log)
            automation_log = np.logaddexp(np.log1p(-transfer) if transfer < 1 else -np.inf,
                                          np.log(transfer) + amdahl_log)
        else:
            coding_log = np.zeros(n)
            quality_log = np.zeros(n)
            automation_log = np.zeros(n)
        labor_log = parallel * (compute_log + np.log(shares[2] / 0.2)
                                + coding_log + automation_log + headcount_log)
        experiment_log = parallel * (compute_log + exp_log + np.log(shares[1] / 0.4))
        with np.errstate(divide="ignore"):
            ref_headcount = (amdahl0 - np.logaddexp(np.log(human0) - hire_rate * mid_t,
                                                    np.log1p(-human0) - np.log(ai_speed)))
        agent_shift = use_shift("agents", mid_t)
        exp_shift = use_shift("experiments", mid_t)
        agent_share = np.full(n, shares[2])
        if p["reallocate_compute"]:
            # How far AI has moved labor against experiments, beyond the
            # frozen-AI reference (compute and its boost cancel; zero without
            # transfer). The split then follows the CES first-order condition,
            # agents/experiments = today's ratio x exp(rho / (1 - parallel rho) x gap):
            # toward experiments when AI labor is abundant and they are
            # complements, toward more AI researchers when they substitute.
            gap = (labor_log - experiment_log) - parallel * (
                np.log(shares[2] / 0.2) + ref_headcount - exp_log - np.log(shares[1] / 0.4))
            log_ratio = (np.log(shares[2] / shares[1])
                         + rho / (1 - parallel * rho) * gap)
            pool = shares[1] + shares[2]
            agent_share = pool / (1 + np.exp(-np.clip(log_ratio, -700, 700)))
            agent_share = np.clip(agent_share, 1e-9 * pool, pool * (1 - 1e-9))
            labor_log = labor_log + parallel * np.log(agent_share / shares[2])
            experiment_log = experiment_log + parallel * np.log((pool - agent_share) / shares[1])
        labor_log = labor_log + parallel * agent_shift
        experiment_log = experiment_log + parallel * exp_shift
        research_log = _ces_log(labor_log, experiment_log, rho) + quality_log
        judgment_log = quality_log.copy()
        # Factor chart, exact: compute is the inputs with neither AI help nor
        # more staff, staff what they add to that (nothing once people do no
        # work), and AI help the rest (zero without transfer).
        staff_alone = headcount_log
        exp_in = parallel * (compute_log + exp_shift + exp_log + np.log(shares[1] / 0.4))
        agent_in = parallel * (compute_log + agent_shift + np.log(shares[2] / 0.2))
        # At today's split: any gain from re-splitting is AI's doing.
        bare = _ces_log(agent_in, exp_in, rho)
        compute_part = bare
        labor_part = _ces_log(agent_in + parallel * staff_alone, exp_in, rho) - bare
        if experiment_slopes is not None and transfer:
            mid = t + dt / 2
            resource_log = (np.log(initial_throughput) + parallel * input_rate * mid
                            - parallel * (cut_log(mid) - (agent_shift + exp_shift) / 2))
            residual = (experiment_slopes - parallel * compute_rate) * mid
            proxy_log = resource_log + p["rsi_useful_growth"] / 100 * residual
            weight = p["rsi_trend_weight"] / 100 * np.exp(
                -np.log(2) * mid * 12 / p["rsi_trend_months"])
            # Substitute between two estimates of total research effort; do
            # not multiply the trend into feedback already calibrated from it.
            research_log = (1 - weight) * research_log + weight * proxy_log
            judgment_log = (1 - weight) * quality_log
            compute_part = ((1 - weight) * compute_part + weight * (
                np.log(initial_throughput) + parallel * mid * np.where(
                    has_history, (compute_rate + exp_share * exp_rate) / 2,
                    compute_rate + exp_growth / 2)))
            labor_part = (1 - weight) * labor_part + weight * parallel * hire_effect / 2 * mid
        # Difficulty: beta per unit of progress, rising toward the ceiling,
        # where returns to research reach 0 (penalty = -beta C ln(1 - S/C)).
        gained = software - initial_stock

        def difficulty_at(progress):
            """(log x, penalty) at `progress` above today's stock."""
            with np.errstate(divide="ignore", invalid="ignore"):
                if all_capped:
                    lx = np.log1p(-np.minimum(progress / ceiling, 1))
                    return lx, -beta * ceiling * lx
                lx = np.where(capped, np.log1p(-np.minimum(progress / ceiling, 1)), 0.0)
                return lx, np.where(capped, -beta * np.where(capped, ceiling, 0) * lx,
                                    beta * progress)

        log_x, penalty = difficulty_at(gained)
        # The frozen-AI reference: same compute (no post-RSI boost), same
        # experiment compute and hiring, today's human share and AI skills;
        # integrated step by step like the actual path, never reaching RSI.
        ref_log_x, ref_penalty = difficulty_at(reference_gained)
        ref_research = _ces_log(
            parallel * (base_compute_log + agent_shift + np.log(shares[2] / 0.2)
                        + ref_headcount),
            parallel * (base_compute_log + exp_shift + exp_log + np.log(shares[1] / 0.4)), rho)
        reference_pace = np.exp(np.minimum(ref_research - ref_penalty, 700))
        ref_log_amount = np.log(software_rate) + ref_research + np.log(
            dt, out=np.full(n, -np.inf), where=dt > 0)
        log_amount = np.log(software_rate) + research_log + np.log(
            dt, out=np.full(n, -np.inf), where=dt > 0)
        # Derivative of the same discovery process being integrated below,
        # in multiples of today's software-progress rate. Snapshot near the
        # end of each monthly integration interval (at most one week long).
        pace = np.exp(np.minimum(research_log - penalty, 700))
        def advance(progress, progress_log_x, amount_log):
            """Progress above today's stock after research `amount_log`,
            integrated exactly for the step's research rate."""
            if p["difficulty"] > 0:
                with np.errstate(divide="ignore", invalid="ignore"):
                    near = -ceiling * np.expm1(
                        ceiling_step(progress_log_x, amount_log, beta * ceiling, ceiling))
                if all_capped:
                    return near
                plain = np.logaddexp(beta * progress, np.log(beta) + amount_log) / beta
                return np.where(capped, near, plain)
            return progress + np.exp(np.minimum(amount_log, 100))

        updated = initial_stock + advance(gained, log_x, log_amount)
        if fol is not None:
            # The follower's inflow over the step, in ECI, toward the leader's
            # released frontier from where its own research stands.
            standing = fol["eci_now"] + fol["w"][0] * now[0] + fol["w"][1] * (
                updated - initial_stock + follow_log)
            gap = np.maximum(fol["teacher"](mid_t) - standing, 0)
            stolen = np.minimum(fol["theft"] * fol["theft_scale"](mid_t), 1.0)
            flows = {"distillation": fol["distill"] * fol["distill_scale"](mid_t) * gap * dt,
                     # Each leaked idea arrives spread evenly over the
                     # absorption years after it left the leader.
                     "leak": fol["leak"] * (1 - stolen) * sum(
                         fol["leak_scale"](mid_t - lag) * np.maximum(
                             fol["software"](end - lag) - fol["software"](t - lag), 0)
                         for lag in fol["absorb"] * (np.arange(LEAK_POINTS) + 0.5)
                         / LEAK_POINTS) / LEAK_POINTS,
                     "theft": stolen * np.maximum(fol["software"](end) - fol["software"](t), 0),
                     "weights": np.zeros(n)}
            # Distillation closes on the released teacher; leaked and stolen
            # ideas come from the leader's labs, so on its trained frontier.
            flows["distillation"] = np.minimum(flows["distillation"], gap)
            room = (gap if fol["trained"] is None else
                    np.maximum(fol["trained"](mid_t) - standing, 0)) - flows["distillation"]
            ideas = flows["leak"] + flows["theft"]
            keep = np.divide(np.minimum(ideas, np.maximum(room, 0)), ideas,
                             out=np.zeros(n), where=ideas > 0)
            flows["leak"], flows["theft"] = flows["leak"] * keep, flows["theft"] * keep
            # One-off and ongoing theft land at their dates, toward the
            # leader's trained frontier rather than its released one.
            if fol["theft_jump"] is not None and not theft_jumped \
                    and np.all(end >= fol["theft_jump"][0] - 1e-12):
                when, share, skip, lift = fol["theft_jump"]
                ahead = fol["trained"](end) - standing - flows["distillation"] - flows["leak"]
                flows["theft"] = flows["theft"] + share * np.maximum(ahead - skip, 0) + lift
                theft_jumped = True
            if fol["weight_theft"] is not None \
                    and np.all(end >= fol["weight_theft"][0] - 1e-12) \
                    and (fol["weight_theft"][1] or not weights_taken):
                # Stolen weights are a model China deploys at once: top its
                # deployed model (not its undeployed research) up to the
                # leader's trained one.
                deployed_eci = fol["eci_now"] + fol["w"][0] * now[0] + fol["w"][1] * (
                    now[1] + follow_log)
                flows["weights"] = np.maximum(fol["trained"](end) - deployed_eci
                                              - sum(flows.values()), 0)
                weights_taken = True
            for key, flow in flows.items():
                follow_eci[key] += np.where(active, flow, 0)
            follow_log = follow_log + np.where(active, sum(flows.values()), 0) / fol["w"][1]
        reference_gained = advance(reference_gained, ref_log_x, ref_log_amount)
        # Stop numerically divergent draws explicitly, rather than silently
        # treating a numerical ceiling as a capability plateau.
        diverged = active & (updated > 1e6)
        # A runaway has automated coding whatever its inherited date says, and
        # its direction share is at the floor: RSI is reached unless the floor
        # sits above the bar, where no draw can ever reach it.
        rsi_possible = floor <= p["full_human"] / 100
        runaway_rsi = diverged & ~np.isfinite(events["RSI"]) & rsi_possible
        events["RSI"][runaway_rsi] = end[runaway_rsi]
        software = np.minimum(updated, 1e6)
        train_budget = (grown(t + dt, compute_rate, compute_late, slow_at)
                        - grown(t, compute_rate, compute_late, slow_at)
                        if cpath is None else np.exp(uncut_base) * dt) \
            * np.exp(boost_log + boost_step / 2 - cut_log(t + dt / 2))
        boost_log = boost_log + boost_step
        used = np.where(finished, 0, shares[0] * train_budget)
        run_compute += used
        training_used += used
        done = active & (~finished) & (end >= train_end - 1e-12)
        if p["serial_speedup"]:
            # Validation runs at the verification stage's mix of people and AI,
            # relative to today's mix.
            h_ver = human_now[:, 2]
            eval_len[done] = (eval_time * (h_ver + (1 - h_ver) / ai_speed)
                              / (today_hours[:, 2] + (1 - today_hours[:, 2]) / ai_speed))[done]
        # Under a review rule no model ships before people have reviewed it.
        reviewed = done & under_review(end)
        eval_len[reviewed] = np.maximum(eval_len[reviewed], review_time)
        candidate_compute = np.log(np.maximum(run_compute / reference_train_compute, 1e-12))
        candidate = (1 - fast_fraction) * snapshot + candidate_compute
        reference_snapshot = initial_stock + reference_at_run_start
        # A successor ships only if it beats the deployed model as both pay off
        # at their own scale (a short run can carry more algorithms on less
        # compute and still be worse).
        adopted = np.zeros(n, dtype=bool)
        hit = np.flatnonzero(done)
        if hit.size:
            adopted[hit] = candidate_compute[hit] + pays_off(
                hit, run_start_scale[hit], ((1 - fast_fraction) * snapshot)[hit],
                fast_deployed[hit], ((1 - fast_fraction) * reference_snapshot)[hit]) > now[2][hit]
        pending[done] = np.where(adopted[done], candidate[done], deployed[done])
        pending_scale[done] = np.where(adopted[done], run_start_scale[done], deployed_scale[done])
        pending_software[done] = np.where(adopted[done], ((1 - fast_fraction) * snapshot)[done], deployed_software[done])
        reference_candidate = (1 - fast_fraction) * reference_snapshot + np.log(
            np.maximum(run_compute / reference_train_compute, 1e-12))
        reference_pending_capability[done] = np.maximum(reference_deployed[done], reference_candidate[done])
        reference_pending_software[done] = np.where(
            reference_candidate[done] > reference_deployed[done],
            ((1 - fast_fraction) * reference_snapshot)[done], reference_delivered[done])
        finished |= done
        ready = active & finished & (end >= deploy_end - 1e-12)
        # Fast gains keep landing on the deployed model during validation, so
        # check again at deployment: a successor that has fallen behind it as
        # both pay off is dropped.
        pending_compute = pending - pending_software
        behind = np.zeros(n, dtype=bool)
        hit = np.flatnonzero(ready)
        if hit.size:
            behind[hit] = pending_compute[hit] + pays_off(
                hit, pending_scale[hit], pending_software[hit], fast_deployed[hit],
                reference_pending_software[hit]) < now[2][hit] - 1e-12
        pending[behind] = deployed[behind]
        pending_software[behind] = deployed_software[behind]
        pending_scale[behind] = deployed_scale[behind]
        deployed[ready] = pending[ready]
        deployed_scale[ready] = pending_scale[ready]
        fast_ready = active & (end >= fast_next - 1e-12)
        fast_deployed[fast_ready] = (fast_fraction * fast_snapshot)[fast_ready]
        reference_fast[fast_ready] = fast_fraction[fast_ready] * (initial_stock[fast_ready]
                                                      + reference_at_fast_start[fast_ready])
        reference_at_fast_start[fast_ready] = reference_gained[fast_ready]
        fast_snapshot[fast_ready] = software[fast_ready]
        fast_next[fast_ready] += np.where(under_review(end[fast_ready]),
                                          max(fast_time, review_time), fast_time)
        # For non-ready slow runs, only their already deployed algorithms count.
        validated = np.where(ready, pending_software, deployed_software) + fast_deployed
        reference_validated = np.where(ready, reference_pending_software,
                                        reference_delivered) + reference_fast
        delivered_rate[ready] = progress_multiple(last_validated[ready], validated[ready],
            end[ready] - last_deploy[ready], software_rate[ready])
        reference_rate = progress_multiple(last_reference[ready], reference_validated[ready],
            end[ready] - last_deploy[ready], software_rate[ready])
        advantage[ready] = np.divide(delivered_rate[ready], reference_rate,
            out=np.zeros(ready.sum()), where=reference_rate > 0)
        last_validated[ready] = validated[ready]
        last_reference[ready] = reference_validated[ready]
        reference_delivered[ready] = reference_pending_software[ready]
        reference_deployed[ready] = reference_pending_capability[ready]
        deployed_software[ready] = pending_software[ready]
        last_deploy[ready] = end[ready]
        changed = np.flatnonzero(ready | fast_ready)
        if changed.size:
            realized(changed)
        compute_now, software_now, effective = (v.copy() for v in now)
        software_now += follow_log
        effective += follow_log
        if coding_capability is not None:
            level = effective
            if coding_weights is not None:
                level = coding_weights[0] * compute_now + coding_weights[1] * software_now
            capable = active & (level >= coding_capability) & (coding > end)
            coding[capable] = end[capable]
        # Each month's history is the value at the last change by then; it is
        # written when the month is observed below (and held to the end after).
        rows = np.flatnonzero(ready | fast_ready)
        for held_value, values in zip(held_now, (effective, software_now, validated,
                                                 reference_validated)):
            held_value[rows] = values[rows]
        # A diverged draw's state is a numerical ceiling: record nothing from it.
        live = active & ~diverged
        human = humans(effective, end, software_now)
        carried_hours = None if diverged.any() else human
        coding_hit = active & (end >= coding) & ~coding_recorded
        record("Full coding automation", coding_hit, human, delivered_rate, advantage)
        coding_recorded |= coding_hit
        hit = (live & (end >= coding) & (human[:, 0] <= p["full_human"] / 100)
               & ~np.isfinite(events["RSI"]))
        events["RSI"][hit] = end[hit]
        record("RSI", hit, human, delivered_rate, advantage)
        tracking = events["RSI"] >= end
        last_labor[tracking] = labor_log[tracking]
        last_experiments[tracking] = experiment_log[tracking]
        snapshot[ready] = software[ready]
        run_start[ready] = end[ready]
        reference_at_run_start[ready] = reference_gained[ready]
        if p["serial_speedup"]:
            # The next run is shorter when capability is growing faster than
            # today: today's growth rate over the current one, capped at 1.
            growth_now = software_rate * pace + np.where(end < slow_at, compute_rate, compute_late)
            run_len[ready] = (train_time * np.minimum(
                1.0, baseline_capability_rate / np.maximum(growth_now, 1e-9)))[ready]
        run_start_scale[ready] = (frontier_log(end) + boost_log)[ready]
        run_compute[ready] = 0
        finished[ready] = False
        observed = active & (end >= next_observation - 1e-12)
        rows = np.flatnonzero(observed)
        pace_history[rows, observation_index[rows]] = pace[rows]
        agent_share_history[rows, observation_index[rows]] = agent_share[rows]
        # The highest compute so far: under a cut it falls, and `pays_off`
        # searches each row as sorted.
        seen_now = np.maximum((frontier_log(end) + boost_log)[rows],
                              compute_seen[rows, np.maximum(observation_index[rows] - 1, 0)])
        compute_seen[rows, observation_index[rows]] = seen_now
        if seen_flat[0] is not None:     # fill the same cells of the sorted copy
            seen_flat[0][rows * len(workflow_grid) + observation_index[rows]] = (
                seen_now + row_offset[rows])
        stock_seen[rows, observation_index[rows]] = software[rows]
        for history, held_value in zip(histories, held_now):
            history[rows, observation_index[rows]] = held_value[rows]
        for key in follow_eci:
            follow_history[key][rows, observation_index[rows]] = follow_eci[key][rows]
        boost_history[rows, observation_index[rows]] = boost_log[rows]
        resources_log = research_log - judgment_log
        for key, values in (("judgment", judgment_log),
                            ("resources", resources_log),
                            ("difficulty", penalty),
                            ("compute", compute_part), ("labor", labor_part),
                            ("ai", resources_log - compute_part - labor_part)):
            factor_history[key][rows, observation_index[rows]] = values[rows]
            last_factors[key][active] = values[active]
        reference_pace_history[rows, observation_index[rows]] = reference_pace[rows]
        observation_index[rows] += 1
        last_pace[active] = pace[active]
        last_reference_pace[active] = reference_pace[active]
        stopped_at[active & diverged] = end[active & diverged]
        t = np.where(diverged, p["years"], end)
    # Months a stopped draw never reached hold its last values.
    unobserved = np.arange(len(workflow_grid))[None, :] >= observation_index[:, None]
    for history, held_value in zip(histories, held_now):
        history[:] = np.where(unobserved, held_value[:, None], history)
    total_budget =(grown(p["years"], compute_rate, compute_late, slow_at) if cpath is None
                    else np.array([np.sum(np.diff(workflow_grid) * 0.5 * (v[1:] + v[:-1])) for v in (
                        np.exp(np.interp(workflow_grid, cpath[0], row)) for row in cpath[1])]))
    # Cumulative, so a month a stopped draw never reached holds its last value.
    follow_history = {k: np.maximum.accumulate(v, axis=1) for k, v in follow_history.items()}
    stopped = workflow_grid[None, :] > stopped_at[:, None]
    pace_history = np.where(stopped, last_pace[:, None], pace_history)
    reference_pace_history = np.where(stopped, last_reference_pace[:, None], reference_pace_history)
    for key in factor_history:
        factor_history[key] = np.where(stopped, last_factors[key][:, None], factor_history[key])
    # Boost observed through each draw's last month, held after it stops.
    held = np.where(stopped, boost_log[:, None], boost_history)
    compute_history = (log_level(workflow_grid[None, :], compute_rate[:, None],
                                 compute_late[:, None], slow_at) if cpath is None
                       else np.array([np.interp(workflow_grid, cpath[0], row)
                                      for row in cpath[1]])) + held
    if cut is not None:
        cut_grid = np.array([np.interp(workflow_grid, cut[0], row) for row in cut[1]])
        compute_history = compute_history - cut_grid
        # The budget reported is the cut one, by months of the grid.
        level = np.exp(compute_history - held)
        total_budget = np.sum(np.diff(workflow_grid) * 0.5 * (level[:, 1:] + level[:, :-1]),
                              axis=1)
    # Retain all draws in each percentile, including slow/non-arriving paths.
    # `direction_ready`: the first grid month direction would be under the bar
    # were coding no gate, which the app pairs coding dates against.
    direction_ready = np.full(n, np.inf)

    def humans_at(j):
        ready = humans(capability_history[:, j], None,
                       realized_history[:, j])[:, 0] <= p["full_human"] / 100
        direction_ready[ready & ~np.isfinite(direction_ready)] = workflow_grid[j]
        hours = humans(capability_history[:, j], workflow_grid[j], realized_history[:, j])
        if p["rsi_autopilot"] and not under_review(workflow_grid[j]):
            hours[events["RSI"] <= workflow_grid[j] + 1e-12] = 0.0
        return hours

    # Per stage, and all stages at their weights: quantiles of the weighted sum,
    # not the weighted sum of quantiles.
    human_quantiles, overall_human_quantiles = [], []
    for j in range(len(workflow_grid)):
        hours = humans_at(j)
        human_quantiles.append(np.quantile(hours, [.1, .5, .9], axis=0))
        overall_human_quantiles.append(np.quantile(hours @ WORKFLOW_WEIGHTS, [.1, .5, .9]))
    # A trailing rate needs a complete measurement window. In particular,
    # there is no observed 1x rate at t=0 to connect to early batch deliveries.
    rate_history = np.full_like(validated_history, np.nan)
    matched_history = np.full_like(validated_history, np.nan)
    for j, year in enumerate(workflow_grid[1:], 1):
        if year < .25 - 1e-12:
            continue
        left = max(0, year - .25)
        k = np.searchsorted(workflow_grid, left + 1e-12, side="right") - 1
        elapsed = year - workflow_grid[k]
        gains = validated_history[:, j] - validated_history[:, k]
        ref_gains = reference_history[:, j] - reference_history[:, k]
        rate_history[:, j] = gains / elapsed / software_rate
        matched_history[:, j] = np.divide(gains, ref_gains,
            out=np.full(n, np.nan), where=ref_gains > 1e-12)
        stopped = workflow_grid[j - 1] >= stopped_at
        rate_history[stopped, j] = rate_history[stopped, j - 1]
        matched_history[stopped, j] = matched_history[stopped, j - 1]
    acceleration_events = {}
    for target in (2, 5):
        crossed = rate_history >= target
        acceleration_events[f"{target}× research progress"] = np.where(
            crossed.any(axis=1), workflow_grid[np.argmax(crossed, axis=1)], np.inf)
    def finite_quantiles(history):
        return np.array([np.quantile(v[np.isfinite(v)], [.1, .5, .9])
                         if np.isfinite(v).any() else [np.nan] * 3 for v in history.T])

    return {
        "params": p, "version": MODEL_VERSION, "onset": onset, "coding_at": coding,
        "direction_ready": direction_ready,
        "events": events, "acceleration_events": acceleration_events,
        "time_origin": "today",
        "compute_limited": last_experiments <= last_labor,
        "budget": total_budget, "allocated": shares[:, None] * total_budget,
        "training_used": training_used,
        "software_log": software, "deployed_log": deployed,
        "deployed_software_log": deployed_software, "fast_software_log": fast_deployed,
        "outcomes": outcomes,
        "workflow_progress": {
            "years": workflow_grid,
            "human_quantiles": np.array(human_quantiles),
            "overall_human_quantiles": np.array(overall_human_quantiles),
            "capability_log": capability_history,
            "rate_quantiles": finite_quantiles(rate_history),
            "cumulative_quantiles": np.quantile(
                validated_history / software_rate[:, None] * 12, [.1, .5, .9], axis=0).T,
            "matched_quantiles": finite_quantiles(matched_history),
            "matched_coverage": np.mean(np.isfinite(matched_history), axis=0),
            "validated_log": validated_history,
            # The algorithmic part of capability_log, as it pays off at scale.
            "software_realized_log": realized_history,
            "validated_baseline_months": validated_history / software_rate[:, None] * 12,
            "pace": pace_history,
            # Share of compute running AI researchers, by month.
            "agent_share": agent_share_history,
            # Log compute relative to today, post-RSI boost included.
            "compute_log": compute_history,
            "pace_factors": factor_history,
            "reference_pace": reference_pace_history,
            "reference_log": reference_history,
            "rate": rate_history,
            "matched": matched_history,
            # A follower's cumulative ECI from each inflow channel, by month.
            "follow_eci": follow_history,
        },
        "progress_multiple": delivered_rate,
        "compute_matched_advantage": advantage,
        "draws": {"taste_slope": taste_slope, "difficulty": beta,
                  "judgment_drift": drift, "substitution": rho,
                  "ceiling_oom": ceiling / np.log(10), "scale_dependent": scale_share,
                  "fast_share": 100 * fast_fraction,
                  "scale_lag_oom": scale_lag / np.log(10)},
        # Each draw's log compute growth a year before and after `slow_at`;
        # its compute is exp(log_level(t, rate, late, slow_at)) x today's.
        "compute": {"rate": compute_rate, "late": compute_late, "slow_at": slow_at},
        # Each draw's log software and capability growth a year today: a
        # follower's clock for reading this run's hours (`FOLLOWER_KEYS`).
        "software_rate": software_rate, "capability_rate": baseline_capability_rate,
        "stopped_at": stopped_at,
    }


def progress_years(result, base_rate, window=1.0, level=None):
    """Per draw, the years of progress at `base_rate` (log capability a year,
    or `level`'s units a year) its deployed capability makes in the `window`
    years after RSI: Forethought's "years of AI progress compressed into one
    year". `level` (draws x months) replaces the capability path, as when it
    is read as ECI. NaN where RSI never comes or the window runs past the
    horizon; +inf where the draw diverges inside it.
    """
    wp = result["workflow_progress"]
    grid = wp["years"]
    cap = wp["capability_log"] if level is None else level
    start = result["events"]["RSI"]
    end = start + window
    out = np.full(len(start), np.nan)
    for i in np.flatnonzero(np.isfinite(start) & (end <= grid[-1] + 1e-9)):
        if result["stopped_at"][i] <= end[i]:
            out[i] = np.inf
        else:
            out[i] = (np.interp(end[i], grid, cap[i])
                      - np.interp(start[i], grid, cap[i])) / base_rate
    return out


def cdf(samples, grid):
    """CDF over all draws, including +inf (not reached) in the denominator."""
    return np.searchsorted(np.sort(samples), grid, side="right") / len(samples)


def quantile(samples, q, horizon=np.inf):
    """Empirical inverse CDF, preserving censored probability mass."""
    value = np.sort(samples)[max(0, int(np.ceil(q * len(samples))) - 1)]
    return float(value) if value <= horizon else np.inf
