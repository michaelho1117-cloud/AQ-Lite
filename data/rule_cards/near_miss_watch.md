# WS2 近邻与未合格候选模型观察清单（`t37_out/ws2/near_miss_watch.md`）

本清单基于对 `data_t37/markets_open.json`（111 个未结算事件、854 个子市场）、`t37_out/tools/merged_timeline.json`（293 条记录，数据快照截止 `2026-11-11`）、`data_t37/signals.csv`（至 `S0913`）以及 `data_t37/addendum_after_2026-11-11.md`（补充 `2026-11-12` `Gemini 4 Hydrogen` 发布事实）逐条原文比对整理。**仅作规则字面核查与未来触发条件记录，不包含任何交易建议或概率/买卖评价。**

状态分类约定：
- **`BENCHMARK_READY`**：候选模型已在时间线发布且满足基准盘的命名/版本/时间创建门槛，仅等待在指定外部榜单完成首次亮相（非 `AutoEval`）或特定查榜时刻排名达标即可结算对应档位。
- **`BLOCKED_NEAR_MISS`**：已公开发布或开放权重的紧邻型号/衍生变体，因规则明文点名排除、版本号未达下限、系列标签缺失或访问阶段受限而被阻断。
- **`SIGNAL_ONLY_UNRELEASED`**：仅在代码日志、盲测别名、高管/官号预告或延期报道中现身，尚未公开可用。

---

## 汇总一览表

| 实验室 | 候选模型 / 信号 | 状态 / 时间（ET） | 关联 WS2 未结事件（slug） | 观察分类 | 阻断条款 / 待触发核心要件 |
|---|---|---|---|---|---|
| Alibaba | `Qwen4-Max-Preview` (`[291]/[292]`) | `preview` (`2026-11-10`, Token Plan) | `next-qwen-max-model-3pt9-text-arena-debut-20261106` | `BENCHMARK_READY` | 模型已面世且满足 `Max` + `>=3.9`，待非 `AutoEval` 登 Arena 总榜并留至次日 12:00 PM ET |
| Alibaba | `Qwen4-Max-Preview` (`[291]/[292]`)、`S0858`/`S0868` | 同上；`Plus/Flash/27B` 未发 | `next-alibaba-qwen-plus-3pt8-released-byptptpt`、`next-qwen-flash-3pt9-released-byptptpt` | `BLOCKED_NEAR_MISS` | 缺 `Plus` / `Flash`（仅 `Max` 在 Token Plan 预览）；即使后续上线亦须核查非 Token Plan 封闭预览 |
| Anthropic | `Claude Fable 5.2` (`[287]`, `S0871`/`S0873`) | `general` (`2026-11-09`) | `next-fable-model-5pt2-humanitys-last-exam-debut-20260928`、`next-fable-model-5pt2-text-arena-debut-20260928`、`next-fable-model-5pt2-text-arena-rank-debut-20261027`、`best-ai-model-on-november-16` | `BENCHMARK_READY` | 晚于 09-28/10-27 建盘且符合 `Fable 5.2+`，待首登 HLE / Arena 次日 12:00 PM ET；但在 11-16 枚举盘只能进 `Other` |
| Anthropic | `Claude Mythos 5.2` (`[288]`)、`Opus/Sonnet/Haiku 5.5` (`[255]/[262]/[268]`) | `limited` (`11-09`)；`general` (`09-22..10-07`) | `claude-6-released-byptptpt`、`next-claude-haiku-5pt6...`、`next-claude-opus-5pt6...`（3 盘）、`next-claude-sonnet-5pt6...` | `BLOCKED_NEAR_MISS` | `Fable 5.2` / `Mythos 5.2` 版本 `< 6` 且后者仅限可信认证；`5.5` 系列全部低于 `5.6` 且按系列点名排除 |
| OpenAI | `GPT-6.1 Terra` (`[278]/[279]`) | `paid_users`+`api` (`2026-10-26`) | `next-gpt-terra-model-5pt7-text-arena-debut-20261022` | `BENCHMARK_READY` | 本盘建于 `10-22`、门槛 `5.7+`；虽未上免费 Chat，但规则明言此前可访范围无关，待非 `AutoEval` 登 Arena |
| OpenAI | `GPT-6.1 Sol` (`[263]/[264]`)、`GPT-6.1 Terra` (`[278]`)、`GPT-6 Astra` (`[249]/[250]`)、`GPT-6 Cyber` (`[285]`)、`GPT-6 Rosalind` (`[282]`) | `paid_users`/`limited` (`09-03..11-05`) | `gpt-astra-6pt1-released-byptptpt`、`gpt-astra-6pt1-released-onptptpt`、`when-will-gpt-astra-6pt1-be-released-20261020`、`next-gpt-sol-6pt2...`、`next-gpt-terra-6pt2...`、`next-gpt-luna-6pt1...` | `BLOCKED_NEAR_MISS` | Astra 6.1+ 排除了 `GPT-6 Astra`、全部 `Sol/Terra/Luna` 及 `Cyber` 专用线；`6.1 Sol/Terra` 低于 `6.2` 门槛 |
| OpenAI | `GPT-6.1 Astra` (`S0820`)、`gpt-6.2-astra` canary (`S0859`/`S0867`/`S0869`) | 已搁置；Codex 金丝雀/延期 (`11-01..11-07`) | 全部 `gpt-astra-6pt1*` 与 `next-gpt-sol/terra-6pt2*` | `SIGNAL_ONLY_UNRELEASED` | 服务端 canary 属私测被禁，且 `11-06/07` 预期窗口已确认推迟未发；未来若发无 tier 的 `6.2 Astra` 需关注“Astra-branded”字面条件 |
| Google | `Gemini 4 Carbon` (`[280]/[289]/[290]`)、`Gemini 4 Argon` (`[265]/[271]-[273]`)、`S0849`/`S0912` | `general` (`11-10` / `10-13`) | `next-google-gemini-pro-model-released-byptptpt`、`...arena-debut`、`...humanitys-last-exam-debut...`、`next-gemini-argon-released-byptptpt-20261014` | `BLOCKED_NEAR_MISS` | 元数据标 `tier=Pro`，但官方名与 ID 均不含 `"Pro"` 字样；`Carbon` 亦不含 `"Argon"`（尽管曾在 LM Arena 以 `gemini-4-argon` 盲测） |
| Google | `gemini-omni-1.1-flash` (`S0864`)、`gemini-omni-1.2-flash` (`S0866`)、`Gemini 3.8 Flash` (`[247]`)、`Gemini 4 Cyber Permissive` (`S0911`) | OpenRouter (`11-04`/`11-05`)；`3.8 Flash` (`09-02`) | `next-gemini-flash-model-3pt9-released-byptptpt`、`next-gemini-flash-lite-model-3pt6...`（2 盘） | `BLOCKED_NEAR_MISS` | 规则显式排除 `"Gemini Omni Flash"`、`"Gemini Flash Cyber"`、`Flash-Lite` 缺位及版本 `< 3.9` |
| Google | `Gemini 4 Hydrogen`（`gemini-4-hydrogen`，无别名，`addendum` 补充） | `general`（`2026-11-12T18:00:00Z`，Stable） | `next-gemini-flash-model-3pt9-released-byptptpt`、`next-gemini-flash-lite-model-3pt6...`（2 盘）、`next-google-gemini-pro-model...`（3 盘）、`next-gemini-argon...`、`best-ai-model-on-november-16` | `BLOCKED_NEAR_MISS`（各命名盘）/ 候选路由（11-16 `Other` & 公司榜） | 博客定位快速普及版并以 `3.8 Flash` 迁移对比，但正式名与 ID 不含 `Flash` / `Flash-Lite` / `Pro` / `Argon`，且 `gemini-flash-latest` 截至 `2026-11-13` 未指向它；11-16 若排 #1 归入 `any other model` |
| Meta | `Muse Spark Open` (`[274]`)、`Muse Wonder / Wonder Full` (`[269]/[270]`)、`Muse Ember` (`[286]`)、`Muse Spark 1.3` (`[248]`) | `open_weights`/`api` (`09-02..11-09`) | `next-muse-spark-1pt4-released-byptptpt`、`next-muse-spark-model-1pt4-released-onptptpt`、`next-muse-wonder-1pt1-released-byptptpt` | `BLOCKED_NEAR_MISS` | `Muse Spark Open` 虽含 `Muse Spark` 但无 `1.4+` 编号；`Muse Ember` 虽由 Wonder Full 蒸馏但名字不含 `Wonder` 也不含 `Spark`；初代 `Muse Wonder` 被点名排除 |
| DeepSeek | `DeepSeek-V4.1-Flash-1017` (`[275]`)、`DeepSeek-V4-Pro GA` (`[237]`) | `open_weights` (`10-16` ET) / `api` (`08-13`) | `next-deepseek-flash-released-byptptpt-20261021-02`、`next-deepseek-pro-released-byptptpt` | `BLOCKED_NEAR_MISS` | `V4.1-Flash-1017` 及将其指向 `deepseek-flash` 别名被点名排除；明确禁止沿用同 ID 静默升级 |
| Moonshot | `Kimi K3.1 Pro` (`[277]` API `10-23` / `[283]` HF 建仓 `11-01` ET) | `api` & `open_weights` | `next-kimi-k-model-3pt2-released-byptptpt`、`kimi-k4-released-by-20260722184115883` | `BLOCKED_NEAR_MISS` | HF 权重释出被点名排除（`"including any open-weight release, rollout, or snapshot"`）；`3.1 < 3.2` 更低于 `K4` |
| Mistral | `Mistral Large 4` / `le Chonk` (`[266]/[267]` API 预览 `10-06` / `[281]` 开源 `10-29`) | `api` & `open_weights` | `next-mistral-large-4pt1-released-byptptpt` | `BLOCKED_NEAR_MISS` | `Large 4`（含其开源权重 `10-29` 及后续 GA 转正）被 `<= 4.0` 排除条款明文剔除 |
| Z.ai | `GLM-5.3-FlashX-Legal` (`[284]` `11-02`) 及 `GLM-5.3` / `Flash` / `FlashX` / `Prime` | `api` / `open_weights` (`08-14..11-02`) | `next-zptai-glm-5pt4-released-byptptpt` | `BLOCKED_NEAR_MISS` | 垂直法律变体及全系 `5.3` 衍生型号受 `"version designation of 5.3 or below"` 阻断 |
| SpaceXAI (xAI) | `Grok 4.7` (`[254]` `09-21`)、`Grok 5` 训练报道 (`S0453`/`S0522`/`S0680`) | `general` / 未发布传闻 | `grok-5-released-byptptpt-20260710195520919`、`next-grok-model-4pt8...`（3 盘） | `BLOCKED_NEAR_MISS` / `SIGNAL_ONLY` | `4.7 < 4.8` 且在 `Grok 5` 盘被点名排除；`Grok 5` 尚在训练（截至 `2026-11-11` 未发布） |

---

## 逐簇原文核查详情

### 1. Alibaba：`Qwen4-Max-Preview`（`[291]/[292]`）与 `S0858`/`S0868` 预告矩阵
- **时间线与信号原文**：
  - `[291]/[292]`（`2026-11-10` ET / `2026-11-11T02:01Z`）：`Qwen4-Max-Preview`（`stage=preview`），访问条件注记为 `Alibaba Token Plan 订阅内预览；无开放权重`，`ev`: `X @Alibaba_Qwen (oembed 原文): "... Qwen4-Max is now in preview on Alibaba's Token Plan"`，`notes`: `Qwen4 家族（Max/Plus/Flash/27B）仅 Max 进入预览，其余未发布。`
  - `S0858`（`2026-10-29`）记录云栖大会（Apsara）现场幻灯片曾列出 `Qwen4-Max / Qwen4-Flash / Qwen4-Plus / Qwen4-27B 标注 coming soon`；`S0868`（`2026-11-06`）仅四词预告 `"The becoming begins."`。
  - 前代已有 `[231]/[240]` `Qwen3.8-Max`（`08-03` API / `08-14` 开源）与 `[241]` `Qwen3.8-Flash-Next`（`08-24`）。
- **重点待触发事件（`BENCHMARK_READY`）**：
  - **`next-qwen-max-model-3pt9-text-arena-debut-20261106`**：
    - `Qwen4-Max-Preview` 已满足该盘全部命名与版本门槛——原文明文例举：`"For example, a version 3.9 or higher named in the same manner as Qwen3.7-Max or Qwen3.8-Max-Preview would qualify, including a new whole-number generation such as Qwen4-Max"`。
    - 其尚未对全员免费开放亦不影响本盘：`"Whether the model was previously released, publicly accessible, in beta, or otherwise available before appearing on the leaderboard is irrelevant"`。
    - **何时触发 YES**：只要带明确 `Qwen4-Max` / `Qwen4-Max-Preview` 名称、且未标 `"AutoEval"` 的条目首次出现在 `https://arena.ai/leaderboard/text/overall-no-style-control`，并在首次出现**次日 `12:00 PM ET`** 仍留在榜上，即按界面展示 `Score` 栏结算各分档位。
  - **Chinese #1 / Top-3 榜单事件（`will-a-chinese-company-have-the-best-ai-model-by-december-31`、`dem-sweep-and-chinese-ai-model-number-1-by-end-of-2027` 及各月末榜）**：若 `Qwen4-Max-Preview` 上榜排名达到 Top 3 / #1 将触发对应条件。注意 `will-a-chinese-company-have-the-best-ai-model-by-december-31` 原文**未写 `AutoEval` 排除条款**，而其余 Arena 榜均明确排除 `"AutoEval"`。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`next-alibaba-qwen-plus-3pt8-released-byptptpt`**：规则限定 `"A qualifying model must have a name or model identifier that includes "Qwen" and "Plus," be the flagship model of Alibaba's core Qwen Plus tier, and be designated as version 3.8 or higher"`，并显式排除 `Qwen3.7-Max` 等非 Plus 型号。当前仅有 `Qwen4-Max-Preview` 上线预览，核心 `Plus` 尚无 `3.8+` 或 `4` 发布。
  - **`next-qwen-flash-3pt9-released-byptptpt`**：规则排除 `"models whose name does not include "Flash" or which retain a version designation below 3.9, such as Qwen3.8-Flash, Qwen3.8-Plus, or Qwen3.9-Max"`。
  - **两盘共同隐患**：后续即使 `Qwen4-Plus` 或 `Qwen4-Flash` 先行进入 **Alibaba Token Plan 封闭/付费预览**，除非符合 `"launched and publicly accessible, including via open beta or open rolling waitlist signups"` 且非 `"A closed beta or any form of private access will not suffice."`，否则将因 `access_stage` 触发歧义甚至不计数。
  - **`us-government-removes-public-access-to-a-major-chinese-ai-model-in-2026-20260703203328223`**：本盘明文规定 `"preview-only models will not qualify"`，若制裁仅波及预览态的 `Qwen4-Max-Preview` 而未影响正式版旗舰模型，仍不足以结算。

---

### 2. Anthropic：`Claude Fable 5.2`（`[287]`）、`Claude Mythos 5.2`（`[288]`）与 `5.5` 系列
- **时间线与信号原文**：
  - `[287]` `Claude Fable 5.2`（`2026-11-09T18:57Z`，`stage=general`）：`全用户 + API/AWS/Google Cloud/Bedrock/Foundry`，OpenRouter `S0871`（`19:49Z`）与 AWS Bedrock `S0873`（`22:43Z`）均已核实；`ev`: `"Claude Fable and Claude Mythos are the same underlying model. Fable has strong cybersecurity and biology safeguards to guard against misuse, which allows us to make it available to all users."`
  - `[288]` `Claude Mythos 5.2`（`2026-11-09T18:57Z`，`stage=limited`）：仅面向 Life Sciences / Cyber Verification 认证组织（`ev`: `"Claude Mythos 5.2 is available to vetted organizations that work in these dual-use areas."`）。
  - `[255]` `Claude Opus 5.5`（`09-22`）、`[262]` `Claude Sonnet 5.5`（`09-28`）、`[268]` `Claude Haiku 5.5`（`10-07`）均已全员可用。
- **重点待触发事件（`BENCHMARK_READY`）**：
  - **`next-fable-model-5pt2-humanitys-last-exam-debut-20260928`**：`[287]` `Claude Fable 5.2` 晚于 `09-28` 建盘且符合 `Fable 5.2+`。一旦其首次现身 `https://agi.safe.ai/` 的 `"AI Progress on Humanity's Last Exam"` 图表并在次日 `12:00 PM ET` 留存，即依页面展示 `"HLE Accuracy"` 结算（注意此盘用的是经典 HLE 图表，而非 `Opus 5.6+` 盘的 1,000 题 HLE-Diamond）。
  - **`next-fable-model-5pt2-text-arena-debut-20260928` & `next-fable-model-5pt2-text-arena-rank-debut-20261027`**：`[287]` 亦晚于 `10-27` 建盘。当带有合格 `Fable 5.2`（且无 `"AutoEval"` 标记）的条目首次登上 `https://arena.ai/leaderboard/text/overall-no-style-control` 并维持至次日 `12:00 PM ET` 时触发。注意在 `Rank Debut` 盘上，**先期匿名盲测占位不计入首现时间，且若同时存在推理/非推理不同档位分开列名，先入榜的一条即锁定结算**：`"Each separately listed entry, including reasoning or thinking-level variants of the same model, is a distinct model for the purposes of this market"`。同底层的 `[288]` `Mythos 5.2` 因名称不含 `"Fable"` 而被双双排除。
  - **对 `best-ai-model-on-november-16` 的分流影响**：该事件创建时仅列出了 `claude-opus-5.5-high`、`gemini-4-argon-high`、`gemini-4-carbon-high` 三个具体子盘并声明 `"No new model will be added to this market after market creation. Any model not explicitly listed in this market will be encompassed under the "Other" option."`。即便 `[287]` `Claude Fable 5.2` 于 `2026-11-16 12:00 PM ET` 排名总榜第 1，也会结算为 `"Other"` 而不会落入 Anthropic 的 `Opus 5.5` 子盘。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`claude-6-released-byptptpt`**：`[287]` `Fable 5.2` 与 `[255]`/`[262]`/`[268]` `5.5` 版本全部低于 `6`（排除 `"models that retain a version designation below 6, such as Claude Fable 5.1 or Claude Opus 5"`）；`[288]` `Mythos 5.2` 不仅 `< 6`，还额外触及 `"A Mythos-branded release available only through Anthropic's verification or trusted-access programs, and task-specific products or restricted lines such as Claude Code, Claude Gov, or Claude Security, will not qualify on their own."`。
  - **`next-claude-haiku-5pt6-released-byptptpt-20261008132000000`、`next-claude-opus-5pt6-released-onptptpt-20261027`、`next-claude-opus-released-byptptpt-20260923144500000`、`next-claude-sonnet-5pt6-released-byptptpt-20260929100500000`、`next-claude-opus-model-5pt6-hle-diamond-debut`、`next-claude-opus-model-5pt6-text-arena-debut-20260928`**：各盘均点名排除了对应的 `5.5`（如 `"while models whose name does not include "Opus" or which retain a version designation below 5.6, such as Claude Opus 5.5, including any rollout, promotion, or snapshot of it, will not qualify."`），同时 `Fable 5.2` 名称不含 `Haiku`/`Opus`/`Sonnet` 而完全不计数。**触发条件**：Anthropic 必须公开发布对应系列且版本明示 `>= 5.6` 的新作（或基准盘对应名字首次上榜）。

---

### 3. OpenAI：`GPT-6 Astra` / `6.1 Sol` / `6.1 Terra` / `6 Cyber` / `6 Rosalind` 与 `gpt-6.2-astra` 信号
- **时间线与信号原文**：
  - `[249]/[250]` `GPT-6 Astra`（`2026-09-03` API / `limited`；系统卡写 `'We are beginning with a limited set of organizations'`）。
  - `[256]-[259]` `GPT-6 Luna` 与 `GPT-6 Sol`（`09-22`）；`[263]/[264]` `GPT-6.1 Sol`（`09-29`，`paid_users`+`api`，博客明言 `'GPT-6.1 Sol is not yet available in Chat.'`）；`[278]/[279]` `GPT-6.1 Terra`（`10-26`，`paid_users`+`api`，只上 ChatGPT Work、Codex 与 API）。
  - `[282]` `GPT-6 Rosalind`（`10-30`，`limited`，仅限 Rosalind Research 信任计划批准机构）；`[285]` `GPT-6 Cyber`（`11-05`，`limited`，`initially available through the API and Codex to a select group of approved Daybreak Red customers`）。
  - `S0820`（`09-29`）：`"just one day after quietly shelving an upgrade to its flagship system"`（`notes`: 指 `9/28-9/29` 弃置 `GPT-6.1 Astra`）；`S0859`（`11-01`）：`"GPT-6.2 Astra has surfaced strictly as an unannounced server-side canary test in OpenAI Codex usage analytics"`；`S0867`/`S0869`（`11-06`/`11-07`）均记录 `GPT-6.2 Astra` 与 `GPT-6.2 Sol` 预期发布窗口推迟、截至 `11-11` 未发布。
- **重点待触发事件（`BENCHMARK_READY`）**：
  - **`next-gpt-terra-model-5pt7-text-arena-debut-20261022`**：市场建于 `2026-10-22`，而 `[278]/[279]` `GPT-6.1 Terra` 发布于 `2026-10-26` 且满足 `5.7+` 与 `GPT`+`Terra`。规则明确 `"Whether the model was previously released, publicly accessible, in beta, or otherwise available before appearing on the leaderboard is irrelevant for this market."`。一旦 `gpt-6.1-terra` 首次以非 `"AutoEval"` 身份登上 `arena.ai/leaderboard/text/overall-no-style-control` 并在次日 `12:00 PM ET` 在榜，即依其分数触发结算（不受未入 Chat 争议拖累）。
- **被阻断与信号跟踪事件（`BLOCKED_NEAR_MISS` / `SIGNAL_ONLY_UNRELEASED`）**：
  - **`gpt-astra-6pt1-released-byptptpt`、`gpt-astra-6pt1-released-onptptpt`、`when-will-gpt-astra-6pt1-be-released-20261020`**：
    - `[249]/[250]` `GPT-6 Astra` 被明确点名排除（`"GPT-6 Astra, including any rollout, promotion, Pro or Fast mode, or snapshot of it, will not qualify."`）。
    - `[263]` `GPT-6.1 Sol`、`[278]` `GPT-6.1 Terra`、`[282]` `GPT-6 Rosalind` 与 `[285]` `GPT-6 Cyber` 被 `"Tier-labeled models such as GPT-5.6 Sol, GPT-5.6 Terra, or GPT-5.6 Luna and their successors, and task-specific or modality lines such as GPT-5.6-Cyber, Daybreak models, Codex, GPT Image, or Realtime models, will not qualify."` 与 `limited` 访问壁垒拦截。
    - `S0859` `"gpt-6.2-astra"` 属于未经宣布的 Codex 服务端金丝雀测试（规则拒斥 `"A closed beta or any form of private access"`）且 `S0867`/`S0869` 已确认延期未发。一旦未来正式公开开放 `GPT-6.1 Astra` 或 `GPT-6.2 Astra`，三盘均立即触发。
  - **`next-gpt-luna-6pt1-released-byptptpt`、`next-gpt-sol-6pt2-released-byptptpt`、`next-gpt-terra-6pt2-released-byptptpt`、`gpt-7-released-byptptpt`**：
    - `[256]` `GPT-6 Luna`、`[263]` `GPT-6.1 Sol`、`[278]` `GPT-6.1 Terra` 分别被各自低于 `6.1` / `6.2` / `6.2` 的版本号条款显式点名排除（如 `"which retain a version designation below 6.2, such as GPT-6.1 Terra (released October 26, 2026)"`）；`S0867/S0869` 里的 `GPT-6.2 Sol` 也因延期而尚未存在公开版本。
    - **双点特殊观察**：(1) 上述三盘正文均写了 `"including a new whole-number generation such as GPT-7 Sol or an Astra-branded release meeting these criteria"`（对应 Terra / Luna 盘分别为 `GPT-7 Terra` / `GPT-7 Luna`）——按字面 `"or an Astra-branded release meeting these criteria"`，前句依然限定 `"includes "GPT" and "Sol""`（或 `Terra`/`Luna`），但若未来仅发 `GPT-6.2 Astra` 而不发同代 tier 型号，这一句将引发市场澄清争议；(2) 参考 `[264]`/`[278]` 先例，OpenAI 近期高端模型频繁在首发时只进付费 ChatGPT Work/Codex 与自助付费 API 而写明 `"not yet available in Chat"`，未来 `6.2` 模型若延续该渠道策略，其算不算 `"accessible to the general public"` 将再成核心核查点（虽然 API 自助注册对开发者开放）。

---

### 4. Google：`Gemini 4 Argon` / `Carbon` / `Hydrogen`、`gemini-omni-1.1/1.2-flash` 与元素代号冲突
- **时间线、信号与补充事实原文**：
  - `[271]-[273]` `Gemini 4 Argon`（`2026-10-13T16:04Z` GA，model ID `gemini-4-argon`，timeline `tier=Pro`）；`[280]` `Gemini 4 Carbon` `10-28` Fairwind 限免测试 -> `[289]/[290]` `Gemini 4 Carbon`（`2026-11-10T16:05Z` GA，model ID `gemini-4-carbon`，timeline `tier=Pro`）。
  - `S0849`（`10-21`）：`"Between October 21 and October 23, 2026, a candidate checkpoint widely attributed to Gemini 4 Carbon appeared in blind testing on LM Arena under the alias "gemini-4-argon""`；`S0912`：`"Google reportedly tested three Gemini 4 variants internally: Argon, Barium, and Carbon. Public Argon was reportedly the Barium-B checkpoint, so codenames did not map cleanly to public names."`
  - `[247]` `Gemini 3.8 Flash`（`09-02`）；`S0864`/`S0866`（`11-04`/`11-05`）：OpenRouter 上架 `google/gemini-omni-1.1-flash` 与 `google/gemini-omni-1.2-flash`；`S0911`（`11-11` 观察）：Model Garden 同页出现 `Gemini 4 Cyber Permissive`。
  - **`data_t37/addendum_after_2026-11-11.md` 补充事实：`Gemini 4 Hydrogen`**（`2026-11-12T18:00:00Z` = 美东 `2026-11-12 13:00 EST`）：稳定版发布（`Stable`），模型 ID 为 `gemini-4-hydrogen`（无别名）；GA 覆盖 Gemini API、Google AI Studio、Gemini for business、Antigravity、Gemini App 及 Google Search 自动选择（先兆为 `2026-11-12 ~08:40Z` Google Cloud 计费行）。定位为 `"rapid execution across diverse agentic workflows"`（对比 Argon 与 Carbon 的 `"deep, long-horizon reasoning"`），称 `"With Hydrogen, we're also bringing Gemini 4 to everyone."`。博客正文仅在 `"migrating from Gemini 3.8 Flash"`、`"compared to 3.8 Flash"` 与自动路由脚注（提及 `Flash-Lite` / `Flash` / `Pro`）中出现 `"Flash"`/`"Flash-Lite"`/`"Pro"`；模型页面仅在 `"API changes from Gemini 3.8 Flash, and migration guidance"` 提及 `"Flash"`；官方别名 `gemini-flash-latest` 变更日志停留在 `2026-01-21`，截至 `2026-11-13` **未指向** `gemini-4-hydrogen`。
- **关键拦截与名称陷阱（`BLOCKED_NEAR_MISS` + 11-16 枚举/公司榜路由）**：
  - **Pro 标签系列（`next-google-gemini-pro-model-released-byptptpt`、`next-google-gemini-pro-model-arena-debut`、`next-google-gemini-pro-model-humanitys-last-exam-debut-20260729192434644`）**：尽管 `[272]` `Argon` 与 `[290]` `Carbon` 在生态定位与 `timeline.csv` 中均为 `Pro` 档，三份规则均要求带 `"Pro"` 标签（如 HLE 盘写 `"Any Gemini model labeled as "Pro" may qualify (e.g., gemini-3.2-pro, gemini-3.5-pro, or gemini-4.0-pro-preview). Gemini models labeled only as Flash, Flash-Lite, or another non-Pro variant will not qualify."`，release 盘加了 `"released after market creation and labeled as "Pro""`）。两者正式名称及 ID 完全不带 `"Pro"`；而 `11-12` 上线的 `Gemini 4 Hydrogen` 同样采用化学元素词且无 `"Pro"` 命名，进一步确认 Gemini 4 全代均不带 `"Pro"`，按字面均不触发上述三盘。唯独枚举盘 `best-ai-model-on-november-16` 明确设了 `gemini-4-argon-high` 与 `gemini-4-carbon-high` 子盘。
  - **`next-gemini-argon-released-byptptpt-20261014`**：`[289]/[290]` `Gemini 4 Carbon` 虽属 Argon 后推出的高阶兄弟版本且 Carbon 检查点曾在 LMArena 以 `"gemini-4-argon"` 盲测（`S0849`），而 `11-12` 的 `Gemini 4 Hydrogen` 为同代普及新元素分支，但规则点名屏蔽 `"while Gemini 4 Argon itself, including any rollout, promotion, snapshot, price change, or thinking-level setting of it, and models whose name does not include "Argon," such as Gemini Pro, Gemini Flash, or Gemini Flash-Lite models, will not qualify."`。只有全新模型 ID（非沿用 `gemini-4-argon`）且名字包含 `"Argon"` 的新型号才算 YES。
  - **`next-gemini-flash-model-3pt9-released-byptptpt`**：除 `[247]` `Gemini 3.8 Flash`（`< 3.9`）与 `gemini-omni-1.1/1.2-flash`（`S0864`/`S0866`，命中 `"Specialized modality or security variants, such as Gemini Flash Image, Gemini Flash-Lite Image, Gemini Omni Flash, Gemini Flash Cyber, or Flash TTS or Live models, will not qualify."`）及 `Gemini 4 Cyber Permissive` 外，`11-12` 刚全量上线的 **`Gemini 4 Hydrogen`** 构成最新擦边阻塞点：虽然其在产品定位与迁移指引上直接承接 `3.8 Flash`（`"migrating from Gemini 3.8 Flash"`、`"bringing Gemini 4 to everyone"`），但正式名与 ID（`gemini-4-hydrogen`）不含 `"Flash"` 且 `gemini-flash-latest` 亦未指向它，无法满足 `"A qualifying model must have a name or model identifier that includes "Gemini," be labeled "Flash" rather than "Flash-Lite,""` 之字面条件。
  - **`next-gemini-flash-lite-model-3pt6-released-onptptpt-20261027` & `next-google-gemini-flash-lite-model-3pt6-released-byptptpt`**：需名称明确同时带 `Gemini` 与 `Flash-Lite` 且版本 `>= 3.6`，故 `3.5 Flash-Lite`、`3.8 Flash`、`Omni Flash` 以及仅在自动选择脚注提及 `Flash-Lite` 的 `Gemini 4 Hydrogen`（`gemini-4-hydrogen`）均被排除。
  - **`best-ai-model-on-november-16` 与公司榜（`which-company-has-*`）路由分流**：在 `2026-11-16 12:00 PM ET` 查榜的 `best-ai-model-on-november-16` 仅有 `gemini-4-carbon-high`、`gemini-4-argon-high`、`claude-opus-5.5-high` 与 `any other model` 四个子盘；若 `gemini-4-hydrogen` 上榜并居首位（且非 `AutoEval`），仅归入 `any other model`（不触发 Carbon/Argon），但在 `which-company-has-*` 公司级 Arena/LiveBench 榜单中计入 `Google`。

---

### 5. Meta：`Muse Spark Open`（`[274]`）、`Muse Wonder`（`[269]/[270]`）与 `Muse Ember`（`[286]`）
- **时间线与信号原文**：
  - `[248]` `Muse Spark 1.3`（`2026-09-02` API）；`[269]/[270]` `Muse Wonder Full` / `Muse Wonder`（`2026-10-12` API）；`[274]` `Muse Spark Open`（`2026-10-15`，`meta-models/Muse-Spark-Open-816B-A42B`）；`[286]` `Muse Ember`（`2026-11-09` API，`notes`: 由 `Muse Wonder Full` 蒸馏而来）。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`next-muse-spark-1pt4-released-byptptpt` & `next-muse-spark-model-1pt4-released-onptptpt`**：两盘要求 `"includes "Muse Spark" and be designated as version 1.4 or higher"`。`[274]` `Muse Spark Open` 名字虽含 `Muse Spark`，但**无 `>= 1.4` 版本号**且为 816B 开源衍生分支；`[248]` `Muse Spark 1.3` 低于 `1.4`；`[270]` `Muse Wonder` 与 `[286]` `Muse Ember` 名字均无 `Muse Spark`。需 Meta 正式开放带明确 `1.4+`（或 `Muse Spark 2`）编号的版本。
  - **`next-muse-wonder-1pt1-released-byptptpt`**：`10-12` 的 `Muse Wonder` 与 `Muse Wonder Full` 被点名排除（`"such as Muse Wonder and Muse Wonder Full (both released October 12, 2026)"`）；`11-09` 上线的 `Muse Ember` (`[286]`) 虽在技术血缘上蒸馏自 `Muse Wonder Full`，但名称不含 `"Wonder"` 且无 `1.1+` 标号，不满足字面要件。

---

### 6. DeepSeek：`DeepSeek-V4.1-Flash-1017`（`[275]`）与 `DeepSeek-V4-Pro-0813`（`[237]`）
- **时间线原文**：`[237]` `DeepSeek-V4-Pro GA`（`2026-08-13`，`HF deepseek-ai/DeepSeek-V4-Pro-0813`，`media notes` 记 `0813 checkpoint 权重未放出`）；`[275]` `DeepSeek-V4.1-Flash-1017`（`2026-10-16` ET / `10-17T02:40Z` 开源，`当前 deepseek-flash API 服务模型`）。
- **被阻断与防热更触发点（`BLOCKED_NEAR_MISS`）**：
  - **`next-deepseek-flash-released-byptptpt-20261021-02`**：规则点名排除 `DeepSeek-V4.1-Flash-1017` 本身及任何重打包（`including any open-weight release, snapshot, or re-pointing of the deepseek-flash API alias to it`），且明言 `"A qualifying release must carry a new, distinct model name or date designation, even if it is served through an unchanged API alias such as deepseek-flash"`。同时排除 `Janus-Pro`、`DeepSeek-OCR`、`DeepSeek-V4-Flash-Vision-Exp` 与 `Pro` 系列。触发需看到官方赋予新日期号或更高版本号的 Flash（或唯一无分层快速继任者）。
  - **`next-deepseek-pro-released-byptptpt`**：排除 `DeepSeek-V4-Pro-0813` 与 `Flash` 系列，且声明 `"A qualifying release must carry a new, distinct model identifier or date designation; updates published under an unchanged identifier will not qualify."`。若后续仅补发 `DeepSeek-V4-Pro-0813` 开源权重而沿用原编号，依然不触发！

---

### 7. Moonshot AI：`Kimi K3.1 Pro` API 与开源仓库（`[277]` / `[283]`）
- **时间线原文**：`[277]` `Kimi K3.1 Pro`（`2026-10-23` 上线 Kimi API/App）；`[283]` `Kimi K3.1 Pro`（`2026-11-01` ET / `2026-11-02T04:13Z` HF 建仓 `moonshotai/Kimi-K3.1-Pro`）。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`next-kimi-k-model-3pt2-released-byptptpt`**：直接点名踢除 10-23 版及 11 月权重发布（`"such as Kimi K3.1 Pro or Kimi K3.1 Pro Highspeed (released October 23, 2026), including any open-weight release, rollout, or snapshot of them"`）。需公开发布 `Kimi K3.2+` 或 `Kimi K4`。
  - **`kimi-k4-released-by-20260722184115883`**：即使未来发了 `Kimi K3.2` / `K3.5`，仍被本盘 `"Products labeled as Kimi K3.5 or similar incremental versions will not count"` 拦下，必须达到 `K4`（或被公认为 K3 下一代旗舰）。

---

### 8. Mistral AI：`Mistral Large 4` API 预览（`[266]/[267]`）与 `le Chonk` 开源权重（`[281]`）
- **时间线原文**：`[266]/[267]`（`2026-10-06` `Mistral Large 4` 预览 API 上线，并预告月末开源）；`[281]`（`2026-10-29T12:00Z` 以代号 `Le Chonk` 开源发布 `Mistral Large 4` 权重）。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`next-mistral-large-4pt1-released-byptptpt`**：`10-29` 开源释出（以及未来预览转正式 GA）已由条款明文提前排除（`"Models which retain a version designation of 4.0 or below, such as Mistral Large 4 (released in public preview on October 6, 2026), including its planned open-weights release"`）。未来需看到版本号 `>= 4.1` 或仅以晚于 Large 4 的新日期构建号（如 `mistral-large-2612` 形式）命名的全新模型才算 YES。

---

### 9. Z.ai (Zhipu)：`GLM-5.3` 与 `GLM-5.3-FlashX-Legal`（`[239]/[242]-[244]/[253]/[260]/[284]`）
- **时间线原文**：`[239]` `GLM-5.3`（`08-14` API）、`[242]`（`08-25` 开源）、`[243]/[244]` `GLM-5.3-Flash`（`08-25/26`）、`[253]` `GLM-5.3-FlashX`（`09-18`）、`[260]` `GLM-5.3-Prime`（`09-23`）、`[284]` `GLM-5.3-FlashX-Legal`（`2026-11-02T13:29Z` API `z-ai/glm-5.3-flashx-legal`）。
- **被阻断事件（`BLOCKED_NEAR_MISS`）**：
  - **`next-zptai-glm-5pt4-released-byptptpt`**：所有 `5.3` 及衍生变体均触及 `"while models with a version designation of 5.3 or below, or derivative models not positioned as the next flagship GLM release, such as GLM-5.3-Turbo, will not qualify."`。仅当官方发布并公众上线 `GLM-5.4+` / `GLM-6` 时方能触发。

---

### 10. SpaceXAI (xAI)：`Grok 4.6` / `4.7`（`[236]/[254]`）与 `Grok 5` 训练传闻（`S0453`/`S0522`/`S0680`）
- **时间线与信号原文**：`[236]` `Grok 4.6`（`08-12`）；`[254]` `Grok 4.7`（`2026-09-21` `general`）；`S0680`（`2026-06-03` 报道：`"Grok 5 is still in training as of May 2026."`，`notes` 记截至 `2026-11-11` 仍未发布）。
- **被阻断与信号状态（`BLOCKED_NEAR_MISS` / `SIGNAL_ONLY_UNRELEASED`）**：
  - **`grok-5-released-byptptpt-20260710195520919`**：明确排除 `"Models released under the Grok 4 generation, including Grok 4.6, Grok 4.7, or similar variants, will not qualify."`，需出现 `Grok 5`（或被公认为继 Grok 4 之后的新一代旗舰）。
  - **`next-grok-model-4pt8-released-by`、`next-grok-model-4pt8-released-onptptpt-20261027`、`next-grok-model-4pt8-text-arena-debut`**：同样显式排除 `Grok 4.7`、`Grok Code Fast`、`Grok Imagine` 及非模型版本升级；需公开推出版本号 `>= 4.8`（含 `Grok 5`）或非 `AutoEval` 首次登上 Arena Text 榜。
