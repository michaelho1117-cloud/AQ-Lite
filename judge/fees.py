"""Per-share taker fees. Task section 2; no D id."""
from __future__ import annotations

from judge.config import DEFAULT_RULES, require_unit_interval


def taker_fee_per_share(p, category, rules=DEFAULT_RULES):
    """tech: coef × p × (1 − p). geo: the geo coefficient, default 0."""
    price = require_unit_interval(p, "price")
    if category == "tech":
        return rules.tech_fee_coef * price * (1.0 - price)
    if category == "geo":
        return float(rules.geo_fee_coef)
    raise ValueError(f"unknown fee category: {category}")
