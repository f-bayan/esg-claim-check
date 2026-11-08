import argparse
import hashlib
import json
import os
import re

from common import LABELS, ROOT, load_items
from mode_c import decide

PROMPTS = ROOT / "prompts"
FIX = "Your answer was not valid. Return only the JSON object in the required format."


def load_env():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def system_prompt(mode):
    return (PROMPTS / "common.txt").read_text() + "\n" + (PROMPTS / f"mode_{mode.lower()}.txt").read_text()


def user_prompt(it):
    return f"Claim: {it['claim']}\nContext: {it['context'] or '(none)'}\nTable:\n{it['evidence']}"


def parse(mode, text, it):
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    if mode in ("A", "B"):
        label = str(data.get("label", "")).strip().upper()
        if label not in LABELS:
            raise ValueError(f"bad label {label!r}")
        return label, "label"
    facts = data.get("facts")
    if not isinstance(facts, list):
        raise ValueError("no facts list")
    return decide(facts, it["evidence"])


def item_hash(system, it):
    return hashlib.sha256((system + "\n" + user_prompt(it)).encode()).hexdigest()[:12]


def read_done(out, phash, hashes):
    done = set()
    if not out.exists():
        return done
    for line in out.open(encoding="utf-8"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            print("skipping a broken line in", out.name)
            continue
        iid = rec.get("item_id")
        if rec.get("prompt_hash") != phash or (iid in hashes and rec.get("item_hash") != hashes[iid]):
            raise SystemExit(f"{out.name} was made with a different prompt or evidence ({iid}). Move it away or delete it first.")
        done.add(iid)
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", required=True, choices=["A", "B", "C"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids")
    ap.add_argument("--reasoning-effort")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    items = load_items()
    if args.ids:
        keep = set(args.ids.split(","))
        unknown = keep - {it["item_id"] for it in items}
        if unknown:
            print("unknown ids:", ", ".join(sorted(unknown)))
        items = [it for it in items if it["item_id"] in keep]
    if args.limit is not None:
        items = items[:args.limit]
    if not items:
        raise SystemExit("no items to run")

    system = system_prompt(args.mode)
    phash = hashlib.sha256(system.encode()).hexdigest()[:12]
    if args.dry_run:
        print(system)
        print("-----")
        print(user_prompt(items[0]))
        print("-----")
        print(f"{len(items)} items, prompt {phash}")
        return

    load_env()
    from openai import BadRequestError, OpenAI
    client = OpenAI(max_retries=5)

    tag = args.model + (f"-{args.reasoning_effort}" if args.reasoning_effort else "")
    suffix = f"_run{args.run}" if args.run > 1 else ""
    out = ROOT / "results" / "llm" / f"{re.sub(r'[^A-Za-z0-9._-]', '_', tag)}__{args.mode}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    hashes = {it["item_id"]: item_hash(system, it) for it in items}
    done = read_done(out, phash, hashes)

    use_temp, tok_in, tok_out = True, 0, 0
    todo = [it for it in items if it["item_id"] not in done]
    print(f"{len(todo)} to run, {len(items) - len(todo)} already done -> {out.name}")
    for n, it in enumerate(todo, 1):
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user_prompt(it)}]
        rec = {"item_id": it["item_id"], "model": args.model, "mode": args.mode, "prompt_hash": phash,
               "item_hash": hashes[it["item_id"]], "run": args.run,
               "reasoning_effort": args.reasoning_effort, "pred": "INVALID", "rule": "", "raw": "", "error": "",
               "api_model": "", "finish_reason": ""}
        for _ in range(2):
            kw = {"model": args.model, "messages": messages, "response_format": {"type": "json_object"}}
            if args.reasoning_effort:
                kw["reasoning_effort"] = args.reasoning_effort
            if use_temp:
                kw["temperature"] = 0
            try:
                resp = client.chat.completions.create(**kw)
            except BadRequestError as e:
                if use_temp and "temperature" in str(e):
                    use_temp = False
                    kw.pop("temperature")
                    resp = client.chat.completions.create(**kw)
                else:
                    raise
            text = resp.choices[0].message.content or ""
            if resp.usage:
                tok_in += resp.usage.prompt_tokens
                tok_out += resp.usage.completion_tokens
            rec.update(raw=text, api_model=resp.model, finish_reason=resp.choices[0].finish_reason)
            try:
                rec["pred"], rec["rule"] = parse(args.mode, text, it)
                rec["error"] = ""
                break
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                rec["error"] = f"parse: {e}"
                messages = messages + [{"role": "assistant", "content": text}, {"role": "user", "content": FIX}]
        rec["temperature"] = 0 if use_temp else "default"
        if out.exists() and out.stat().st_size and not out.read_bytes().endswith(b"\n"):
            with out.open("a", encoding="utf-8") as f:
                f.write("\n")
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{n}/{len(todo)}] {it['item_id']}: {rec['pred']} (gold {it['label']})")
    print(f"tokens in {tok_in}, out {tok_out}")


if __name__ == "__main__":
    main()
