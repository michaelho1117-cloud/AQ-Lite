# T39 红队审查：T36 回测与 AS1H 前向记录

审查人：z2（红队）。日期：2026-11-13。分支 `t39`。
方法：不相信任何交付结论——独立写最小实现复算全部关键数字、逐行读代码、用构造输入离线测试、核对哈希；所有数字由 `t39_out\tools\` 里的脚本打印，原样输出贴在本文对应小节（存档在 `t39_out\out\`）。未修改 `audit_t39\` 的任何文件；建议的代码修改在 `t39_out\patches\`。

---

## 一页结论

**1. T36 的结论还站得住吗？——计算层面站得住，统计解读站不住。**

- **计算层面**：我从 `data_t36\` 独立重写了结算时刻解析（含夏令时）、快照、热门、手续费和两格预注册的全部逻辑，复算结果与交付**逐项吻合**（137 期主样本、2 个剔除事件、CAL 90 行、两格 22/27 笔交易逐字段一致、pooled 均值一致）；2138 个快照无一晚于决策时刻（无前视偏差）；`sha256.txt` 与文件实际哈希一致（4/4）；冻结脚本复跑差异仅为浮点末位（Python 3.12 `sum()` 补偿求和所致，不影响任何数字的比较）。
- **统计层面**：留出段「17 期全胜，每 $1 +0.026，p = 0.0，通过」里的 **p = 0.0 是全胜样本的退化值**——所有交易 pnl>0 时每个自助重抽均值必然 >0，p=0 对任意样本量机械成立（n=3 也一样）。改用二项分析：合并 44 期全胜（训练 27 + 留出 17，平均进场 0.9733）的**保本失败率是 2.57%**；若真实失败率恰为保本率，观察到 0/44 的概率是 **0.318**；0 失败的 Clopper-Pearson 95% 上界是 **6.58%**，远高于保本率。也就是说：**留出段结果与「存在小幅正期望」一致，但同样与「进场价就是公允价」一致，没有确立任何边际**。「133 期全胜」重新加总成立（99+34，无重叠、无重复计入；其中 1 期是 Play Store，App Store 口径为 132 期），但价格 ≥0.8 的热门全胜与市场校准良好相容（0.8–0.9 档 11/11、0.9–0.95 档 15/15 的二项检验都不显著），它本身不是超额收益的证据。

**2. AS1H 的记录可信吗？——当前脚本会漏记和双记，先打补丁再继续攒样本。**

- **会漏**：检查点失败（Apple 504、CLOB/gamma 瞬时错误）后 `done` 照样标记——该期 RSS60/RSS10 被永久跳过且无重试（构造测试证实）。丢失对 RSS60 是选择性的（网络抖动与行情无关，尚不算定向偏差，但样本悄悄变小、无对账痕迹）。
- **会双记**：进程在写 paper.jsonl 之后、写 done.json 之前被杀，重启补跑会产生重复 paper_buy；恢复运行的 `settle()` 在同一轮里把两条相同交易**各结算一次（pnl 双记）**（构造测试证实）。
- **会卡死**：`settle()` 只认字符串 `"1"/"0"`，接口格式一变（`"1.0"`、数字）成交就永久静默卡住；50/50 结算同样静默卡住（构造测试证实）。
- 边界项大都正确：夏令时切换周、跨年、占位过滤、`fill()` 多档成交、403/429 立即停、窗口「不早到最多晚 15 分钟」全部按文档工作（41 项构造测试全过）。
- **判定规则判定力不足**（先于任何记录问题）：「20 期每 $1 均值 > 0 且最多输 1 期」在进场 0.975 时等价于「20/20 全胜」，而即使 20/20 全胜，失败率的 95% 置信上界仍高达 **13.9%**，是保本失败率（2.4%）的近 6 倍——通过无法区分「有边际」与「无边际但价格公允」，只能排除粗大失败。在保本失败率下该规则有 **61.5%** 的概率误通过。
- Apple RSS 与结算榜单的同源性无法离线验证；dryrun 已提供实证线索（legacy iTunes feed 付费榜 #1 是 Minecraft（游戏），新营销 RSS 是 Shadowrocket），脚本记录 rss_updated/legacy_top5 的做法是对的，建议再记完整 top10 和结算胜出者。

**3. 最该先修的三件事**

1. **AS1H 打补丁**（`t39_out\patches\as1h_patched.py`，4 处改动，21 项验证测试全过）：失败检查点重试+漏检日志、结算去重+格式容错+卡单日志、前缀匹配双向 ≥4 字符、outcomes/完整 top10 记录。
2. **改判定统计**：RSS60 的「通过」改成「观察失败率的置信上界 < 保本失败率」类检验（或把期数提到 50+），并写明「20 期」指有 RSS60 成交的期还是全部事件（现文有歧义）；在此之前，任何通过/不通过都不应解读为边际存在/不存在。
3. **冻结复现环境**：登记 T36 生成环境的 Python 版本（≥3.12 的 `sum()` 与 3.9 有 ULP 级差异），或约定数值比较用 1e-9 相对容差——否则以后每次复跑都会出现「末位不同」的假阳性。

发现分级汇总：T36：major 1、minor 4、note 5；AS1H：major 3、minor 3、note 5。共 21 条，见 `findings.csv`（无 blocker：预注册流程、数据、计算本身没有发现错误；major 集中在统计解读与 AS1H 记录完整性）。

---

## WS1 审 T36

### WS1.1 独立复算

实现说明（`tools\ws1_recompute.py`，不调用 `t36_out\` 的任何代码）：

- 结算时刻：自己的美东夏令时实现（EDT = 3 月第 2 个星期日至 11 月第 1 个星期日，noon ET → 16:00Z/17:00Z），日期来源按 T36 记录的口径（description 有完整日期用之，否则标题月日 + endDate 的美东/UTC 日期对位，双不匹配 = date_conflict）。
- 快照：严格早于 t 的最后一个价格点、年龄 ≤ 2h（线性扫描实现，与交付的二分实现独立）。
- 热门：只在有价格历史且有快照的候选里排，最高价并列则该时刻无热门；胜出者 = outcomePrices 恰好一个 "1" 的候选。
- 两格预注册：快照价 ∈ 区间即按快照价 + 2 跳进场（0.001 跳界外），持有到结算，pnl 含 `0.04·p·(1−p)` 手续费。

原样输出：

```
HIST_FILES n=725
MAIN counts:
  1-paid-app: n=46
  1-free-app: n=50
  2-free-app: n=40
  1-grossing-play-store: n=1
  ALL: n=137
EXCLUDED: [('1-free-app', '637589', 'date_conflict'), ('2-free-app', '637588', 'date_conflict')]
DST spot checks (own impl): 2025-10-31-> 16:00Z 2025-11-02-> 17:00Z 2025-11-03-> 17:00Z 2026-03-07-> 17:00Z 2026-03-08-> 16:00Z
CELL a_fav_24h_bin090_095: n=22 wins=22 mean_2j_fee=0.05122873924847286
CELL a_fav_1h_bin095_098: n=27 wins=27 mean_2j_fee=0.026786236624058095
LOOKAHEAD snapshots_checked=2138 with_ts_ge_t=0  hist_points_at_or_after_settle=14144
AGE a_fav_24h_bin090_095: min=548s max=1149s mean=614s over_1h=0
AGE a_fav_1h_bin095_098: min=548s max=597s mean=579s over_1h=0

==== DIFF vs delivered ====
DIFF CAL ws1/stdout.txt: IDENTICAL (90 lines, 21 lines differ only at float ULP)
DIFF CAL a_fav_24h_bin090_095/rule.md: IDENTICAL (90 lines, 21 lines differ only at float ULP)
DIFF CELL a_fav_24h_bin090_095: IDENTICAL (5 rows, CI fields excluded, float ULP tolerated)
DIFF TRADE a_fav_24h_bin090_095: delivered=22 mine=22 field_mismatches=0
DIFF CAL a_fav_1h_bin095_098/rule.md: IDENTICAL (90 lines, 21 lines differ only at float ULP)
DIFF CELL a_fav_1h_bin095_098: IDENTICAL (5 rows, CI fields excluded, float ULP tolerated)
DIFF TRADE a_fav_1h_bin095_098: delivered=27 mine=27 field_mismatches=0

WROTE t39_out/ws1_summary.json
```

两格的复算均值与交付一致到 1 ULP（0.05122873924847285 vs ...86、0.0267862366240581 vs ...095）；每笔交易的 `snapshot_ts / snapshot_price / entry_2j / won / pnl_2j_fee / app / condition_id` 逐字段零差异。「133 期全胜」加总与范围见 WS1.4 和 findings T36-2。

### WS1.2 前视偏差

- 逐快照审计：CAL 三个 horizon × 全部候选共 2138 个快照，`snapshot_ts < t` 全部成立（0 个违例）。历史文件里确实存在 14,144 个结算时刻之后的价格点（结算跳 0/1），但快照二分/线性扫描都严格取 `< t` 且 `t < 结算时刻`，这类点结构上不可能入选。
- 热门只在没有前视的快照集合里排；胜出者只用作结算结果，不进决策。
- 胜出者无价格历史的事件（训练 28 期）按口径留在样本、热门即输——这对规则 A 是保守方向，不是有利于结论的偏差。
- 快照年龄：两格交易年龄 544–1149 秒（≤19 分钟），无超过 1 小时的陈旧快照。

### WS1.3 口径：快照价 + 2 跳 是否足以代表可成交价

方法：对每个事件每个 horizon 的热门，取其快照之后、结算前 1 分钟之前的历史价格点（纯诊断，不参与任何 T36 决策），度量「快照后第一个点相对快照的变动」（约 0–10 分钟的时效风险，按快照价的跳为单位）。原样输出（`tools\ws1_spread.py`）：

```
MOVE Analysis: snapshot staleness vs tradable price (train, favorites with snapshot)
  h=24: favorites=122  signed move1: n=122 mean=-1.18 up>2ticks=9/122 down>2ticks=7/122
  h=24: favorites=122  move1(first pt after snap): n=122 med=0.00 p90=2.30 p95=6.50 max=110.00 ticks | <=2ticks: 106/122
       moveMax(any pt before settle-1min): n=122 med=22.00 p90=71.00 p95=93.65 max=986.00 ticks | <=2ticks: 0/122
       movePre(last pt before settle-1min vs snap): n=122 med=15.00 p90=62.90 p95=77.50 max=986.00 ticks | <=2ticks: 7/122
  h=6: favorites=122  signed move1: n=122 mean=-0.10 up>2ticks=10/122 down>2ticks=9/122
  h=6: favorites=122  move1(first pt after snap): n=122 med=0.00 p90=3.00 p95=3.55 max=10.00 ticks | <=2ticks: 103/122
       moveMax(any pt before settle-1min): n=122 med=14.50 p90=55.50 p95=63.50 max=654.50 ticks | <=2ticks: 6/122
       movePre(last pt before settle-1min vs snap): n=122 med=10.00 p90=44.00 p95=56.50 max=654.50 ticks | <=2ticks: 13/122
  h=1: favorites=122  signed move1: n=122 mean=+0.07 up>2ticks=16/122 down>2ticks=8/122
  h=1: favorites=122  move1(first pt after snap): n=122 med=0.10 p90=3.70 p95=7.00 max=34.00 ticks | <=2ticks: 98/122
       moveMax(any pt before settle-1min): n=122 med=3.00 p90=17.50 p95=27.00 max=465.50 ticks | <=2ticks: 49/122
       movePre(last pt before settle-1min vs snap): n=122 med=2.00 p90=16.50 p95=25.00 max=465.50 ticks | <=2ticks: 60/122

CELL-STABILITY a_fav_1h_bin095_098 (train): t-1h snapshot in [0.95,0.98) ->
  FLIP event=364455 fav@t-1h=0.9735 (ChatGPT) -> fav@t-10min=0.988 (ChatGPT)
  FLIP event=388872 fav@t-1h=0.973 (ChatGPT) -> fav@t-10min=0.992 (ChatGPT)
  FLIP event=183243 fav@t-1h=0.9605 (UpScrolled) -> fav@t-10min=0.985 (UpScrolled)
  FLIP event=364463 fav@t-1h=0.979 (HBO Max: Stream Movies & TV) -> fav@t-10min=0.9935 (HBO Max: Stream Movies & TV)
  in-bin at t-1h: 27; same app+bin at t-10min: 23; changed: 4
```

解读：h=1 时 80%（98/122）的快照后 10 分钟变动 ≤2 跳，带符号漂移均值 ≈0（+0.07 跳，无系统性上偏），说明「快照价 + 2 跳」在多数情况下是充分的；但约 20% 的期次 10 分钟内变动超过 2 跳（上移 16 次 vs 下移 8 次），尾部到 34 跳（0.034）——对格内平均 +0.026/每$1 的边际，这类期次的真实进场成本可能显著更高。moveMax/movePre 大是持仓风险本身（价格走向 0/1），不是进场成本。另见 CELL-STABILITY：15% 的格内交易在 t-10min 时已越出 [0.95,0.98)（全部向上越过 0.98；≥0.98 档训练 56/56 全胜，经济含义相近）。

### WS1.4 统计问题

原样输出（`tools\ws1_stats.py`）：

```
TRAIN h=1 favorites with price>=0.8 (my recompute): n=99 wins=99
HOLDOUT h=1 favorites with price>=0.8 (from delivered CAL lines): n=34 wins=34
CLAIM CHECK '133 straight wins': 99+34=133  wins 99+34=133

BINOMIAL P(0 failures in n | true failure rate f) = (1-f)^n
  n=1h cell holdout(17) 1h cell train(27) 1h cell pooled(44) all favs>=0.8 pooled(133)
  f=0.01   0.8429  0.7623  0.6426  0.2627 
  f=0.02   0.7093  0.5796  0.4111  0.0681 
  f=0.025  0.6502  0.5048  0.3282  0.0345 
  f=0.03   0.5958  0.4394  0.2618  0.0174 
  f=0.05   0.4181  0.2503  0.1047  0.0011 
  f=0.1    0.1668  0.0581  0.0097  0.0    

Clopper-Pearson 95% UPPER bound on failure rate given 0 failures in n:
  n= 17 (1h cell holdout): 0.1616
  n= 27 (1h cell train): 0.1050
  n= 44 (1h cell pooled): 0.0658
  n=133 (all favs>=0.8 pooled): 0.0223

DEGENERATE BOOTSTRAP: with every trade pnl>0, every resample mean is >0, so p=0.0
  mechanically for ANY n (even n=3). The delivered train n=6 cell (h=1 [0.8,0.9),
  all 6 win) would print p=0.0 too. The p-value adds nothing beyond 'min>0'.

BREAKEVEN failure rate f* (expected pnl = 0) and whether the data can establish it:
  train 1h cell (n=27): mean entry=0.9729 W=+0.0268 L=-1.0011 -> f*=0.0261
    0/27 wins: CP95 upper bound on f = 0.1050  edge NOT established (upper >= breakeven)
    P(0/27 | f=f*) = 0.4902  (binomial p-value against 'just breakeven')
  holdout 1h cell (n=17): mean entry=0.9738 W=+0.0259 L=-1.0010 -> f*=0.0252
    0/17 wins: CP95 upper bound on f = 0.1616  edge NOT established (upper >= breakeven)
    P(0/17 | f=f*) = 0.6482  (binomial p-value against 'just breakeven')
  pooled 1h cell (n=44): mean entry=0.9733 W=+0.0264 L=-1.0011 -> f*=0.0257
    0/44 wins: CP95 upper bound on f = 0.0658  edge NOT established (upper >= breakeven)
    P(0/44 | f=f*) = 0.3178  (binomial p-value against 'just breakeven')

MULTIPLE COMPARISONS: grid.csv rows=75 (all scopes), pooled rows=15
  pooled GATE cells=15, selected=2
  if each holdout test had size 0.05, family-wise error for 2 cells = 0.0975 (Bonferroni-bound 0.10)
  BUT the holdout statistic is the degenerate all-win bootstrap, so the nominal
  0.05 size does not hold; see BINOMIAL section for the proper test.
```

要点：① p=0.0 退化；② 更合适的说法已算出——观察 44 期全胜时真实失败率 2%/3%/5% 的概率分别为 0.411/0.262/0.105，CP95 上界 6.58% > 保本率 2.57%；③「133 期全胜」加总成立、无重叠（每期每 horizon 只计一个热门、训练/留出按结算日切分）；④ 多重比较：75 格（含分系列）→ pooled 15 格 → 2 格进留出段，名义族错误率 ≤9.75%，但统计量退化使其无意义；⑤ 附带发现：24h 格的留出段 p=0.6515 与「8 期 7 胜、−0.084」在结果文件里一致，验收方数字无误。

### WS1.5 代码审读、哈希与复跑

- 两份 `run.py` 除格子常量（NAME/HORIZON_H/BIN_LO/BIN_HI/BIN_LABEL）外逐行相同；与 `rule.md` 的规则文字逐条对照无发现不一致（区间开闭、并列处理、跳、手续费、bootstrap 顺序与种子、PASS 只在 holdout 认定，全部一致）。留出段可能的坑（跨年、缺历史、平局、`outcomePrices` 格式）在代码里都有处理路径：跨年由 endDate 美东/UTC 日期对位（构造测试见 T36-8 的两个真实事件）；缺历史 → FAV missing；平局 → 该期不做；`outcome_yes` 断言 YES 在 outcome 0。
- 哈希（`tools\check_prereg_hashes.py`）：

```
== T36 prereg sha256 ==
a_fav_24h_bin090_095/rule.md: OK b8ca0bbf415927eb94ae4c34fde59d8a4659344ddbdff04d5d64ef179d933fb8
a_fav_24h_bin090_095/run.py: OK 686a5503ed5909c2bdc414b1632c3336241db8adfb7eb99dff747692d1ed2c08
a_fav_1h_bin095_098/rule.md: OK 695e9e37d931fa7fbfb82fb431cdd43beefc4cc17e36987c3ab99c5a7b6a32d3
a_fav_1h_bin095_098/run.py: OK f1815ec3e92fbf6ef951189a0584c2dc9e7a6b3c378d2115f0e5616564e39599

== AS1H ==
as1h.py: OK 0c9136833ccd09d2430193b6d9926095f73d5f572b0a2d0f8d06f70b62f127ec
```

- 交付文件一致性：两格的 `result_holdout.txt` 与 `holdout_stdout.txt` 内容相同（后者是 UTF-16 编码，PowerShell 重定向所致）；两格 result 文件里的 CAL 表逐行相同（同一数据同一段代码，合理）。
- 冻结脚本复跑（`--split train`，本机 Python 3.9.6）：行数相同（131/131、136/136），差异只有浮点末位——CAL 21 行、CELL 3–4 行、PASS_CI95 1 行；n/wins/TRADE/P_ONESIDED 全部一致。判定为 Python ≥3.12 的 `sum()` Neumaier 补偿求和 vs 3.9 朴素求和（findings T36-3）。

```
a_fav_24h_bin090_095 differing tags: Counter({'CAL/CAL': 21, 'CELL/CELL': 3, 'PASS_CI95/PASS_CI95': 1})
a_fav_1h_bin095_098 differing tags: Counter({'CAL/CAL': 21, 'CELL/CELL': 4})
（逐行样例见 out\rerun_diff_out.txt：全部是最后 1-2 个有效数字的差异，如 mean_price=0.69875 vs 0.6987500000000001）
```

---

## WS2 审 AS1H

### WS2.1 逐行对照（as1h.py vs AS1H.md）

一致的部分：每 5 分钟运行（cron，外部）；两个检查点 60/10 分钟；窗口「不早到、最多晚 15 分钟」（构造测试 4 个边界全对）；RSS 取 Apps 分区前 10、付费/免费榜取第 1、免费榜第 2 取第 2；匹配唯一才成交；从最低卖单往上吃、只吃 ≤0.98、$50 上限、按档加权、`0.04·p·(1−p)` 手续费（构造测试逐项验证）；记录热门/一致性/买卖一/深度/RSS 更新时间；结算后 1 小时起结算；403/429 立即停；STOP 文件生效；sha256 一致。

不一致 / 文档未写全（详见 findings AS1H-1..11）：

| # | 位置 | 问题 |
|---|---|---|
| 1 | main() | **检查点失败被永久标为已做**（文档无失败处理条款；代码注释「never retry … more than once per run」与实际「从不重试」不符） |
| 2 | settle() | **中断重跑的重复 paper_buy 在同一轮被结算两次**；`px` 只认字符串 `"1"/"0"`（格式变化→静默卡死）；50/50 结算静默卡死 |
| 3 | match() | 前缀规则 ≥4 字符只约束盘方一侧；RSS 名规范化为空串时可误配（文档「去掉标点」与代码「去掉所有非字母数字」也有出入，代码行为更有利） |
| 4 | checkpoint() | 「两边的买一卖一」：target==fav 时只记一份；「价格热门」来源（outcomePrices 最近价）文档未指明；RSS 只记 top5（文档写「前 10 名」） |
| 5 | fill() | 「最多花 $50」只约束成本，手续费另计（总支出 ~$50.04） |
| 6 | refresh_events() | 事件缓存 30 分钟 + limit=20（文档未写）；gamma 单系列失败杀死整轮（无日志） |
| 7 | 判定节 | 「攒满 20 个事件」未定义是否要求有 RSS60 成交；判定统计的判定力不足（见 WS2.3） |

### WS2.2 边界情况构造测试

全部离线：把 as1h.py 以只读方式 import（禁写 bytecode，audit_t39 不产生任何文件），HOME 指到临时目录，网络函数 `get()` 换成构造 payload。原样输出（`tools\ws2_as1h_tests.py`，41 项全过；完整见 `out\ws2_tests_out.txt`）：

```
== resolve_ts: DST boundaries and year disambiguation ==
  PASS  fall-back day (Nov 1 2026) -> EST noon 17:00Z  | got=2026-11-01T17:00Z
  PASS  day before fall-back (Oct 31 2026) -> EDT noon 16:00Z  | got=2026-10-31T16:00Z
  PASS  spring-forward eve (Mar 7 2026) -> EST 17:00Z
  PASS  spring-forward day (Mar 8 2026) -> EDT 16:00Z
  PASS  Dec 31 event with endDate next year (cross-year)  | got=2026-12-31T17:00Z
  PASS  title date != endDate date -> None (like the 2 excluded T36 events)  | got=None
  PASS  no '12:00 PM ET' in description -> None
== match(): ... ==
  PASS  exact / curly vs straight apostrophe / subtitle prefix (Vinted) / suffix ' - ' variant
  PASS  comma app "Instants, an Instagram app" vs Apple "Instants"  | got=prefix
  PASS  space stripped: 'Hot Schedules' vs 'HotSchedules'  | got=exact
  PASS  exact wins before prefix: 'Google' matches 'Google' not 'Google Gemini'
  PASS  NO MATCH: HBO Max subtitle wording differs (real-world near miss)  | got=none
  PASS  false prefix: 4-char RSS name 'Chat' matches ChatGPT (doc says >=4 chars, code checks only market side)
  PASS  short RSS name 'AI' prefix-matches 'AI Chatbot' (doc ambiguity)
  PASS  dup market names -> ambiguous
  PASS  BUG: RSS name all non-ASCII (norm='') -> c.startswith('') vacuously true -> lone >=4-char candidate falsely matches
== real(): placeholders filtered; 'Other' kept (9 train wins) ==
== fill(): empty asks / best ask>0.98 / multi-level partial fill / fee formula == PASS ×4
== checkpoint window: t<=NOW<t+15min == PASS ×4
== main(): checkpoint failure handling (constructed) ==
  PASS  FAILED checkpoint is permanently marked done (lost: no retry inside window)  | done.json=['e1:60']
  PASS  hard kill mid-run -> paper_buy recorded TWICE (duplicate ledger entry)
  PASS  BUG: duplicate buys from the interrupted run BOTH settle in the recovery run (pnl double-counted)
  PASS  outcomePrices string '1.0' / numeric 1: market closed+won but NOTHING settles (silent stall) ×2
  PASS  unresolved/open market -> skipped, retried next run
  PASS  403 -> run stops immediately (sys.exit, doc-conform)
  PASS  403 -> checkpoint key NOT marked done (retried next run)
  PASS  happy-path checkpoint: book walk correct (shares=51.5282), rss_updated/legacy_top5/depth recorded, target_is_fav=true
SUMMARY checks=41 failures=0
```

用 `events_train.json` 里出现过的候选名构造 Apple 可能的写法（大小写、弯/直引号、副标题、「- 」后缀、逗号名、商标符、空格、非 ASCII）共 12 例：9 例按预期匹配/不匹配，暴露 1 个真 bug（空串前缀误配）和 2 个文档歧义（4 字符约束的单侧性、短名误配）；「HBO Max: Stream TV & Movies」vs「HBO Max: Stream Movies & TV」这类副标题词序差不会匹配（漏配、按规则不成交，安全方向）。

### WS2.3 方法问题

**判定规则的误判率**（`tools\ws2_method.py`，解析解 + 20 万次 Monte Carlo 种子 7）：

```
1) constant entry portfolios
   entry W(win pnl/$1)  breakeven f*  max losses with mean>0
   0.820       +0.2123        0.1741                       3
   0.900       +0.1071        0.0964                       1
   0.940       +0.0614        0.0577                       1
   0.975       +0.0246        0.0240                       0
  P(pass | f) rows:
   entry f=0.0   f=0.01  f=0.02  f=0.024 f=0.03  f=0.05  f=0.1   f=0.15 
   0.975 1.000   0.818   0.668   0.615   0.544   0.358   0.122   0.039
2) mixed entry portfolio (dryrun 0.968/0.940/0.820): P(pass|f=0.024)≈0.917
3) 20/20 wins: Clopper-Pearson 95% upper bound on failure rate = 0.139  vs breakeven 0.024
```

结论：该规则在「完全无边际、价格公允」（f=保本率）时约 62%（高进场）/92%（混合进场）概率通过；即使最好情形 20/20 全胜，失败率上界 13.9% ≫ 保本率 2.4%——**通过不构成边际存在的统计证据**；反向在 f=10%（明确亏损）时仍有 12.2% 误通过。建议改判据（见 findings AS1H-7）。

**RSS 与 App Store Top Charts 的同源/延迟风险**（从现有材料能看出的）：

- 实证线索：dryrun 里 legacy iTunes RSS 付费榜 #1 是「Minecraft: Play with Friends!」（游戏），营销 RSS 是 Shadowrocket——两个 feed 确实不同；市场规则按「overall Top Charts under 'Paid Apps'」结算（Apps 分区不含游戏），营销 RSS 与规则一致的假设合理但离线不可证。
- 延迟：dryrun 的 `rss_updated` 与抓取同分钟，说明营销 RSS 刷新不慢于小时级；但 RSS 刷新节奏与结算参考的实时榜单是否同步无法离线验证。
- 应该额外记录的（补丁已做一部分）：完整 top10（原来只记 top5）；T-60 与 T-10 两次榜单差异；**结算时市场实际判给的胜出者名字**（现在 settled 记录只有 win 布尔）——三者对齐才能事后算「RSS60 预测 vs RSS10 预测 vs 结算结果」的一致率，检验同源性。
- 残余风险：RSS 与 App Store 应用内榜单若在某天不一致（苹果换源、分区调整），记录能发现但脚本不能防；这是「提前记录、事后审计」的定位。

### WS2.4 patches

`t39_out\patches\`：`as1h_patched.py`（4 处改动，源码内 `# T39:` 标注）、`as1h.patch`（统一 diff）、`README.md`（逐条原因）。验证：`python -I tools\ws2_patch_tests.py` 21 项全过（失败重试+漏检日志、同轮结算去重、`"1.0"`/数字结算价、`settle_stuck` 可见、前缀双向 ≥4 字符、outcomes 检查、top10 记录、403 行为与 happy-path 不回归）。

原样输出（节选，完整见 `out\ws2_patch_tests_out.txt`）：

```
  PASS  FIXED: all-non-ASCII RSS name no longer falsely matches  | got=none
  PASS  FIXED: sub-4-char RSS name ('AI') no longer prefix-matches  | got=none
  PASS  failed checkpoint NOT marked done  | done=[]
  PASS  expired window logged once as checkpoint_missed and marked done  | done=['e1:60']
  PASS  duplicate buys settle ONCE
  PASS  FIXED: outcomePrices '1.0' now settles
  PASS  closed but 50/50 -> logged once as settle_stuck (visible), not settled
  PASS  403 still stops immediately / leaves key unmarked
  PASS  happy-path checkpoint unchanged (rss_top10 added, trade correct)
SUMMARY checks=21 failures=0
```

---

## 待用户决定

1. 留出段 53 期的构成：两个 date_conflict 事件（637588/637589，标题 July 3、endDate 6-26）按标题日期落在留出窗口，本地留出数据不可见，无法确认验收方是否按同一规则剔除（results 文件显示 holdout 数据不含它们）。请在验收环境跑一次 `run.py --split holdout` 并核对 `EXCLUDED`。
2. AS1H 判定口径：「20 个事件」= 有 RSS60 成交的 20 期，还是 20 个自然事件（含未成交/未匹配期）？判定前必须写死；同时建议采纳 findings AS1H-7 的判据修改（新登记）。
3. 是否采纳 `patches\as1h_patched.py` 替换线上脚本（改动会偏离 AS1H.md 登记的 sha256，需要按「改规则必须新登记」处理——补丁不改变记录规则本身，只修实现缺陷，请登记方确认处理方式）。
4. T36 预注册两格的 PASS 判定是否改用二项/区间判据重述结论（findings T36-1）；这不改历史数据，只改结论的表述与解读。

## 复现

```
cd /d D:\NISA\z2\repo
python -I -X utf8 t39_out\tools\ws1_recompute.py      (写 t39_out\ws1_summary.json)
python -I -X utf8 t39_out\tools\ws1_spread.py
python -I -X utf8 t39_out\tools\ws1_stats.py          (依赖 ws1_summary.json)
python -I -X utf8 t39_out\tools\rerun_runpy_train.py
python -I -X utf8 t39_out\tools\rerun_diff_tags.py
python -I -X utf8 t39_out\tools\check_holdout_files.py
python -I -X utf8 t39_out\tools\check_prereg_hashes.py
python -I -X utf8 t39_out\tools\ws2_as1h_tests.py
python -I -X utf8 t39_out\tools\ws2_method.py
python -I -X utf8 t39_out\tools\ws2_patch_tests.py
python -I -X utf8 t39_out\tools\make_findings.py      (重建 findings.csv)
python -I -X utf8 t39_out\tools\make_patch_diff.py    (重建 patches\as1h.patch)
```

全部只用标准库、不联网、不写 `audit_t39\`。环境：Python 3.9.6 / Windows，git 2.53（仅 clone/push 分支 t39）。本文不构成交易建议。
