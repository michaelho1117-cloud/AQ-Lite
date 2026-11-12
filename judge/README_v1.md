# judge

下单前的纯函数：输入数字，输出金额、档位和提示。不联网，不读写文件，不读环境变量，不下单。阈值都在 `judge/config.py` 的 `Rules`。除自助抽样外不用随机数；抽样必须传入 `seed`。

价格和概率要在 (0, 1)，金额不能为负，否则抛 `ValueError`。纪律检查只在任务书写明「拒绝」时把 `ok` 设为 False；其余情况 `ok` 仍为 True，提示在 `notes` 里。

## 函数

- `taker_fee_per_share`：tech 收取 `tech_fee_coef × p × (1 − p)`，geo 收取 `geo_fee_coef`。出处是任务书第 2 节，没有 D 编号。
- `blend`：`w × anchor + (1 − w) × market`。D24。
- `anchor_weight`：按 CLV 账本决定混合权重。D45。
- `edge`：买 YES 为 `fair − (ask + fee)`，买 NO 为 `(1 − fair) − (no_ask + fee)`。任务书第 2 节。
- `grade`：按 edge 分 S / A / B，更低为 None；红旗降档。任务书第 2 节第 7 步。
- `kelly_fraction`：买 YES 为 `(fair − price) / (1 − price)`，买 NO 用 NO 的概率和价格，结果截到 [0, 1]。任务书第 2 节。
- `position_size`：S 全凯利，A 半凯利，B 为 0。D7。
- `tranche_plan`：市价首笔不超过计划的 1/3，其余按权重分到限价档。D73 第 2 条、D14；权重 D10、D21。
- `overnight_gtd`：GTD 挂单 8 小时过期；跳变窗口内金额减半。D10、D21、D9。
- `threshold_check`：偏离不到门槛则拒绝；薄盘一律用默认门槛。D20、D44、D31。
- `news_triage_required`：偏离一日中位数达到门槛时提示先过新闻分诊。D22。
- `scope_check`：esports、btc_short、novelty、sports 拒绝。D11。
- `concentration_check`：同一驱动因素过重，或下单后现金过低，给出提示。D25。
- `event_risk_check`：单一事件在险过高时提示。D73 第 1 条。
- `downgrade_advice`：估值下调时，按新的混合锚给出应保留的份数和要卖的份数。D73 第 3 条。
- `c_play_check`：C 打法单笔或当天合计过高时提示。SOP 第 7 步，没有 D 编号。
- `jump_window_adjust`：跳变窗口内 S 降为 A。D9。
- `AnchorCard`：`point` 必须等于 `market_mid + Σdelta` 再截到 [0.01, 0.99]；修正必须有 `source_url`。D37、D103。
- `brier`、`compare_to_market`：锚和同期市价的 Brier，以及二者之差。D8。
- `clv_72h`：每笔 72 小时 CLV、按金额加权的均值、为正的比例，以及按事件自助抽样的区间。任务书第 2 节。

## 待用户决定

1. 多面红旗。条文是「任何红旗降一档」。现在按每面红旗降一档，降到 None 为止。如果无论几面都只降一档，需要改这一条。
2. 手续费系数、分档边界 0.15 / 0.08 / 0.04、C 打法的 5% 和 15%、自助抽样的 2000 次，任务书没有 D 编号。这些数在 `Rules` 里，注释写了小节。未知的手续费类别会抛 `ValueError`。
3. `anchor_weight`：加权 CLV 等于 0 时保持 0.5，不升档，也不降到 0.4。区间下限等于 0 视为没有达标。n ≥ 60 且 CLV < 0 时得到 0.4，因为升档要求 CLV > 0。
4. 分档边界按第 4 节的用例：0.15 是 S，0.08 是 A，0.04 是 B。S 是 edge ≥ 0.15，A 是 [0.08, 0.15)，B 是 [0.04, 0.08)。
5. S 档金额超过余额 25% 只提示「超过 25% 必须写理由」，不截断。恰好 25% 不提示。A 档半凯利超过余额 35% 才截断并提示。恰好 35% 不截断。B 和 None 的金额是 0。
6. 薄盘是价差 > 0.06。恰好 0.06 不改门槛。偏离 ≥ 门槛才通过。
7. 同一驱动因素合计 > 余额 35% 才提示。下单后现金 < 余额 30% 才提示。恰好 35% 或恰好 30% 不提示。`positions` 是下单前的仓位，现金 = 余额 − 已有金额 − 本笔金额。
8. 事件在险 > 总资产 10% 才提示。用例里的 200 / 2000 恰好是 10%，不提示。
9. `today_c_total` 不含本笔。本笔 > 余额 5%，或（已有 + 本笔）> 余额 15%，才提示。恰好等于不提示。
10. `downgrade_advice` 里的 `fair` 是 YES 概率，`price` 是所买那一边的价格。YES 下调指新概率更低；NO 下调指 YES 概率变高。混合锚在这一边的概率上，用默认权重和这一边的价格混合。份数上限用这一边的全凯利，不用半凯利。下调时目标份数不会高于现有份数。
11. `tranche_plan` 的市价首笔取计划金额的 1/3。限价档不是 4 档时，权重改成 1, 2, …, n。没有限价档会抛 `ValueError`。除不尽的余数加在最深一档，合计等于计划金额。
12. `overnight_gtd` 不重新分配 1:2:3:4。它给每一档写上 8 小时到期；`jump_window=True` 时金额乘 0.5。
13. `price_at(market, t)` 返回 YES 价。买 YES 的 CLV 是 72 小时 YES 价减去成交价。买 NO 的成交价是 NO 价，CLV 是 `(1 − 72 小时 YES 价) − 成交价`。CLV 等于 0 不算正。为正的比例按笔数，不按金额。自助抽样按事件编号有放回；抽中的事件，其成交全部计入，抽到几次就计几次。区间端点的下标是 `floor(0.025 × n_boot)` 和 `ceil(0.975 × n_boot) − 1`。默认 `n_boot` 是 2000。这些抽样细节任务书没有写死。
14. `AnchorCard.point` 与截断后的合计，绝对差不超过 `anchor_point_tol`（1e-12）才算相等。空白的 `source_url` 视为没有。`low` 和 `high` 的顺序任务书没有要求，这里不额外拒绝。
15. 类别比较忽略大小写。`Sports` 和 `sports` 一样拒绝。

## 测试输出

下面是 `python -m unittest discover -s tests_judge -v` 的完整输出。

```
test_brier_and_compare_to_market (test_anchors.AnchorTests.test_brier_and_compare_to_market) ... ok
test_case_9_source_and_point (test_anchors.AnchorTests.test_case_9_source_and_point) ... ok
test_case_12_hand_calc_and_same_seed (test_clv.ClvTests.test_case_12_hand_calc_and_same_seed) ... ok
test_no_fill_uses_the_complement_of_the_yes_price (test_clv.ClvTests.test_no_fill_uses_the_complement_of_the_yes_price) ... ok
test_case_7_concentration_check (test_discipline.ConcentrationAndRiskTests.test_case_7_concentration_check) ... ok
test_case_8_event_risk_check (test_discipline.ConcentrationAndRiskTests.test_case_8_event_risk_check) ... ok
test_c_play_single_and_daily (test_discipline.OtherDisciplineTests.test_c_play_single_and_daily) ... ok
test_downgrade_advice_cuts_to_kelly_and_does_not_add (test_discipline.OtherDisciplineTests.test_downgrade_advice_cuts_to_kelly_and_does_not_add) ... ok
test_jump_window_drops_s_to_a (test_discipline.OtherDisciplineTests.test_jump_window_drops_s_to_a) ... ok
test_news_triage_at_boundary (test_discipline.OtherDisciplineTests.test_news_triage_at_boundary) ... ok
test_scope_rejects_entertainment_only (test_discipline.OtherDisciplineTests.test_scope_rejects_entertainment_only) ... ok
test_case_6_threshold_check (test_discipline.ThresholdTests.test_case_6_threshold_check) ... ok
test_case_1_tech_half_and_geo_zero (test_fees.FeeTests.test_case_1_tech_half_and_geo_zero) ... ok
test_price_outside_open_unit_interval_raises (test_fees.FeeTests.test_price_outside_open_unit_interval_raises) ... ok
test_unknown_category_raises (test_fees.FeeTests.test_unknown_category_raises) ... ok
test_blend_default_weight (test_sizing.BlendAndAnchorTests.test_blend_default_weight) ... ok
test_case_2_anchor_weight (test_sizing.BlendAndAnchorTests.test_case_2_anchor_weight) ... ok
test_case_3_grade_boundaries_and_one_flag (test_sizing.EdgeGradeKellyTests.test_case_3_grade_boundaries_and_one_flag) ... ok
test_case_4_kelly (test_sizing.EdgeGradeKellyTests.test_case_4_kelly) ... ok
test_case_5_position_size (test_sizing.EdgeGradeKellyTests.test_case_5_position_size) ... ok
test_edge_yes_and_no (test_sizing.EdgeGradeKellyTests.test_edge_yes_and_no) ... ok
test_observe_grade_is_zero (test_sizing.EdgeGradeKellyTests.test_observe_grade_is_zero) ... ok
test_case_10_tranche_plan (test_sizing.TrancheTests.test_case_10_tranche_plan) ... ok
test_case_11_overnight_gtd_jump_window_halves (test_sizing.TrancheTests.test_case_11_overnight_gtd_jump_window_halves) ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.001s

OK
```
