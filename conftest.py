"""Pytest configuration — all of it is about test *speed*.

Almost all of the suite's time is in test_integration.py's AppTest cases.
Three things keep it down:

1. Streamlit rebuilds a ``ScriptCache`` on every ``AppTest.run()`` — once in
   ``AppTest._run()`` and again in ``LocalScriptRunner.__init__`` — so the
   app was re-read, AST-rewritten by ``magic.add_magic`` and recompiled
   for each of the ~300 runs the suite does. That was ~0.5s of the ~0.7s a run
   cost. One process-wide cache fixes it; the bytecode is still exec'd into a
   fresh module every run, so per-run isolation is unchanged.
2. Sampling the production count of fan-chart trajectories per render was most of what remained.
   ``_VP_SAMPLES`` turns that down for tests only — see ``N_SAMPLES`` in
   visualize_projection.py for why nothing asserted on depends on it.
3. The cases are independent, so they parallelize — pytest.ini runs them under
   pytest-xdist.
"""

import os

import streamlit.testing.v1.app_test as _app_test
import streamlit.testing.v1.local_script_runner as _local_script_runner
from streamlit.runtime.scriptrunner.script_cache import ScriptCache as _ScriptCache

# ── 1. One bytecode cache for the whole session ──────────────────────────
_SHARED_SCRIPT_CACHE = _ScriptCache()
_app_test.ScriptCache = lambda: _SHARED_SCRIPT_CACHE
_local_script_runner.ScriptCache = lambda: _SHARED_SCRIPT_CACHE

# ── 2. Smaller Monte Carlo under test ────────────────────────────────────
os.environ.setdefault("_VP_SAMPLES", "400")
# xdist already fills the cores; one numba thread per worker avoids oversubscribing them.
os.environ.setdefault("NUMBA_NUM_THREADS", "1")
