import sys, time, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
from streamlit.testing.v1 import AppTest
import streamlit.testing.v1.app_test as _a, streamlit.testing.v1.local_script_runner as _l
from streamlit.runtime.scriptrunner.script_cache import ScriptCache
from pyinstrument import Profiler
_c = ScriptCache(); _a.ScriptCache = lambda: _c; _l.ScriptCache = lambda: _c
LSR = _l.LocalScriptRunner
_orig = LSR._run_script
PROF = {}
def _wrapped(self, rerun_data):
    p = Profiler(interval=0.002); p.start()
    try: return _orig(self, rerun_data)
    finally:
        p.stop(); PROF['last'] = p
LSR._run_script = _wrapped
slug, which = sys.argv[1], sys.argv[2]
at = AppTest.from_file(os.path.join(ROOT, "visualize_projection.py"), default_timeout=300)
at.query_params["tab"] = slug
at.run()
if which == "warm":
    at.run()
elif which.startswith("set:"):
    _, kind, key, val = which.split(":")
    at.run()
    w = getattr(at, kind)(key=key)
    t = time.perf_counter(); w.set_value(type(w.value)(float(val)) if not isinstance(w.value, bool) else val == "1").run()
    print("rerun after change:", round(time.perf_counter() - t, 2), "s")
assert not list(at.exception), list(at.exception)[0]
print(PROF['last'].output_text(unicode=False, color=False, show_all=False, timeline=False)[:int(sys.argv[3]) if len(sys.argv) > 3 else 6000])
