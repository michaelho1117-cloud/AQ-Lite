"""Blend, edge, grade, Kelly, and order slicing."""
from __future__ import annotations

from dataclasses import dataclass

from judge.config import DEFAULT_RULES, require_non_negative, require_positive, require_unit_interval

_GRADES = ("S", "A", "B")


@dataclass(frozen=True)
class PositionSize:
    amount: float
    notes: tuple


@dataclass(frozen=True)
class Tranche:
    price: float | None
    amount: float
    kind: str


@dataclass(frozen=True)
class GtdOrder:
    price: float
    amount: float
    expire_hours: float


def blend(anchor, market, w=None, rules=DEFAULT_RULES):
    """D24. w × anchor + (1 − w) × market. w defaults to rules.blend_weight."""
    anchor_p = require_unit_interval(anchor, "anchor")
    market_p = require_unit_interval(market, "market")
    weight = rules.blend_weight if w is None else w
    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        raise ValueError("w must be a number in [0, 1]")
    if not 0.0 <= float(weight) <= 1.0:
        raise ValueError("w must be in [0, 1]")
    return float(weight) * anchor_p + (1.0 - float(weight)) * market_p


def anchor_weight(clv_stats, rules=DEFAULT_RULES):
    """D45. Raise the blend weight only when every positive condition holds."""
    n = clv_stats.n
    weighted = clv_stats.weighted_clv
    positive = clv_stats.positive_ratio
    ci_lower = clv_stats.ci_lower
    if isinstance(n, bool) or not isinstance(n, (int, float)) or int(n) != n or n < 0:
        raise ValueError("n must be a non-negative integer")
    if isinstance(weighted, bool) or not isinstance(weighted, (int, float)):
        raise ValueError("weighted_clv must be a number")
    if isinstance(positive, bool) or not isinstance(positive, (int, float)):
        raise ValueError("positive_ratio must be a number")
    if not 0.0 <= float(positive) <= 1.0:
        raise ValueError("positive_ratio must be in [0, 1]")
    if isinstance(ci_lower, bool) or not isinstance(ci_lower, (int, float)):
        raise ValueError("ci_lower must be a number")
    n = int(n)
    positive_ok = (
        float(weighted) > 0.0
        and float(positive) >= rules.anchor_positive_ratio_min
        and float(ci_lower) > 0.0
    )
    if n >= rules.anchor_n_high and positive_ok:
        return rules.anchor_weight_high
    if n >= rules.anchor_n_mid and positive_ok:
        return rules.anchor_weight_mid
    if n >= rules.anchor_n_mid and float(weighted) < 0.0:
        return rules.anchor_weight_negative
    return rules.anchor_weight_default


def _side(side):
    if side not in ("YES", "NO"):
        raise ValueError("side must be YES or NO")
    return side


def edge(fair, side, best_price, fee, rules=DEFAULT_RULES):
    """YES: fair − (ask + fee). NO: (1 − fair) − (no_ask + fee)."""
    del rules  # fee is passed in; the coefficient lives in Rules for taker_fee_per_share
    fair_p = require_unit_interval(fair, "fair")
    ask = require_unit_interval(best_price, "best_price")
    fee_v = require_non_negative(fee, "fee")
    if _side(side) == "YES":
        return fair_p - (ask + fee_v)
    return (1.0 - fair_p) - (ask + fee_v)


def grade(edge_value, red_flags, rules=DEFAULT_RULES):
    """Step 7. One red flag lowers the grade by one step. Several flags lower it once per flag."""
    if isinstance(edge_value, bool) or not isinstance(edge_value, (int, float)):
        raise ValueError("edge must be a number")
    if isinstance(red_flags, str):
        raise ValueError("red_flags must be a sequence of flags, not a string")
    flags = () if red_flags is None else tuple(red_flags)
    value = float(edge_value)
    if value >= rules.grade_s_min:
        current = "S"
    elif value >= rules.grade_a_min:
        current = "A"
    elif value >= rules.grade_b_min:
        current = "B"
    else:
        current = None
    order = ("S", "A", "B", None)
    index = order.index(current)
    index = min(index + len(flags), len(order) - 1)
    return order[index]


def kelly_fraction(fair, price, side, rules=DEFAULT_RULES):
    """YES: (fair − price) / (1 − price). NO uses the NO probability and the NO price. Clipped to [0, 1]."""
    del rules
    fair_p = require_unit_interval(fair, "fair")
    px = require_unit_interval(price, "price")
    if _side(side) == "YES":
        prob = fair_p
    else:
        prob = 1.0 - fair_p
    raw = (prob - px) / (1.0 - px)
    if raw < 0.0:
        return 0.0
    if raw > 1.0:
        return 1.0
    return raw


def position_size(balance, fair, price, side, grade_name, rules=DEFAULT_RULES):
    """D7. S is full Kelly, A is half Kelly capped at 35% of balance, B is zero."""
    cash = require_positive(balance, "balance")
    if grade_name not in ("S", "A", "B", None):
        raise ValueError("grade must be S, A, B, or None")
    frac = kelly_fraction(fair, price, side, rules)
    if grade_name == "S":
        multiplier = rules.kelly_s_multiplier
    elif grade_name == "A":
        multiplier = rules.kelly_a_multiplier
    else:
        multiplier = rules.kelly_b_multiplier
    amount = cash * frac * multiplier
    notes = []
    if grade_name == "S" and amount > rules.s_reason_balance_fraction * cash:
        notes.append("超过 25% 必须写理由")
    if grade_name == "A" and amount > rules.a_cap_balance_fraction * cash:
        amount = rules.a_cap_balance_fraction * cash
        notes.append("A 档超过余额 35%，已截断")
    return PositionSize(amount, tuple(notes))


def _weights_for(n_levels, rules):
    default = tuple(rules.ladder_weights)
    if n_levels == len(default):
        return default
    return tuple(range(1, n_levels + 1))


def tranche_plan(planned_amount, levels, rules=DEFAULT_RULES):
    """D73 item 2 and D14. Market order is 1/3; the rest follows D10/D21 weights."""
    planned = require_positive(planned_amount, "planned_amount")
    if isinstance(levels, str) or levels is None:
        raise ValueError("levels must be a sequence of limit prices")
    prices = tuple(levels)
    if not prices:
        raise ValueError("levels must contain the limit rungs")
    checked = tuple(require_unit_interval(price, "level") for price in prices)
    weights = _weights_for(len(checked), rules)
    first = planned * rules.market_order_max_fraction
    rest = planned - first
    weight_sum = float(sum(weights))
    amounts = []
    allocated = 0.0
    for index, weight in enumerate(weights):
        if index == len(weights) - 1:
            amounts.append(rest - allocated)
        else:
            piece = rest * (float(weight) / weight_sum)
            allocated += piece
            amounts.append(piece)
    out = [Tranche(None, first, "market")]
    for price, amount in zip(checked, amounts):
        out.append(Tranche(price, amount, "limit"))
    return tuple(out)


def _level_price_amount(level):
    if isinstance(level, Tranche):
        if level.price is None:
            raise ValueError("GTD levels need a limit price")
        return level.price, level.amount
    if isinstance(level, GtdOrder):
        return level.price, level.amount
    try:
        price, amount = level
    except (TypeError, ValueError) as exc:
        raise ValueError("level must be (price, amount)") from exc
    return price, amount


def overnight_gtd(levels, rules=DEFAULT_RULES, jump_window=False):
    """D10/D21 expiry, D9 haircut. Weights are applied by tranche_plan, not here."""
    if isinstance(levels, str) or levels is None:
        raise ValueError("levels must be a sequence of priced amounts")
    scale = rules.jump_window_amount_scale if jump_window else 1.0
    orders = []
    for level in levels:
        price, amount = _level_price_amount(level)
        px = require_unit_interval(price, "level")
        amt = require_positive(amount, "amount")
        orders.append(GtdOrder(px, amt * scale, rules.gtd_expire_hours))
    if not orders:
        raise ValueError("levels must not be empty")
    return tuple(orders)
