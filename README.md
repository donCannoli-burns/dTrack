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

One declared dependency: [libraryaddict/KolItemPrices](https://github.com/libraryaddict/KolItemPrices) (listed in [`kolmafia/dependencies.txt`](kolmafia/dependencies.txt)).

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
