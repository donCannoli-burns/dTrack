# dTrack

> **Original project and credit:** [Prusias-kol/pTrack](https://github.com/Prusias-kol/pTrack) by Prusias-kol. This is a separate experimental fork maintained at [donCannoli-burns/dTrack](https://github.com/donCannoli-burns/dTrack).
>
> **EXPERIMENTAL — USE AT YOUR OWN RISK.** This fork is not guaranteed to be stable or safe. Review settings and scripts before running them, especially commands that spend turns, change inventory, use the mall, PvP, or ascend. The upstream author is not responsible for modifications in this fork.

**Additional original-code credit:** The Dictator's `ProfitTracking.ash` and `DicsLibrary.ash`, and Thoth19's `TimeTracking.ash`, provide much of the tracking implementation. These credits are retained from upstream.

This is a gCLI wrapper for profit/time tracking, letting you mark breakpoints, view a daily list, and compare gains and losses between breakpoints.

## Install, update, and remove

Run these commands in the **KoLmafia gCLI** (not your operating system's Git shell).

**Install**
```
git checkout https://github.com/donCannoli-burns/dTrack main
```

**Update**
```
git update donCannoli-burns-dTrack-main
```

**Remove this fork**
```
git delete donCannoli-burns-dTrack-main
```

If you previously installed the original upstream project, use `git list` to confirm its installed project ID before optionally deleting it with `git delete Prusias-kol-pTrack-main`. Avoid keeping upstream and fork versions installed simultaneously when they supply the same script filenames.

## Dependencies

Two declared dependencies: [libraryaddict/KolItemPrices](https://github.com/libraryaddict/KolItemPrices) and [donCannoli-burns/don-ash-lib](https://github.com/donCannoli-burns/don-ash-lib), both listed in [`kolmafia/dependencies.txt`](kolmafia/dependencies.txt).

`ProfitTracking.ash` now imports `don_track_compat.ash` from `don-ash-lib` instead of the bundled `DicsLibrary.ash`. This trimmed adapter preserves the original item-counting, user price overrides, special item valuation, historical-price logic, and Irrat price support that pTrack uses, while excluding unrelated DicsLibrary gameplay helpers. Original credit remains with The Dictator and upstream pTrack. The original file is retained in Git history. **Static source checks passed; runtime `verify ptrack` still needs to be performed in KoLmafia before relying on reports.**

## How to use

The existing command remains `ptrack`.

```
ptrack help
ptrack add <breakpoint name>
ptrack list
ptrack compare <bp1> <bp2>
ptrack recap
```

- `ptrack add` creates a breakpoint.
- `ptrack list` lists today's breakpoints (or yesterday's if none have been set today).
- `ptrack compare` compares two breakpoints; the legacy `dcompare` variant provides an item profit/loss breakdown.
- `ptrack recap` compares the listed breakpoints.

## Breakfast tracking

To capture breakfast profits, invoke `ptrack breakfast` instead of the usual KoLmafia breakfast command. To run it during login, disable the default breakfast checkbox, then set **KoLmafia → Preferences → Automation → On Login** to:

```
ptrack breakfast
```

## In development (inherited upstream roadmap)

- View previous days.
- Exclude outlier items from profit comparisons.
- Compare across days.

## Hardened staged absorption (2026-10-29)

This suite is licensed **GPL-3.0**, with substantial upstream work by The Dictator and Thoth19. Its six identified scripts and the `relay_ptrack.js` entrypoint are staged under [don-ash-lib/dtrack-suite](https://github.com/donCannoli-burns/don-ash-lib/tree/main/dtrack-suite) as an **isolated, non-installable source shelf**, preserving the GPL license. The root don-ash-lib manifest still installs only the master ASH library; it does **not** make this staged suite available to KoLmafia.

This dTrack repository remains the required **active** tracking dependency of dLooper until runtime compilation, relay UI, existing saved reports, and valuation regression checks pass. Hardening here has removed implicit storage pull-all, bounded duplicate names, guarded token pricing and path construction, and added an approval gate before Screege redemption. See the staged suite README for detailed limitations. **Do not delete dTrack yet.**


## Performance helpers (experimental branch)

Native performance improvements do **not** need Python or NumPy:

- ASH checkpoint inventory/net-worth capture now computes each item's count once per pass.
- ASH inventory comparisons iterate over recorded snapshot items instead of every possible game item, and compute the valuation once per changed item before sorting. The descriptive list is limited to ten losses and ten gains.
- The JavaScript `graphWithItems` path reuses each item's price during a single graph generation run. This avoids repeated mall/history lookups across days; prices are recalculated on the next run.

### Optional offline NumPy analyzer

`tools/dtrack_numpy.py` reads **existing** KoLmafia checkpoint files without contacting the game, updating properties, touching inventory, or writing to the data directory. It vectorizes adventure, meat, and historical item-value deltas; produces JSON for plotting or other scripts; and labels gaps when a historical net-worth checkpoint is absent. It does **not** accelerate live ASH commands, and NumPy may not provide an advantage for a short history.

From a checkout of this repository, using an isolated environment:

```sh
python3 -m venv .venv-dtrack
. .venv-dtrack/bin/activate
python -m pip install -r tools/requirements-optional.txt
python tools/dtrack_numpy.py \
  --data-dir "$HOME/.kolmafia/data/Profit Tracking/YOUR_CHARACTER" \
  > dtrack-history.json
python -m unittest discover -s tools -p 'test_*.py'
```

Replace `YOUR_CHARACTER` with the directory name used by KoLmafia. For a containerized KoLmafia installation, use its **mounted** `data/Profit Tracking/<character>` directory. Existing checkpoint values are preserved; the helper never fetches fresh mall prices. Treat intervals crossing ascensions or other counter resets cautiously.

**Verification status:** three offline NumPy fixture tests are included, but have not yet been executed against the committed branch. Native ASH compilation and live KoLmafia runtime behavior have not been verified. Benchmark native commands against the original before claiming a measured speedup.


### Diagnosing the actual item-count bottleneck

The NumPy analyzer runs offline and **does not accelerate item counting in KoLmafia**. The compatibility library's `total_amount(item)` checks many inventory locations and iterates familiars for each item; `LogItems` and `LogNetworthCheckpoint` call it over `$items[]`. Before changing accounting semantics, use the **read-only** count probe:

```text
verify ptrackSuite/dtrack_count_probe.ash
call ptrackSuite/dtrack_count_probe.ash bulk
call ptrackSuite/dtrack_count_probe.ash parity
```

`bulk` reads each current collection map once and counts equipped/terrarium/campground items separately. `parity` additionally runs the original `total_amount` against every item and reports any discrepancies (first 12 shown), plus wall-clock milliseconds for each approach. **Do not use the bulk algorithm in production unless mismatch count is zero and the counts agree across representative character states.** In particular, the current installed `don_track_compat.ash` dependency must compile before this probe will work.

The probe deliberately skips `refresh shop`, `refresh storage`, and `refresh inv`; it is measuring *cached item-count enumeration*, not KoLmafia's network-refresh latency. The production `ptrack add` path includes those refreshes and separate item valuation; benchmark them separately before making a speedup claim. Neither probe mode writes checkpoint files, changes preferences, spends turns, or intentionally refreshes the game state.
