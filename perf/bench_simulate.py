"""Time `takeoff_model.simulate` alone at the app's size (1,000 draws, 14 years).

    python perf/bench_simulate.py
"""
import os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import takeoff_model as tm

p = dict(tm.DEFAULTS); p["years"] = 14.0
for n in (50, 500, 1000, 2000):
    np.random.seed(0)
    t = time.perf_counter(); tm.simulate(p, n=n)
    print(f"n={n:5d}  {time.perf_counter() - t:5.2f}s")
