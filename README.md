# AQ-Lite

**AtomQuant 的独立轻量版：给任何 LLM agent 用的 Polymarket 扫描与交易建议工具包。**

AQ-Lite 把 AtomQuant 研究项目里验证过的**策略、规则卡和数据资产**拆出来，配上一个只用 Python 标准库的只读工具 `aq.py`，再加一份写给 LLM 的主脑说明 `AGENTS.md`。把它交给 Claude Code、Codex、Cursor、Gemini CLI / Antigravity 等 harness，模型就能按同一套 SOP 扫描 AI 发布盘和地缘盘、读规则、定锚、算仓位，并给出带出处的盘口卡。

> ⚠️ **只读，不下单，不含任何密钥。** 本仓库没有私钥、API key、钱包签名或下单代码，只访问 Polymarket 的公开只读接口。所有输出都只是研究笔记，**不构成投资建议**。

---

## 特点
- **策略才是核心**：`knowledge/SOP.md`（盘口分析十步法）和 `knowledge/DECISIONS.md`（D1–D119 决策记录：哪些打法通过了检验，哪些被否决，原因是什么）。
- **数据资产**：AI 模型发布时间线、发布前信号、模型命名表、开放盘的规则卡与命名风险标记、回测校准表、红队审查报告。
- **零依赖**：Python 3.10+ 标准库即可，`git clone` 后马上能用。
- **为 agent 设计**：`AGENTS.md` / `CLAUDE.md` / `GEMINI.md` 内容相同，主流 harness 启动时会自动读到其中一份。里面写了边界、资产地图、两个标准工作流和输出格式。
- **礼貌访问**：请求之间间隔 0.7 秒；遇到 403 / 429 立即停止。不伪装浏览器，不绕过任何限制。

## 快速开始
```bash
git clone https://github.com/michaelho1117-cloud/AQ-Lite.git
cd AQ-Lite
python3 aq.py scan --days 15          # 全市场扫描（AI + 地缘，约 5–10 分钟）
python3 aq.py market <slug|链接|关键词>  # 某个事件的规则全文与每档价格
```
Windows 用 `python -X utf8 aq.py ...`（或先 `chcp 65001`），否则中文会乱码。

### 交给 agent 使用
1. 用 harness 打开克隆下来的 `AQ-Lite` 文件夹作为工作区。
2. （可选）在 `knowledge/private/` 里放你自己的持仓和资金情况，模板见该目录的 README。这个目录不会进 git。
3. 第一句话发：

   > 先完整读 AGENTS.md，再按里面的要求读 knowledge 目录下的文件。读完后用三句话告诉我你理解的边界和两个工作流，然后等我指令。

4. 之后直接说：
   - **「扫描」**：跑全市场扫描，按 SOP 筛出值得看的盘。
   - **「看这个盘：<链接或关键词>」**：按 SOP 第 1–9 步出一张盘口卡（规则闸门 → 锚 → 相对位置 → 仓位 → 退出）。
   - **「我想在 0.xx 买 X 的 YES，总资产 $A，现金 $C」**：用 `aq.py size` 算评级、凯利仓位和分批价位。

## 命令
| 命令 | 作用 |
|---|---|
| `aq.py scan [--days N]` | AI 与地缘、N 天内到期、中间价 0.04–0.96 的盘；给出买一卖一、一天变动、相对 1 天中位数的偏离、1 天和 7 天分位。结果另存 `var/scan_*.txt` |
| `aq.py market <q> [--no-history]` | 事件规则全文、每档价格、成交量、流动性、UMA 结算状态 |
| `aq.py book <slug> <档位>` | 某一档的 CLOB 深度 |
| `aq.py size --anchor A --mid M --price P --side YES\|NO --cat tech\|geo --assets X --cash C [...]` | 混合锚公允价、含手续费的 edge、S/A/B 评级、凯利仓位、分批阶梯、纪律提示 |
| `aq.py rules <关键词>` | 搜索规则卡和命名风险标记 |
| `aq.py positions <钱包地址>` | 某个公开钱包的持仓（地址是公开编号，不是密钥） |

## 目录
```
AGENTS.md / CLAUDE.md / GEMINI.md   给 LLM 的主脑说明（三份相同）
aq.py                               只读工具
knowledge/
  SOP.md                            盘口分析与操作建议 SOP v0.3.3
  DECISIONS.md                      决策总表（公开版已隐去个人余额和服务器地址）
  strategy_status.md                各打法的证据和状态一页纸
  AS1H.md                           App Store 1 小时前向记录预注册
  private/                          你的持仓、资金、交易习惯（gitignored）
data/
  refdata/                          发布时间线 v3、信号、模型命名、阶段表
  rule_cards/                       开放盘规则卡、命名风险标记、临界观察
  backtests/                        App Store 校准表、红队审查报告
judge/                              锚、仓位、纪律、CLV、手续费的函数库
var/                                扫描输出与模型笔记（gitignored）
```

## 核心结论（详见 `knowledge/strategy_status.md`）
- **公允价从市场价出发**。我们自己从零预测发布日期的模型输给了市场；edge 只来自写得出来源的信息修正。
- **按规则字面结算**。名字和档位词是最大的坑，例如 Gemini 4 Hydrogen 不算 "Flash"，见 `data/rule_cards/risk_flags.csv`。
- **地缘急变后不要机械地逆着做**（1,264 次急变回测，每 $1 亏 20–50%）。
- **仓位纪律**：单一事件在险 ≤ 总资产 10%；同一驱动因素 ≤ 35%；始终留 30% 现金；首笔 ≤ 计划的 1/3。

## 局限
- 知识和数据冻结在 **2026-11-13**；之后的新闻要你提供，或让 agent 联网查。
- 回测样本小，很多结论只是「没被否决」，不等于「已被证明」。`strategy_status.md` 写明了每条的状态。
- 外部模型的判断没有经过本项目验证；SOP 要求每条修正都写出来源。

## 安全
- 仓库不含、也不应含任何密钥。`.gitignore` 默认忽略 `.env*`、`*.key`、`*.pem` 和 `knowledge/private/`。
- CI 会在每次推送时做一次简单的密钥扫描。
- 如果你在 fork 里发现敏感信息，请开 issue（不要贴出内容本身）。

## 许可
代码与文档按 [MIT](LICENSE) 授权。市场数据来自 Polymarket 公开接口，版权归原作者。
