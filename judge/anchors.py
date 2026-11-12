"""Anchor cards and Brier comparison against the market."""
from __future__ import annotations

from dataclasses import dataclass

from judge.config import DEFAULT_RULES, clip_unit, require_unit_interval


@dataclass(frozen=True)
class Correction:
    delta: float
    source_url: str
    seen_utc: str
    note: str

    def __post_init__(self):
        if isinstance(self.delta, bool) or not isinstance(self.delta, (int, float)):
            raise ValueError("delta must be a number")
        # D103. A correction with no source is not allowed.
        if not isinstance(self.source_url, str) or not self.source_url.strip():
            raise ValueError("correction requires source_url")


@dataclass(frozen=True)
class AnchorCard:
    market_id: str
    created_utc: str
    market_mid: float
    corrections: tuple
    point: float
    low: float
    high: float
    triggers: tuple

    def __post_init__(self):
        if not isinstance(self.market_id, str) or not self.market_id:
            raise ValueError("market_id must be a non-empty string")
        mid = require_unit_interval(self.market_mid, "market_mid")
        if isinstance(self.corrections, str) or self.corrections is None:
            raise ValueError("corrections must be a sequence")
        items = tuple(self.corrections)
        for item in items:
            if not isinstance(item, Correction):
                raise ValueError("corrections must be Correction values")
        expected = clip_unit(mid + sum(float(item.delta) for item in items))
        if abs(float(self.point) - expected) > DEFAULT_RULES.anchor_point_tol:
            raise ValueError("point must equal market_mid + sum(delta), clipped to [0.01, 0.99]")
        object.__setattr__(self, "corrections", items)
        object.__setattr__(self, "triggers", tuple(self.triggers or ()))


@dataclass(frozen=True)
class BrierComparison:
    anchor_brier: float
    market_brier: float
    difference: float


def brier(prob, outcome):
    """Squared error. outcome is 0 or 1."""
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    probability = require_unit_interval(prob, "prob")
    return (probability - float(outcome)) ** 2


def compare_to_market(cards, outcomes, market_probs, rules=DEFAULT_RULES):
    """D8. difference = anchor Brier − market Brier over the same outcomes."""
    del rules
    if isinstance(cards, str) or isinstance(outcomes, str) or isinstance(market_probs, str):
        raise ValueError("cards, outcomes, and market_probs must be sequences")
    card_list = tuple(cards)
    outcome_list = tuple(outcomes)
    market_list = tuple(market_probs)
    if not card_list or not (len(card_list) == len(outcome_list) == len(market_list)):
        raise ValueError("cards, outcomes, and market_probs must be non-empty and the same length")
    anchor_scores = [brier(card.point, outcome) for card, outcome in zip(card_list, outcome_list)]
    market_scores = [brier(prob, outcome) for prob, outcome in zip(market_list, outcome_list)]
    anchor_mean = sum(anchor_scores) / len(anchor_scores)
    market_mean = sum(market_scores) / len(market_scores)
    return BrierComparison(anchor_mean, market_mean, anchor_mean - market_mean)
