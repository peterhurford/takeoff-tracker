import sys, time, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
t0 = time.perf_counter()
from streamlit.testing.v1 import AppTest
import streamlit.testing.v1.app_test as _a, streamlit.testing.v1.local_script_runner as _l
from streamlit.runtime.scriptrunner.script_cache import ScriptCache
_c = ScriptCache(); _a.ScriptCache = lambda: _c; _l.ScriptCache = lambda: _c
slug = sys.argv[1]
at = AppTest.from_file(os.path.join(ROOT, "visualize_projection.py"), default_timeout=300)
at.query_params["tab"] = slug
out = {"tab": slug}
for name in ("cold", "warm1", "warm2"):
    t = time.perf_counter(); at.run(); out[name] = round(time.perf_counter() - t, 2)
assert not list(at.exception), list(at.exception)[0]
charts = at.get("plotly_chart")
sizes = [el.proto.ByteSize() for el in charts]
out["charts"] = len(charts); out["chart_MB"] = round(sum(sizes) / 1e6, 2); out["max_chart_MB"] = round(max(sizes or [0]) / 1e6, 2)
out["widgets"] = sum(len(at.get(k)) for k in ("slider","number_input","selectbox","checkbox","radio","toggle","multiselect","select_slider","button","date_input"))
print(json.dumps(out))
