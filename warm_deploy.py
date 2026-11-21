"""Warm the deployed app after a push, so the first real visitor does not pay
for numba compiling the step loop and empty caches (a minute or more on Cloud).

    git push && python warm_deploy.py     # waits for the redeploy, then warms
    python warm_deploy.py --now           # one warm run, no waiting

It holds a Streamlit session open on the Takeoff tab; Cloud's redeploy shows up
as the server dropping the connection or a `script_changed_on_disk` event, and
the warmer then reconnects and runs the tab once more. Exits 0 when that run
finishes with no exception on the page, 1 otherwise. With no signal by
`--wait`, it warms anyway.
"""
import argparse
import asyncio
import http.cookiejar
import sys
import time
import urllib.request

import websockets
from streamlit.proto import BackMsg_pb2, ForwardMsg_pb2

APP_URL = "https://takeoff-tracker.streamlit.app/"


def _cookies(url):
    """Cookies from Streamlit Cloud's redirect handshake, which the websocket
    needs; without them every request bounces to /-/login."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.open(url, timeout=120).read()
    return "; ".join(f"{c.name}={c.value}" for c in jar)


async def _connect(url):
    host = url.split("://", 1)[1].rstrip("/")
    return await websockets.connect(
        f"wss://{host}/~/+/_stcore/stream", subprotocols=["streamlit"],
        max_size=None, open_timeout=120,
        additional_headers={"Cookie": _cookies(url), "Origin": url.rstrip("/")})


async def _run(ws, tab, timeout):
    """Rerun `tab` on `ws` until its script finishes: (status, exceptions, seconds)."""
    started = time.time()
    msg = BackMsg_pb2.BackMsg()
    msg.rerun_script.query_string = f"tab={tab}"
    await ws.send(msg.SerializeToString())
    errors = []
    while True:
        fwd = ForwardMsg_pb2.ForwardMsg()
        fwd.ParseFromString(await asyncio.wait_for(ws.recv(), timeout=timeout))
        kind = fwd.WhichOneof("type")
        if kind == "delta" and fwd.delta.new_element.WhichOneof("type") == "exception":
            errors.append(fwd.delta.new_element.exception.message)
        elif kind == "script_finished":
            status = ForwardMsg_pb2.ForwardMsg.ScriptFinishedStatus.Name(
                fwd.script_finished)
            if status != "FINISHED_FRAGMENT_RUN_SUCCESSFULLY":
                return status, errors, time.time() - started


async def _await_redeploy(ws, wait):
    """True once the server drops `ws` or reports the script changed on disk."""
    try:
        async with asyncio.timeout(wait):
            while True:
                fwd = ForwardMsg_pb2.ForwardMsg()
                fwd.ParseFromString(await ws.recv())
                if (fwd.WhichOneof("type") == "session_event"
                        and fwd.session_event.HasField("script_changed_on_disk")):
                    return True
    except websockets.ConnectionClosed:
        return True
    except TimeoutError:
        return False


async def _connect_retrying(url, until):
    """Connect, retrying while the app restarts, until the `until` deadline."""
    while True:
        try:
            return await _connect(url)
        except Exception:
            if time.time() > until:
                raise
            await asyncio.sleep(10)


async def _warm(args):
    ws = await _connect_retrying(args.url, time.time() + args.wait)
    if not args.now:
        print(f"waiting up to {args.wait:.0f}s for the redeploy...", flush=True)
        status, _, secs = await _run(ws, args.tab, args.timeout)
        print(f"  current version: {status} in {secs:.0f}s", flush=True)
        seen = await _await_redeploy(ws, args.wait)
        await ws.close()
        # A push touching no file the app imports changes nothing it runs, so
        # Cloud neither restarts nor signals; warm anyway, which costs seconds.
        print("redeploy seen; warming" if seen else
              "no redeploy seen (no app file changed?); warming anyway", flush=True)
        ws = await _connect_retrying(args.url, time.time() + args.wait)
    async with ws:
        status, errors, secs = await _run(ws, args.tab, args.timeout)
    print(f"{args.tab}: {status} in {secs:.0f}s"
          + "".join(f"\n  exception: {e}" for e in errors))
    return 0 if status == "FINISHED_SUCCESSFULLY" and not errors else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--url", default=APP_URL)
    ap.add_argument("--tab", default="takeoff")
    ap.add_argument("--now", action="store_true", help="warm once without waiting")
    ap.add_argument("--wait", type=float, default=600,
                    help="seconds to wait for the redeploy")
    ap.add_argument("--timeout", type=float, default=600,
                    help="seconds to wait between messages of one run")
    sys.exit(asyncio.run(_warm(ap.parse_args())))


if __name__ == "__main__":
    main()
