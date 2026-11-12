"""Thresholds for the judge library. Every number lives here."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    """Frozen thresholds. Comments cite the decision-table id, or the task section when there is no id."""

    # 任务书第 2 节，没有 D 编号。tech 为 0.04 × p × (1 − p)，geo 为 0。
    tech_fee_coef: float = 0.04
    geo_fee_coef: float = 0.0

    # D24。混合锚默认权重。
    blend_weight: float = 0.5

    # D45。样本量和权重。
    anchor_n_mid: int = 30
    anchor_n_high: int = 60
    anchor_positive_ratio_min: float = 0.6
    anchor_weight_default: float = 0.5
    anchor_weight_mid: float = 0.65
    anchor_weight_high: float = 0.75
    anchor_weight_negative: float = 0.4

    # 任务书第 2 节第 7 步，没有 D 编号。S / A / B 的下界。
    grade_s_min: float = 0.15
    grade_a_min: float = 0.08
    grade_b_min: float = 0.04

    # D7。S 全凯利，A 半凯利，B 只观察。
    kelly_s_multiplier: float = 1.0
    kelly_a_multiplier: float = 0.5
    kelly_b_multiplier: float = 0.0
    # D7。S 档金额超过余额的这个比例时，提示要写理由。
    s_reason_balance_fraction: float = 0.25
    # D7。A 档金额上限占余额的比例。
    a_cap_balance_fraction: float = 0.35

    # D73 第 2 条、D14。市价首笔不超过计划的这个比例。
    market_order_max_fraction: float = 1.0 / 3.0
    # D10、D21。越深权重越大。
    ladder_weights: tuple = (1, 2, 3, 4)
    # D10、D21。GTD 挂单多少小时后过期。
    gtd_expire_hours: float = 8.0
    # D9。跳变窗口内金额乘上这个比例。
    jump_window_amount_scale: float = 0.5

    # D20、D44。默认偏离门槛。
    deviation_threshold: float = 0.12
    # D20、D44。有硬信息时的门槛。
    hard_info_threshold: float = 0.08
    # D31。价差大于这个值视为薄盘，门槛一律回到默认值。
    thin_spread: float = 0.06

    # D22。相对一日中位数的偏离达到这个值，提示先过新闻分诊。
    news_triage_deviation: float = 0.15

    # D11。这些类别直接拒绝。
    rejected_categories: tuple = ("esports", "btc_short", "novelty", "sports")

    # D25。同一驱动因素合计超过余额的这个比例时提示。
    driver_concentration_fraction: float = 0.35
    # D25。下单后现金低于余额的这个比例时提示。
    min_cash_fraction: float = 0.30

    # D73 第 1 条。单一事件在险超过总资产的这个比例时提示。
    event_risk_fraction: float = 0.10

    # 任务书第 2 节 SOP 第 7 步 C 打法，没有 D 编号。
    c_play_single_fraction: float = 0.05
    c_play_daily_fraction: float = 0.15

    # D37。锚点截断区间。
    anchor_point_min: float = 0.01
    anchor_point_max: float = 0.99
    # D37。point 与截断后的合计允许的绝对误差。任务书没写公差。
    anchor_point_tol: float = 1e-12

    # 任务书第 2 节 CLV。小时数来自函数名里的 72。抽样次数和区间端点任务书没写。
    clv_hours: float = 72.0
    clv_n_boot: int = 2000
    clv_ci_alpha: float = 0.05


DEFAULT_RULES = Rules()


def require_unit_interval(value, name):
    """Prices and probabilities must lie in the open interval (0, 1)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a real number in (0, 1)")
    if not 0.0 < float(value) < 1.0:
        raise ValueError(f"{name} must be in (0, 1)")
    return float(value)


def require_positive(value, name):
    """Balances and notionals must be strictly positive."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive amount")
    if float(value) <= 0.0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def require_non_negative(value, name):
    """Spreads, deviations, and similar magnitudes cannot be negative."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a non-negative number")
    if float(value) < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return float(value)


def clip_unit(value, rules=DEFAULT_RULES):
    if value < rules.anchor_point_min:
        return rules.anchor_point_min
    if value > rules.anchor_point_max:
        return rules.anchor_point_max
    return value
