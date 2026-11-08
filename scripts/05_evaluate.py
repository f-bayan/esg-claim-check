import csv
import importlib
import json
import random
from collections import Counter
from math import comb

from common import LABELS, ROOT, load_items
from mode_c import decide

RULE_ITEMS = {"prosus_10", "adyen_03", "postnl_05", "asml_02", "aholddelhaize_04", "prosus_24", "prosus_24_number"}
PILOT = {"adyen_01", "postnl_01", "zalando_03", "heineken_01_unit", "kpn_04"}
N_BOOT = 2000
run = importlib.import_module("04_run_llm")
REPLIES = {}


def load_system(path, items, name, check_hash):
    preds = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if check_hash:
            system = run.system_prompt(r["mode"])
            if r["item_hash"] != run.item_hash(system, items[r["item_id"]]):
                raise SystemExit(f"{path.name}: {r['item_id']} was run with another prompt or evidence. Run 04 again for it.")
        REPLIES[(name, r["item_id"])] = r["raw"]
        pred = r["pred"]
        if r["mode"] == "C":
            try:
                facts = json.loads(r["raw"])["facts"]
                pred = decide(facts, items[r["item_id"]]["evidence"])[0] if isinstance(facts, list) else "INVALID"
            except (ValueError, KeyError, TypeError):
                pred = "INVALID"
        preds[r["item_id"]] = pred
    return preds


def systems(items):
    out = {"baseline": {r["item_id"]: r["pred"] for r in csv.DictReader(open(ROOT / "results" / "baseline.csv", encoding="utf-8"))}}
    for model in ["gpt-6-luna", "gpt-6.1-sol"]:
        for mode in "ABC":
            name = f"{model} {mode}"
            out[name] = load_system(ROOT / "results" / "llm" / f"{model}__{mode}.jsonl", items, name, True)
    for mode in "ABC":
        name = f"gpt-6-luna {mode} (v1)"
        out[name] = load_system(ROOT / "results" / "llm" / "v1" / f"gpt-6-luna__{mode}.jsonl", items, name, False)
    return out


def scores(ids, gold, pred):
    acc = sum(pred[i] == gold[i] for i in ids) / len(ids)
    per = {}
    for lab in LABELS:
        tp = sum(pred[i] == lab and gold[i] == lab for i in ids)
        n_pred = sum(pred[i] == lab for i in ids)
        n_gold = sum(gold[i] == lab for i in ids)
        p = tp / n_pred if n_pred else 0.0
        r = tp / n_gold if n_gold else None
        f = 2 * p * r / (p + r) if r and p + r else (0.0 if r is not None else None)
        per[lab] = {"p": p, "r": r, "f1": f, "n": n_gold}
    f1s = [v["f1"] for v in per.values() if v["f1"] is not None]
    return {"acc": acc, "macro_f1": sum(f1s) / len(f1s), "per": per, "n": len(ids)}


def boot_ci(ids, gold, pred, cluster, key="macro_f1"):
    rng = random.Random(0)
    groups = {}
    for i in ids:
        groups.setdefault(cluster[i], []).append(i)
    keys = sorted(groups)
    vals = []
    for _ in range(N_BOOT):
        s = [i for _ in keys for i in groups[rng.choice(keys)]]
        vals.append(scores(s, gold, pred)[key])
    vals.sort()
    return vals[int(0.025 * N_BOOT)], vals[int(0.975 * N_BOOT) - 1]


def mcnemar(ids, gold, a, b):
    only_a = sum(a[i] == gold[i] and b[i] != gold[i] for i in ids)
    only_b = sum(b[i] == gold[i] and a[i] != gold[i] for i in ids)
    n = only_a + only_b
    if n == 0:
        return only_a, only_b, 1.0
    k = min(only_a, only_b)
    p = min(1.0, 2 * sum(comb(n, j) for j in range(k + 1)) / 2 ** n)
    return only_a, only_b, p


def paired(items, gold, pred):
    groups = {}
    for i, it in items.items():
        if it["source"] == "synthetic":
            groups.setdefault(it["source_claim_id"], []).append(i)
    pairs = [(s, p) for s, ps in groups.items() for p in ps]
    both = sum(pred[s] == gold[s] and pred[p] == gold[p] for s, p in pairs)
    full = sum(pred[s] == gold[s] and all(pred[p] == gold[p] for p in ps) for s, ps in groups.items())
    return both / len(pairs), full / len(groups), len(pairs), len(groups)


def pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}"


def main():
    raw = load_items()
    src = {r["item_id"]: r["source_claim_id"] for r in csv.DictReader(open(ROOT / "data" / "perturbed.csv", encoding="utf-8"))}
    items = {}
    for it in raw:
        it["source_claim_id"] = src.get(it["item_id"])
        items[it["item_id"]] = it
    gold = {i: it["label"] for i, it in items.items()}
    cluster = {i: it["source_claim_id"] or i for i, it in items.items()}
    systs = systems(items)
    for name, p in systs.items():
        missing = set(items) - set(p)
        if missing:
            raise SystemExit(f"{name} is missing {len(missing)} items")
    main_names = [n for n in systs if "(v1)" not in n]
    all_ids = sorted(items)
    real = [i for i in all_ids if items[i]["source"] == "real"]
    synth = [i for i in all_ids if items[i]["source"] == "synthetic"]
    no_rule = [i for i in all_ids if i not in RULE_ITEMS]
    kinds = ["number", "direction", "year", "unit", "scope", "drop_row"]

    L = ["# Results", "", f"{len(all_ids)} items: {len(real)} real claims and {len(synth)} synthetic items. "
         "INVALID counts as wrong. Mode C labels are recomputed from the stored replies with the current mode_c.py. "
         f"95% intervals use {N_BOOT} bootstrap resamples (seed 0) that draw whole source claims, so a real claim and its synthetic versions stay together. "
         "p-values use the exact McNemar test and are not corrected for the number of comparisons. "
         "The models reject temperature 0, so they run at their default temperature. Each system was run three times. The main tables use run 1, and the section Repeated runs shows all three.", ""]

    L += ["## Overall", "", "| system | accuracy | macro-F1 | 95% CI | real macro-F1 | 95% CI | synthetic accuracy | INVALID |", "|---|---|---|---|---|---|---|---|"]
    for n in main_names:
        p = systs[n]
        a, r, s = scores(all_ids, gold, p), scores(real, gold, p), scores(synth, gold, p)
        lo, hi = boot_ci(all_ids, gold, p, cluster)
        rlo, rhi = boot_ci(real, gold, p, cluster)
        inv = sum(p[i] == "INVALID" for i in all_ids)
        L.append(f"| {n} | {pct(a['acc'])} | {pct(a['macro_f1'])} | {pct(lo)} to {pct(hi)} | {pct(r['macro_f1'])} | {pct(rlo)} to {pct(rhi)} | {pct(s['acc'])} | {inv} |")
    L += ["", "The synthetic items contain no CONSISTENT claims, so only accuracy is shown for them.", ""]

    L += ["## Recall per label, real claims", "", "| system | CONSISTENT (n=%d) | INCONSISTENT (n=%d) | CANNOT_VERIFY (n=%d) |" % tuple(
        sum(gold[i] == lab for i in real) for lab in LABELS), "|---|---|---|---|"]
    for n in main_names:
        per = scores(real, gold, systs[n])["per"]
        L.append(f"| {n} | " + " | ".join(f"{sum(systs[n][i] == lab and gold[i] == lab for i in real)}/{per[lab]['n']}" for lab in LABELS) + " |")
    L.append("")

    L += ["## Accuracy per perturbation type", "", "| system | " + " | ".join(f"{k} (n={sum(items[i]['perturbation'] == k for i in synth)})" for k in kinds) + " |",
          "|---" * (len(kinds) + 1) + "|"]
    for n in main_names:
        p = systs[n]
        cells = []
        for k in kinds:
            ids = [i for i in synth if items[i]["perturbation"] == k]
            cells.append(f"{sum(p[i] == gold[i] for i in ids)}/{len(ids)}")
        L.append(f"| {n} | " + " | ".join(cells) + " |")
    L.append("")

    L += ["## Paired check", "", "A pair is an original CONSISTENT claim and one of its synthetic versions. "
          "Both right means the system labels both correctly. All right means the original and all its versions are correct.", "",
          "| system | both right (pairs) | all right (claims) |", "|---|---|---|"]
    for n in main_names:
        b, f, npairs, ng = paired(items, gold, systs[n])
        L.append(f"| {n} | {pct(b)} (n={npairs}) | {pct(f)} (n={ng}) |")
    L.append("")

    L += ["## Items the v2 prompt changes were aimed at", "", f"Prompt v2 was written after the v1 run. These {len(RULE_ITEMS)} items are the ones its changes were aimed at, "
          "so they are shown separately and macro-F1 without them is given. "
          "The v1 rows use the v1 replies with the current mode_c.py, which fixed a unit bug. Stored v1 labels differ for adyen_01_unit, adyen_02_unit and adyen_04_unit. "
          f"The 5 pilot items ({', '.join(sorted(PILOT))}) were also seen during prompt writing and are still scored.", "", "| system | " + " | ".join(sorted(RULE_ITEMS)) + " | macro-F1 without them |", "|---" * (len(RULE_ITEMS) + 2) + "|"]
    for n in systs:
        p = systs[n]
        L.append(f"| {n} | " + " | ".join("ok" if p[i] == gold[i] else p[i] for i in sorted(RULE_ITEMS)) + f" | {pct(scores(no_rule, gold, p)['macro_f1'])} |")
    L.append("")

    comps = [("gpt-6-luna A", "baseline"), ("gpt-6.1-sol A", "baseline")]
    for m in ["gpt-6-luna", "gpt-6.1-sol"]:
        comps += [(f"{m} A", f"{m} B"), (f"{m} A", f"{m} C"), (f"{m} B", f"{m} C")]
    comps += [(f"gpt-6.1-sol {x}", f"gpt-6-luna {x}") for x in "ABC"]
    comps += [(f"gpt-6-luna {x}", f"gpt-6-luna {x} (v1)") for x in "ABC"]
    L += ["## Comparisons (all 174 items)", "", "Only first right counts items the first system gets right and the second gets wrong.", "",
          "| first | second | only first right | only second right | p |", "|---|---|---|---|---|"]
    for a, b in comps:
        oa, ob, p = mcnemar(all_ids, gold, systs[a], systs[b])
        L.append(f"| {a} | {b} | {oa} | {ob} | {p:.3f} |")
    L.append("")

    llm = [n for n in main_names if n != "baseline"]
    wrong = Counter(i for n in llm for i in real if systs[n][i] != gold[i])
    L += ["## Hard real claims", "", "Real claims that at least two LLM systems got wrong.", "", "| claim | gold | wrong in |", "|---|---|---|"]
    for i, k in wrong.most_common():
        if k >= 2:
            L.append(f"| {i} | {gold[i]} | " + ", ".join(n for n in llm if systs[n][i] != gold[i]) + " |")
    L.append("")

    L += ["## Agreement between modes", "", "| model | A and B | A and C | B and C | wrong in all three | majority vote correct |", "|---|---|---|---|---|---|"]
    for m in ["gpt-6-luna", "gpt-6.1-sol"]:
        a, b, c = (systs[f"{m} {x}"] for x in "ABC")
        agree = lambda p, q: sum(p[i] == q[i] for i in all_ids)
        allwrong = sum(a[i] != gold[i] and b[i] != gold[i] and c[i] != gold[i] for i in all_ids)
        vote = sum(Counter([a[i], b[i], c[i]]).most_common(1)[0][0] == gold[i] if len({a[i], b[i], c[i]}) < 3 else a[i] == gold[i] for i in all_ids)
        L.append(f"| {m} | {agree(a, b)}/174 | {agree(a, c)}/174 | {agree(b, c)}/174 | {allwrong} | {vote}/174 |")
    L += ["", "When all three modes disagree, the vote uses mode A.", ""]

    L += ["## v1 to v2 changes for luna", "", "| mode | fixed | broken | fixed items not aimed at by v2 | broken items |", "|---|---|---|---|---|"]
    for x in "ABC":
        new, old = systs[f"gpt-6-luna {x}"], systs[f"gpt-6-luna {x} (v1)"]
        fixed = [i for i in all_ids if new[i] == gold[i] and old[i] != gold[i]]
        broken = [i for i in all_ids if new[i] != gold[i] and old[i] == gold[i]]
        L.append(f"| {x} | {len(fixed)} | {len(broken)} | {', '.join(i for i in fixed if i not in RULE_ITEMS) or '-'} | {', '.join(broken) or '-'} |")
    L += ["", "Items that change without being aimed at show how much a single run varies.", ""]

    runs = {}
    for m in ["gpt-6-luna", "gpt-6.1-sol"]:
        for x in "ABC":
            paths = [ROOT / "results" / "llm" / f"{m}__{x}_run{k}.jsonl" for k in (2, 3)]
            if all(p.exists() for p in paths):
                name = f"{m} {x}"
                runs[name] = [systs[name]] + [load_system(p, items, f"{name} run{k}", True) for k, p in zip((2, 3), paths)]
    if runs:
        L += ["## Repeated runs", "", "Each system was run three times with the same prompts. "
              "Changed label means the share of items that did not get the same label in all three runs.", "",
              "| system | accuracy per run | macro-F1 mean (min to max) | changed label | wrong in at least one run |", "|---|---|---|---|---|"]
        for name, rs in runs.items():
            accs = [scores(all_ids, gold, r)["acc"] for r in rs]
            f1s = [scores(all_ids, gold, r)["macro_f1"] for r in rs]
            changed = sum(len({r[i] for r in rs}) > 1 for i in all_ids)
            anywrong = sum(any(r[i] != gold[i] for r in rs) for i in all_ids)
            L.append(f"| {name} | {' / '.join(pct(a) for a in accs)} | {pct(sum(f1s) / 3)} ({pct(min(f1s))} to {pct(max(f1s))}) | "
                     f"{changed}/174 ({pct(changed / 174)}) | {anywrong} |")
        L.append("")

        L += ["## Three-run summary", "", "Means over runs 1 to 3. Real counts are correct answers out of 49 real claims, and found counts are real INCONSISTENT claims found out of 7, given per run.", "",
              "| system | accuracy mean | macro-F1 mean (min to max) | real correct per run | real INCONSISTENT found per run |", "|---|---|---|---|---|"]
        b = systs["baseline"]
        L.append(f"| baseline | {pct(scores(all_ids, gold, b)['acc'])} | {pct(scores(all_ids, gold, b)['macro_f1'])} | "
                 f"{sum(b[i] == gold[i] for i in real)} | {sum(b[i] == gold[i] == 'INCONSISTENT' for i in real)} |")
        for name, rs in runs.items():
            accs = [scores(all_ids, gold, r)["acc"] for r in rs]
            f1s = [scores(all_ids, gold, r)["macro_f1"] for r in rs]
            rc = " / ".join(str(sum(r[i] == gold[i] for i in real)) for r in rs)
            ri = " / ".join(str(sum(r[i] == gold[i] == "INCONSISTENT" for i in real)) for r in rs)
            L.append(f"| {name} | {pct(sum(accs) / 3)} | {pct(sum(f1s) / 3)} ({pct(min(f1s))} to {pct(max(f1s))}) | {rc} | {ri} |")
        L.append("")

        L += ["## Flagging unstable items for review", "",
              "A simple rule for a reporting team: run the cheap model three times and send an item to a person when the three answers differ. "
              "An item whose answers differ is always wrong in at least one run, so all flagged items reach a person. "
              "Errors left after review counts items that are wrong in all three runs, which flagging cannot catch.", "",
              "| system | items flagged | errors per single run | errors left after review |", "|---|---|---|---|"]
        for name, rs in runs.items():
            flagged = {i for i in all_ids if len({r[i] for r in rs}) > 1}
            per_run = " / ".join(str(sum(r[i] != gold[i] for i in all_ids)) for r in rs)
            allwrong = {i for i in all_ids if all(r[i] != gold[i] for r in rs)}
            L.append(f"| {name} | {len(flagged)} | {per_run} | {len(allwrong)} ({', '.join(sorted(allwrong)) or '-'}) |")
        L.append("")

    L += ["## Confusion matrices, all items", "", "Rows are gold labels, columns are predictions.", ""]
    for n in main_names:
        p = systs[n]
        cols = LABELS + ["INVALID"]
        L += [f"**{n}**", "", "| gold \\ pred | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
        for g in LABELS:
            L.append(f"| {g} | " + " | ".join(str(sum(gold[i] == g and p[i] == c for i in all_ids)) for c in cols) + " |")
        L.append("")

    (ROOT / "results" / "summary.md").write_text("\n".join(L), encoding="utf-8")

    with open(ROOT / "results" / "errors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["system", "item_id", "source", "perturbation", "gold", "pred", "claim", "reply"])
        for n in systs:
            for i in all_ids:
                if systs[n][i] != gold[i]:
                    w.writerow([n, i, items[i]["source"], items[i]["perturbation"], gold[i], systs[n][i], items[i]["claim"], REPLIES.get((n, i), "")])
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
