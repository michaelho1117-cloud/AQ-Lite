"""72-hour closing-line value, with an event-level bootstrap."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from judge.config import DEFAULT_RULES, require_positive, require_unit_interval


@dataclass(frozen=True)
class Fill:
    market: str
    ts: float
    side: str
    price: float
    amount: float
    event_id: str


@dataclass(frozen=True)
class ClvFill:
    market: str
    ts: float
    side: str
    price: float
    amount: float
    event_id: str
    clv: float


@dataclass(frozen=True)
class ClvReport:
    per_fill: tuple
    n: int
    weighted_clv: float
    positive_ratio: float
    ci_lower: float
    ci_upper: float


def _check_fill(fill):
    if not isinstance(fill, Fill):
        raise ValueError("fills must be Fill values")
    if not isinstance(fill.market, str) or not fill.market:
        raise ValueError("market must be a non-empty string")
    if isinstance(fill.ts, bool) or not isinstance(fill.ts, (int, float)):
        raise ValueError("ts must be a number of unix seconds")
    if fill.side not in ("YES", "NO"):
        raise ValueError("side must be YES or NO")
    price = require_unit_interval(fill.price, "price")
    amount = require_positive(fill.amount, "amount")
    if not isinstance(fill.event_id, str) or not fill.event_id:
        raise ValueError("event_id must be a non-empty string")
    return price, amount


def _weighted(pairs):
    total = 0.0
    weight = 0.0
    for clv_value, amount in pairs:
        total += clv_value * amount
        weight += amount
    if weight <= 0.0:
        raise ValueError("amount total must be positive")
    return total / weight


def _ci_indices(n_boot, alpha):
    lo_i = int(math.floor((alpha / 2.0) * n_boot))
    hi_i = int(math.ceil((1.0 - alpha / 2.0) * n_boot)) - 1
    lo_i = max(0, min(n_boot - 1, lo_i))
    hi_i = max(0, min(n_boot - 1, hi_i))
    return lo_i, hi_i


def clv_72h(fills, price_at, rules=DEFAULT_RULES, n_boot=None, seed=0):
    """Per-fill CLV, amount-weighted mean, positive share, and an event bootstrap interval.

    price_at(market, t) returns the YES price. A YES fill's CLV is that future YES price
    minus the fill price. A NO fill's price is the NO price, and its CLV is
    (1 − future YES price) − fill price. Positive means the move favored the side bought.
    """
    if isinstance(fills, str) or fills is None:
        raise ValueError("fills must be a sequence")
    book = tuple(fills)
    if not book:
        raise ValueError("fills must not be empty")
    if not callable(price_at):
        raise ValueError("price_at must be a function")
    boots = rules.clv_n_boot if n_boot is None else n_boot
    if isinstance(boots, bool) or not isinstance(boots, int) or boots < 1:
        raise ValueError("n_boot must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an int")
    horizon = rules.clv_hours * 3600.0
    scored = []
    groups = {}
    order = []
    for fill in book:
        _check_fill(fill)
        later = price_at(fill.market, float(fill.ts) + horizon)
        yes_later = require_unit_interval(later, "price_at")
        if fill.side == "YES":
            clv_value = yes_later - float(fill.price)
        else:
            clv_value = (1.0 - yes_later) - float(fill.price)
        scored.append(
            ClvFill(
                fill.market,
                float(fill.ts),
                fill.side,
                float(fill.price),
                float(fill.amount),
                fill.event_id,
                clv_value,
            )
        )
        if fill.event_id not in groups:
            groups[fill.event_id] = []
            order.append(fill.event_id)
        groups[fill.event_id].append((clv_value, float(fill.amount)))
    weighted = _weighted((item.clv, item.amount) for item in scored)
    positive = sum(1 for item in scored if item.clv > 0.0) / len(scored)
    rng = random.Random(seed)
    k = len(order)
    samples = []
    for _ in range(boots):
        drawn = [order[rng.randrange(k)] for _ in range(k)]
        pairs = []
        for event_id in drawn:
            pairs.extend(groups[event_id])
        samples.append(_weighted(pairs))
    samples.sort()
    lo_i, hi_i = _ci_indices(boots, rules.clv_ci_alpha)
    return ClvReport(
        tuple(scored),
        len(scored),
        weighted,
        positive,
        samples[lo_i],
        samples[hi_i],
    )
