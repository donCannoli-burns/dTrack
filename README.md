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
