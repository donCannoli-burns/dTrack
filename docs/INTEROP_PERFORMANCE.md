# dTrack interoperability and acceleration decision record

Status: exploratory, not a runtime integration.

## Existing prototypes

- Go: [don-ash-lib/kolmafia-ash-go](https://github.com/donCannoli-burns/don-ash-lib/tree/main/kolmafia-ash-go) is a Go 1.20+ client of KoLmafia's Browser JSON API. Its source implements `Client.Batch`, `PasswordProvider`, and per-function `CallPolicy` checks (`AllowOnly` / `Deny`). The standard-library runtime can be an optional read-only adapter.
- C++20: [don-ash-lib/kolmafia-ash-cpp20](https://github.com/donCannoli-burns/don-ash-lib/tree/main/kolmafia-ash-cpp20) is a libcurl + Boost.JSON client of the same API. It uses a callback for the session hash and supports batched requests. Its generic `Client::call` is unrestricted by itself.
- NumPy: `tools/dtrack_numpy.py` handles historical checkpoint arrays **offline**. No KoLmafia session or Browser JSON API access is required.

Neither Go nor C++ prototype currently makes arbitrary functions defined in third-party `.ash` libraries callable from outside KoLmafia. More importantly, these are **clients** of KoLmafia's runtime, not a fast foreign-function interface that lets ASH directly call native code.

## Performance and authority decisions

1. Keep normal `ptrack` commands within ASH/KoLmafia. Existing native optimizations should first be validated by KoLmafia compilation, equivalence fixtures, and before/after timing.
2. For large saved-history processing, favor direct filesystem reads with a separate offline analytics process. No session credentials or gameplay calls should be required. Benchmark NumPy, pure-Python, and a Go implementation before assuming which is fastest at real checkpoint sizes.
3. If live external monitoring is justified, prefer a separate **read-only** Go adapter, with a strict, explicitly documented `ash.AllowOnly(...)` function set, bounded batch sizes, request timeouts, and a host-supplied ephemeral PasswordProvider. Never expose unrestricted generic `Call`/arbitrary ASH source through dTrack. Do not log/persist session hashes. Read-only file processing needs none of these credentials.
4. Consider pybind11/C++20 solely for an independently benchmarked CPU-bound numerical kernel. Do not infer that `torch.compile` automatically compiles arbitrary NumPy code to C++/CUDA; that workflow would require explicit PyTorch-compatible operations, and is unnecessary for the current script.
5. Avoid a second source of truth for historical item valuation: saved checkpoint values are authoritative historical data; external analytics must not silently revalue old checkpoints with today's prices.
6. Do not add the Go or C++ binding to `kolmafia/dependencies.txt`: those are external prototype clients, not installable ASH dependencies. Preserve dTrack's ordinary install/update path.

## Go packaging caveat

The source currently lives under `don-ash-lib/kolmafia-ash-go`, but its `go.mod` declares `module github.com/doncannoli-burns/kolmafia-ash-go`. At inspection time, that standalone repository path was not found. Before `go get` integration, either publish a corresponding standalone module, set up a deliberate subdirectory module layout with the appropriate module path, or use an explicit local `replace` directive in an isolated adapter build. Do not assume the README's example import resolves remotely.

## Required gates before any runtime integration

- Compare native ASH outputs (totals, overrides, blacklist, top gains/losses) against the unoptimized baseline on zero, small, sparse, and typical saved snapshots.
- Validate `verify ptrack` and resolve `don_track_compat.ash` compilation errors before measuring real command performance.
- Benchmark `ptrack compare`, `ptrack dcompare`, `ptrack graphWithItems`, and offline history analytics separately, with repeated runs and consistent price caches.
- Validate the optional NumPy tests independently. Source inspection is **not** execution evidence.
- For any future Go relay interaction: fake-server policy/transport tests first, then separately approved, bounded, read-only local KoLmafia tests. No live call has been performed for this design note.

Decision: keep Go/C++ bindings optional and out of the live `ptrack` code path until a measured bottleneck justifies them.
