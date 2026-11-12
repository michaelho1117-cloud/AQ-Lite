"""AQ-Lite: read-only market tools for the AtomQuant offline kit. Standard library only. Never trades.

  python aq.py scan [--days 15]           full scan: AI + geopolitics markets ending within N days, with 1d/7d percentiles
  python aq.py market <slug|url|keywords> rules + every bucket of matching events (bid/ask/mid, d1, vol, p1/p7)
  python aq.py book <slug> <bucket text>   CLOB depth for one bucket (YES side; NO = 1 - YES)
  python aq.py size --anchor A --mid M --price P --side YES|NO --cat tech|geo --assets X --cash C [options]
  python aq.py rules <keyword>             search the rule-card library (data/rule_cards)
  python aq.py positions <wallet>          public positions of a wallet (data-api)
"""
import argparse, csv, datetime as dt, gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
VAR = os.path.join(ROOT, "var")
os.makedirs(VAR, exist_ok=True)
GAMMA, CLOB, DATA = "https://gamma-api.polymarket.com", "https://clob.polymarket.com", "https://data-api.polymarket.com"
NOW = dt.datetime.now(dt.timezone.utc)


def get(url, tries=3):
    """Polite GET (0.7 s gap). gzip is required by gamma for large pages. 403/429 stops the program (D29)."""
    req = urllib.request.Request(url, headers={"User-Agent": "atomquant/0.1", "Accept": "application/json", "Accept-Encoding": "gzip"})
    for i in range(tries):
        time.sleep(0.7)
        try:
            r = urllib.request.urlopen(req, timeout=40)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
            return json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                sys.exit(f"STOP: HTTP {e.code} from {url[:80]} - wait at least 10 minutes before retrying")
            if e.code in (404, 422):
                return None
        except Exception:
            pass
        time.sleep(2)
    return None


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def hours_to(end):
    try:
        return (dt.datetime.fromisoformat(end.replace("Z", "+00:00")) - NOW).total_seconds() / 3600
    except Exception:
        return None


def pct_rank(xs, v):
    return round(100 * sum(1 for x in xs if x <= v) / len(xs)) if xs else None


def history_pct(token, mid):
    h7 = (get(f"{CLOB}/prices-history?market={token}&interval=1w&fidelity=60") or {}).get("history", [])
    h1 = (get(f"{CLOB}/prices-history?market={token}&interval=1d&fidelity=10") or {}).get("history", [])
    p7, p1 = [x["p"] for x in h7], [x["p"] for x in h1]
    return {"p1": pct_rank(p1, mid), "p7": pct_rank(p7, mid), "lo7": min(p7) if p7 else None, "hi7": max(p7) if p7 else None,
            "med1": sorted(p1)[len(p1) // 2] if p1 else None}


AI = re.compile(r"\b(openai|gpt|chatgpt|sora|gemini|google ai|deepmind|claude|anthropic|grok|xai|deepseek|qwen|alibaba|kimi|moonshot|glm|zhipu|minimax|llama|meta ai|muse|mistral|llm|ai model|astra|fable|mythos|opus|sonnet|haiku|nvidia|agi|arena|lmarena|hle|benchmark|app store)\b", re.I)
GEO = re.compile(r"\b(iran|israel|gaza|hamas|hezbollah|houthi|yemen|lebanon|syria|russia|ukraine|putin|zelensky|nato|china|taiwan|north korea|venezuela|cuba|strike|ceasefire|invade|invasion|military|troops|missile|nuclear|sanction|hormuz|red sea|war|peace deal|summit|diplomatic|pakistan|india|qatar|saudi|iraq|turkey|netanyahu|khamenei|coup|blockade|annex|greenland|tariff)\b", re.I)
BAD = re.compile(r"\b(vs\.?|nfl|nba|mlb|nhl|ufc|premier league|la liga|serie a|bundesliga|champions league|tennis|golf|f1|grand prix|esports|cs2|dota|valorant|bitcoin|btc|ethereum|eth|solana|xrp|doge|crypto|price of|above \$|below \$|temperature|weather|box office|grammy|oscar|tweets?|spotify|billboard|album|movie|netflix|mrbeast|super bowl|mayor|primary|senate race|poll|miss universe)\b", re.I)
TAGS = ["ai", "tech", "openai", "geopolitics", "world", "middle-east", "foreign-policy", "ukraine", "iran", "israel", "china", "russia", "trump"]


def cmd_scan(a):
    lo, hi = NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), (NOW + dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    seen, rows = set(), []
    for tag in TAGS:
        off = 0
        while off < 3000:
            page = get(f"{GAMMA}/events?closed=false&active=true&tag_slug={tag}&limit=100&offset={off}")
            if not page:
                break
            for ev in page:
                if ev["id"] in seen:
                    continue
                seen.add(ev["id"])
                for m in ev.get("markets") or []:
                    end = m.get("endDate") or ev.get("endDate") or ""
                    if m.get("closed") or not (lo <= end[:19] + "Z" <= hi):
                        continue
                    text = (m.get("question") or "") + " " + (ev.get("title") or "")
                    if BAD.search(text):
                        continue
                    cat = "AI" if AI.search(text) else ("GEO" if GEO.search(text) else None)
                    bid, ask = f(m.get("bestBid")), f(m.get("bestAsk"))
                    if not cat or bid is None or ask is None or not 0.04 < (bid + ask) / 2 < 0.96:
                        continue
                    rows.append({"cat": cat, "event": ev.get("slug"), "etitle": (ev.get("title") or "")[:70], "item": m.get("groupItemTitle") or (m.get("question") or "")[:60],
                                 "bid": bid, "ask": ask, "d1": f(m.get("oneDayPriceChange")), "v24": f(m.get("volume24hr")) or 0, "liq": f(m.get("liquidity")) or 0,
                                 "end": end[:16], "tok": json.loads(m["clobTokenIds"])[0] if m.get("clobTokenIds") else None})
            if len(page) < 100:
                break
            off += 100
        print(f"  tag {tag}: events so far {len(seen)}", file=sys.stderr)
    print(f"events seen {len(seen)}, candidate markets {len(rows)}; fetching price history (~1.5 s each)", file=sys.stderr)
    for i, r in enumerate(rows):
        if i % 20 == 0:
            print(f"  history {i}/{len(rows)}", file=sys.stderr)
        if r["tok"]:
            r.update(history_pct(r["tok"], (r["bid"] + r["ask"]) / 2))
    out = [f"now {NOW:%Y-%m-%d %H:%MZ} | p1/p7 = mid's percentile in the last 1d / 7d of prices (0 = lowest, 100 = highest); med1 = 1-day median"]
    by = {}
    for r in rows:
        by.setdefault(r["event"], []).append(r)
    for slug, rs in sorted(by.items(), key=lambda kv: -sum(r["v24"] for r in kv[1])):
        out.append(f"\n# {rs[0]['cat']} {rs[0]['etitle']}  [{slug}]  v24={sum(r['v24'] for r in rs):.0f}")
        for r in sorted(rs, key=lambda r: r["end"]):
            mid = (r["bid"] + r["ask"]) / 2
            dev = f"{mid - r['med1']:+.3f}" if r.get("med1") is not None else "?"
            out.append(f"   {r['item'][:34]:<34} {r['bid']}/{r['ask']} d1={r['d1']} vs1dmed={dev} p1={r.get('p1')} p7={r.get('p7')} "
                       f"rng7={r.get('lo7')}-{r.get('hi7')} v24={r['v24']:.0f} liq={r['liq']:.0f} end={r['end']} ({hours_to(r['end'] + ':00Z') or 0:.0f}h)")
    text = "\n".join(out)
    path = os.path.join(VAR, f"scan_{NOW:%Y%m%d_%H%M}.txt")
    open(path, "w", encoding="utf-8").write(text)
    print(text)
    print(f"\nsaved {path}", file=sys.stderr)


def find_events(q):
    m = re.search(r"polymarket\.com/(?:event|market)/([^/?#]+)", q)
    slug = m.group(1) if m else (q if re.fullmatch(r"[a-z0-9\-]+", q) else None)
    if slug:
        evs = get(f"{GAMMA}/events?" + urllib.parse.urlencode({"slug": slug})) or []
        if evs:
            return evs
    res = get(f"{GAMMA}/public-search?" + urllib.parse.urlencode({"q": q, "limit_per_type": 5, "events_status": "active"})) or {}
    return [get(f"{GAMMA}/events/{e['id']}") for e in (res.get("events") or [])[:3]]


def cmd_market(a):
    for ev in find_events(" ".join(a.query)):
        if not ev:
            continue
        print("=" * 100)
        print(f"{ev.get('title')}  [{ev.get('slug')}]  end {ev.get('endDate')}  vol {f(ev.get('volume')) or 0:.0f}")
        print("RULES:\n" + (ev.get("description") or "").strip())
        rules_seen = {(ev.get("description") or "").strip()}
        for m in sorted(ev.get("markets") or [], key=lambda m: m.get("endDate") or ""):
            if m.get("closed"):
                continue
            d = (m.get("description") or "").strip()
            if d and d not in rules_seen:
                rules_seen.add(d)
                print(f"\nRULES for bucket {m.get('groupItemTitle')}:\n{d}")
            bid, ask = f(m.get("bestBid")), f(m.get("bestAsk"))
            line = f"  {(m.get('groupItemTitle') or m.get('question') or '')[:36]:<36} last={json.loads(m.get('outcomePrices') or '[null]')[0]} bid={bid} ask={ask} d1={m.get('oneDayPriceChange')} v24={f(m.get('volume24hr')) or 0:.0f} liq={f(m.get('liquidity')) or 0:.0f} end={(m.get('endDate') or '')[:16]} uma={m.get('umaResolutionStatuses') or ''}"
            if a.history and bid is not None and ask is not None and m.get("clobTokenIds"):
                h = history_pct(json.loads(m["clobTokenIds"])[0], (bid + ask) / 2)
                line += f" p1={h['p1']} p7={h['p7']} med1={h['med1']} rng7={h['lo7']}-{h['hi7']}"
            print(line)


def cmd_book(a):
    evs = find_events(a.slug)
    for ev in evs:
        for m in ev.get("markets") or []:
            if m.get("closed") or a.bucket.lower() not in (m.get("groupItemTitle") or m.get("question") or "").lower():
                continue
            b = get(f"{CLOB}/book?token_id={json.loads(m['clobTokenIds'])[0]}") or {}
            bids = sorted(((f(o["price"]), f(o["size"])) for o in b.get("bids", [])), reverse=True)[:10]
            asks = sorted((f(o["price"]), f(o["size"])) for o in b.get("asks", []))[:10]
            print(f"{ev.get('title')} :: {m.get('groupItemTitle')}   (YES book; buying NO at x = selling YES at 1-x)")
            print("  YES asks (price, shares, $):", [(p, round(s), round(p * s)) for p, s in asks])
            print("  YES bids (price, shares, $):", [(p, round(s), round(p * s)) for p, s in bids])
            return
    print("bucket not found")


def fee(p, cat):
    return 0.04 * p * (1 - p) if cat == "tech" else 0.0


def cmd_size(a):
    """SOP step 7 with the D106 fixes: blended anchor (D24/D45), edge and Kelly on the fee-inclusive price,
    grade S/A/B with red flags, D7 caps, D25 concentration on total assets vs cash, D73 tranche (1/3 market, rest laddered deeper)."""
    w = a.weight
    blend_yes = w * a.anchor + (1 - w) * a.mid
    p_side = blend_yes if a.side == "YES" else 1 - blend_yes
    q = a.price + fee(a.price, a.cat)                         # effective price per share incl. taker fee
    edge = p_side - q
    thr = 0.12 if (a.spread is not None and a.spread > 0.06) else (0.08 if a.hard_info else 0.12)   # D20/D44/D31
    grades = ["S", "A", "B", None]
    g = 0 if edge >= 0.15 else 1 if edge >= 0.08 else 2 if edge >= 0.04 else 3
    g = min(3, g + a.flags)
    grade = grades[g]
    kelly = max(0.0, min(1.0, (p_side - q) / (1 - q))) if q < 1 else 0.0
    mult = {"S": 1.0, "A": 0.5}.get(grade, 0.0)
    amount = a.assets * kelly * mult
    notes = []
    if grade == "A" and amount > 0.35 * a.assets:
        amount, _ = 0.35 * a.assets, notes.append("A 档超过总资产 35%，已截断")
    if grade == "S" and amount > 0.25 * a.assets:
        notes.append("S 档超过总资产 25%：必须写一句理由（D7）")
    if a.deviation is not None and abs(a.deviation) < thr:
        notes.append(f"偏离 {a.deviation:+.3f} 未达门槛 {thr}（D20/D44；薄盘一律 0.12）→ 按 SOP 不出手")
    if amount > 0.10 * a.assets:
        notes.append("单一事件在险超过总资产 10%（D73-1）")
    if a.driver_existing + amount > 0.35 * a.assets:
        notes.append("同一驱动因素合计超过总资产 35%（D25）")
    if a.cash - amount < 0.30 * a.assets:
        notes.append("下单后现金低于总资产 30%（D25）")
    print(f"blended YES fair = {w}×{a.anchor} + {1 - w:.2f}×{a.mid} = {blend_yes:.4f}  ({a.side} side prob {p_side:.4f})")
    print(f"price {a.price} + taker fee {fee(a.price, a.cat):.4f} = effective {q:.4f}   edge = {edge:+.4f}   grade = {grade}  (flags {a.flags})")
    print(f"Kelly fraction (fee-inclusive) = {kelly:.4f}   multiplier {mult}   planned amount = ${amount:.2f}   shares ≈ {amount / q if q else 0:.1f}")
    if amount > 0:
        levels = sorted(a.levels or [], reverse=(True))
        first = amount / 3
        print(f"tranche (D73-2): market/limit-at-best ${first:.2f} now; rest ${amount - first:.2f} as resting bids", end="")
        if levels:
            ws = list(range(1, len(levels) + 1))
            print(" (shallow→deep, deeper gets more):", ", ".join(f"{p:.3f}: ${(amount - first) * w_ / sum(ws):.2f}" for p, w_ in zip(levels, ws)))
        else:
            print(" (pass --levels to split)")
        print(f"worst case: lose ${amount:.2f} = {100 * amount / a.assets:.1f}% of total assets")
    for n in notes:
        print("NOTE:", n)


def cmd_rules(a):
    kw = " ".join(a.keyword).lower()
    base = os.path.join(ROOT, "data", "rule_cards")
    for fn in ("rule_cards_open.csv", "risk_flags.csv"):
        for r in csv.DictReader(open(os.path.join(base, fn), encoding="utf-8")):
            if kw in json.dumps(r, ensure_ascii=False).lower():
                print(f"--- {fn} ---")
                for k, v in r.items():
                    print(f"  {k}: {v}")


def cmd_positions(a):
    rows = get(f"{DATA}/positions?" + urllib.parse.urlencode({"user": a.wallet, "sizeThreshold": 0.1, "limit": 200})) or []
    for p in sorted(rows, key=lambda p: -(f(p.get("currentValue")) or 0)):
        print(f"  {(p.get('title') or '')[:60]:<60} {p.get('outcome'):<4} size={f(p.get('size')) or 0:.1f} avg={p.get('avgPrice')} cur={p.get('curPrice')} value=${f(p.get('currentValue')) or 0:.2f} pnl=${f(p.get('cashPnl')) or 0:.2f} end={p.get('endDate')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("scan"); s.add_argument("--days", type=int, default=15); s.set_defaults(fn=cmd_scan)
    s = sp.add_parser("market"); s.add_argument("query", nargs="+"); s.add_argument("--no-history", dest="history", action="store_false"); s.set_defaults(fn=cmd_market)
    s = sp.add_parser("book"); s.add_argument("slug"); s.add_argument("bucket"); s.set_defaults(fn=cmd_book)
    s = sp.add_parser("size")
    for k, t in [("anchor", float), ("mid", float), ("price", float), ("assets", float), ("cash", float)]:
        s.add_argument("--" + k, type=t, required=True)
    s.add_argument("--side", choices=["YES", "NO"], required=True); s.add_argument("--cat", choices=["tech", "geo"], required=True)
    s.add_argument("--weight", type=float, default=0.5, help="D24/D45 anchor weight (default 0.5)")
    s.add_argument("--flags", type=int, default=0, help="number of red flags (each lowers the grade one step)")
    s.add_argument("--hard-info", action="store_true", help="a sourced hard signal exists (threshold 0.08 instead of 0.12)")
    s.add_argument("--spread", type=float); s.add_argument("--deviation", type=float, help="mid minus 1-day median, for the D20/D44 threshold")
    s.add_argument("--driver-existing", type=float, default=0.0, help="USD already at risk on the same driver")
    s.add_argument("--levels", type=float, nargs="*", help="limit prices for the resting part")
    s.set_defaults(fn=cmd_size)
    s = sp.add_parser("rules"); s.add_argument("keyword", nargs="+"); s.set_defaults(fn=cmd_rules)
    s = sp.add_parser("positions"); s.add_argument("wallet"); s.set_defaults(fn=cmd_positions)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
