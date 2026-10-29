// Hardened read-only coinmaster valuation; derived from Prusias-kol/pTrack.
// GPL-3.0 licensed component. Experimental, use at your own risk.
"use strict";

const { Coinmaster, Item, isAccessible, sellsItem, mallPrice, sellPrice, printHtml } = require("kolmafia");

function escapeHtml(value) {
    return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
function numberText(value) {
    if (!Number.isFinite(value)) return "N/A";
    return Math.round(value).toLocaleString("en-US");
}

function main() {
    const groups = new Map();
    const available = Coinmaster.all().filter(cm =>
        cm !== Coinmaster.get("none") && cm.availableTokens > 0 && isAccessible(cm));
    for (const cm of available) {
        const key = String(cm.token);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(cm);
    }
    let total = 0;
    for (const [token, coinmasters] of groups) {
        printHtml("<b>" + escapeHtml(token) + "</b>");
        let bestGroupValue = 0;
        for (const cm of coinmasters) {
            let best = null;
            for (const it of Item.all()) {
                if (!sellsItem(cm, it)) continue;
                const price = sellPrice(cm, it);
                if (!(price > 0)) continue; // No divide-by-zero or invalid token prices.
                const mall = mallPrice(it);
                if (!(mall > 0)) continue;
                const value = 0.9 * mall / price;
                if (!Number.isFinite(value) || value <= 0) continue;
                if (!best || value > best.value) best = { item: it, value };
            }
            if (!best) {
                printHtml("No priced offer for " + escapeHtml(cm) + ".");
                continue;
            }
            const maxValue = cm.availableTokens * best.value;
            if (Number.isFinite(maxValue)) bestGroupValue = Math.max(bestGroupValue, maxValue);
            printHtml("For " + escapeHtml(cm) + ": " +
                escapeHtml(cm.availableTokens) + " tokens; best priced item " +
                escapeHtml(best.item) + " at approximately " + numberText(best.value) + " Meat/token.");
        }
        total += bestGroupValue;
        printHtml("<b>Estimated token-group maximum: " + numberText(bestGroupValue) + " Meat</b>");
    }
    printHtml("<b>Estimated total potential value: " + numberText(total) + " Meat</b>");
    printHtml("This is an estimate, not a guaranteed sale price.");
}

module.exports.main = main;
