script "dtrack_count_probe";
import <don_track_compat.ash>;

// Diagnostic only: do not replace dTrack's production counter until parity
// has been established against actual character configurations.
//
// This probe does NOT refresh inventories, query mall prices, write files,
// change preferences, or take any gameplay action.

void count_add(int[item] totals, int[item] source) {
    foreach it, amount in source {
        if (amount != 0)
            totals[it] += amount;
    }
}

int[item] count_bulk() {
    int[item] totals;
    count_add(totals, get_inventory());
    count_add(totals, get_closet());
    count_add(totals, get_storage());
    count_add(totals, get_display());
    count_add(totals, get_shop());

    if (get_property_bool("autoSatisfyWithStash"))
        count_add(totals, get_stash());

    // Equipment is not included in get_inventory(). Enumerate slots once,
    // instead of probing equipped_amount() for every known item.
    foreach s in $slots[] {
        item it = equipped_item(s);
        if (it != $item[none])
            totals[it] += 1;
    }

    // Preserve legacy treatment of inactive terrarium familiar equipment.
    foreach f in $familiars[] {
        if (have_familiar(f) && my_familiar() != f) {
            item it = familiar_equipped_equipment(f);
            if (it != $item[none])
                totals[it] += 1;
        }
    }

    // Match the original special campground accounting, not every campground
    // item (otherwise unrelated campground items could be double-counted).
    boolean[item] garden = $items[Peppermint Pip Packet, packet of dragon's teeth, packet of beer seeds, packet of winter seeds, packet of thanksgarden seeds, packet of tall grass seeds, packet of mushroom spores];
    boolean[item] workshed = $items[warbear jackhammer drill press, warbear auto-anvil, warbear induction oven, warbear chemistry lab, warbear high-efficiency still, warbear lp-rom burner, spinning wheel, snow machine, Asdon Martin keyfob (on ring), portable mayo clinic, little geneticist dna-splicing lab, diabolic pizza cube];
    int[item] campground = get_campground();
    foreach it, amount in campground {
        if ((garden contains it || workshed contains it) && amount != 0)
            totals[it] += amount;
    }
    return totals;
}

void main(string mode) {
    if (mode != "bulk" && mode != "parity") {
        print("dTrack counter probe (cached reads only)", "teal");
        print("call ptrackSuite/dtrack_count_probe.ash bulk");
        print("call ptrackSuite/dtrack_count_probe.ash parity");
        print("bulk: count current items from collection maps.");
        print("parity: also run legacy per-item counter, compare outputs.");
        print("Neither mode refreshes collections or changes game state.");
        return;
    }

    int started = now_to_int();
    int[item] bulk = count_bulk();
    int bulk_ms = now_to_int() - started;
    print("BULK: " + count(bulk) + " distinct item keys, " + bulk_ms + " ms", "teal");

    if (mode == "bulk")
        return;

    started = now_to_int();
    int[item] legacy;
    foreach it in $items[] {
        int n = total_amount(it);
        if (n != 0)
            legacy[it] = n;
    }
    int legacy_ms = now_to_int() - started;
    print("LEGACY: " + count(legacy) + " distinct item keys, " + legacy_ms + " ms", "teal");

    boolean[item] keys;
    foreach it in bulk
        keys[it] = true;
    foreach it in legacy
        keys[it] = true;
    int mismatches = 0;
    foreach it in keys {
        if (bulk[it] != legacy[it]) {
            mismatches += 1;
            if (mismatches <= 12)
                print("MISMATCH: " + it + " bulk=" + bulk[it] + " legacy=" + legacy[it], "red");
        }
    }

    print("PARITY: mismatched item counts=" + mismatches +
        " (first 12 shown), bulk=" + bulk_ms +
        " ms, legacy=" + legacy_ms + " ms",
        mismatches == 0 ? "green" : "red");
    if (mismatches != 0)
        print("Do NOT replace production total_amount until mismatches are explained.", "red");
}
