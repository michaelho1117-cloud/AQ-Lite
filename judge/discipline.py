"""Discipline checks. Notes do not block, except the two cases marked as rejections."""
from __future__ import annotations

from dataclasses import dataclass

from judge.config import DEFAULT_RULES, require_non_negative, require_positive, require_unit_interval
from judge.sizing import kelly_fraction


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    notes: tuple


@dataclass(frozen=True)
class Position:
    driver: str
    amount: float


@dataclass(frozen=True)
class DowngradeAdvice:
    target_shares: float
    sell_shares: float
    notes: tuple


def threshold_check(deviation, spread, hard_info, rules=DEFAULT_RULES):
    """D20/D44 and D31. Below the threshold is a rejection."""
    gap = require_non_negative(deviation, "deviation")
    width = require_non_negative(spread, "spread")
    if hard_info:
        bar = rules.hard_info_threshold
    else:
        bar = rules.deviation_threshold
    if width > rules.thin_spread:
        bar = rules.deviation_threshold
    if gap < bar:
        return CheckResult(False, ("偏离不到门槛",))
    return CheckResult(True, ())


def news_triage_required(deviation_from_1d_median, rules=DEFAULT_RULES):
    """D22. A note, not a rejection."""
    gap = require_non_negative(deviation_from_1d_median, "deviation_from_1d_median")
    if gap >= rules.news_triage_deviation:
        return CheckResult(True, ("先过新闻分诊",))
    return CheckResult(True, ())


def scope_check(category, rules=DEFAULT_RULES):
    """D11. Entertainment categories are rejections."""
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must be a non-empty string")
    banned = {item.casefold() for item in rules.rejected_categories}
    if category.strip().casefold() in banned:
        return CheckResult(False, ("娱乐盘，拒绝",))
    return CheckResult(True, ())


def _as_position(item):
    if isinstance(item, Position):
        driver, amount = item.driver, item.amount
    else:
        try:
            driver, amount = item
        except (TypeError, ValueError) as exc:
            raise ValueError("position must be Position or (driver, amount)") from exc
    if not isinstance(driver, str) or not driver:
        raise ValueError("driver must be a non-empty string")
    return driver, require_non_negative(amount, "position amount")


def concentration_check(positions, new_driver, new_amount, balance, rules=DEFAULT_RULES):
    """D25. Notes only. positions are the book before this order."""
    if not isinstance(new_driver, str) or not new_driver:
        raise ValueError("new_driver must be a non-empty string")
    added = require_non_negative(new_amount, "new_amount")
    cash = require_positive(balance, "balance")
    if isinstance(positions, str) or positions is None:
        raise ValueError("positions must be a sequence")
    book = tuple(_as_position(item) for item in positions)
    same = sum(amount for driver, amount in book if driver == new_driver) + added
    notes = []
    if same > rules.driver_concentration_fraction * cash:
        notes.append("同一驱动因素合计超过余额 35%")
    remaining = cash - sum(amount for _driver, amount in book) - added
    if remaining < rules.min_cash_fraction * cash:
        notes.append("下单后现金低于 30%")
    return CheckResult(True, tuple(notes))


def event_risk_check(event_cost_at_risk, total_assets, rules=DEFAULT_RULES):
    """D73 item 1. A note when one event is more than 10% of assets."""
    at_risk = require_non_negative(event_cost_at_risk, "event_cost_at_risk")
    assets = require_positive(total_assets, "total_assets")
    if at_risk > rules.event_risk_fraction * assets:
        return CheckResult(True, ("事件在险超过总资产 10%",))
    return CheckResult(True, ())


def _side_probability(fair, side):
    if side == "YES":
        return fair
    if side == "NO":
        return 1.0 - fair
    raise ValueError("side must be YES or NO")


def downgrade_advice(old_fair, new_fair, position_shares, price, side, balance, rules=DEFAULT_RULES):
    """D73 item 3. Cut toward the Kelly cap of the new blend. Never advise adding."""
    old_p = require_unit_interval(old_fair, "old_fair")
    new_p = require_unit_interval(new_fair, "new_fair")
    px = require_unit_interval(price, "price")
    shares = require_non_negative(position_shares, "position_shares")
    cash = require_positive(balance, "balance")
    if side not in ("YES", "NO"):
        raise ValueError("side must be YES or NO")
    old_side = _side_probability(old_p, side)
    new_side = _side_probability(new_p, side)
    if new_side >= old_side:
        return DowngradeAdvice(shares, 0.0, ("估值没有下调",))
    blended = rules.blend_weight * new_side + (1.0 - rules.blend_weight) * px
    # kelly_fraction takes the YES fair. For NO, the YES fair is 1 − blended NO probability.
    yes_fair = blended if side == "YES" else 1.0 - blended
    if not 0.0 < yes_fair < 1.0:
        fraction = 0.0
    else:
        fraction = kelly_fraction(yes_fair, px, side, rules)
    kelly_shares = fraction * cash / px
    target = min(shares, kelly_shares)
    sell = shares - target
    return DowngradeAdvice(target, sell, ())


def c_play_check(amount, balance, today_c_total, rules=DEFAULT_RULES):
    """SOP step 7, C plays. today_c_total excludes this order."""
    order = require_non_negative(amount, "amount")
    cash = require_positive(balance, "balance")
    already = require_non_negative(today_c_total, "today_c_total")
    notes = []
    if order > rules.c_play_single_fraction * cash:
        notes.append("单笔超过余额 5%")
    if already + order > rules.c_play_daily_fraction * cash:
        notes.append("当天合计超过余额 15%")
    return CheckResult(True, tuple(notes))


def jump_window_adjust(grade, jump_window, rules=DEFAULT_RULES):
    """D9. Inside a jump window, S becomes A. Other grades stay put."""
    del rules
    if grade not in ("S", "A", "B", None):
        raise ValueError("grade must be S, A, B, or None")
    if jump_window and grade == "S":
        return "A"
    return grade
