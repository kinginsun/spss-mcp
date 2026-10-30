# spss-mcp：给 Agent 的使用教程

> 把本机 IBM SPSS Statistics 变成 Agent 可调用的「统计引擎 + 制图工厂」。
>
> 适用版本：**v1.1+** ｜ 平台：**macOS / Windows** ｜ Python 3.10+ ｜ IBM SPSS Statistics（已在 **macOS 27**、上游 **Windows 32** 验证）

完成安装后，你不需要记住工具名。直接用自然语言告诉 Agent：数据在哪、想回答什么问题、希望得到什么结果。

## 1. 它能做什么

传统流程：打开 SPSS → 导入数据 → 找菜单 → 设参数 → 运行 → 整理表 → 导出图 → 写结果。

spss-mcp 把大量重复步骤交给 Agent：

- 读取 `.sav` / `.zsav`，检查变量、标签、缺失值与样本量；
- 按研究问题选用描述 / t / ANOVA / 回归 / 因子 / 信度 / 生存 / 混合模型 / 中介调节等；
- **调用真实 SPSS 引擎**执行（不是让模型猜数值）；
- 返回 Markdown 表、结构化 JSON、统计摘要、`.sps` 语法与 `.spv`；
- 按需导出 PNG / TIFF / EMF（默认 1950×1500 @300 dpi）；
- 对危险语法与数据路径做安全检查，并写审计日志。

适合论文分析、问卷/实验、医学随访、课程作业，以及需要可复现的重复流程。

## 2. 最快方式：把这段话发给 Agent

```text
请帮我安装并配置 spss-mcp，让你可以直接调用本机 IBM SPSS Statistics 做统计分析和论文级出图。

项目地址：
https://github.com/kinginsun/spss-mcp

请按以下顺序执行，不要跳过检查：

1. 检查 Python 3.10+、pip，以及本机是否已安装并授权 IBM SPSS Statistics。
2. 优先从 PyPI 安装：`pip install spss-mcp`（开发者才需要 clone + `pip install -e ".[dev]"`）。
3. 运行 `spss-mcp status`，报告 pyreadstat、pandas、SPSS batch / python 状态。
4. 按我当前客户端配置 MCP：
   - Codex → spss-mcp configure-codex
   - Claude Code → spss-mcp configure-claude
   - Cursor 或其他 → 使用 `uvx spss-mcp serve`，或 `spss-mcp setup-info`
5. 确认配置已写入；若改了配置，提示我重启 / Reload MCP。
6. 用公开样例或我提供的 `.sav` 做最小测试：读变量、描述统计。
7. 告诉我：是否成功、下一步可用哪些自然语言请求。

排错时先判断是 Python、依赖、SPSS 路径、授权、MCP 配置还是数据路径；不要删除或覆盖我的原始数据。
```

若 Agent 不能执行命令，让它逐条解释，你在终端跑完后把输出贴回去。

## 3. 手动安装

### 3.1 环境

```bash
python --version   # 需 3.10+
pip --version
```

确认本机已安装并授权 **IBM SPSS Statistics**。无引擎时仍可读 `.sav` 元数据；分析与出图需要 SPSS。

| 平台 | 典型安装位置 |
|------|----------------|
| macOS | `/Applications/IBM SPSS Statistics 27`（需含 `Resources/Python3` XD） |
| Windows | `C:\Program Files\IBM\SPSS Statistics\32`（`stats.exe`） |

### 3.2 安装（优先 PyPI）

```bash
pip install spss-mcp
# 或：uv pip install spss-mcp
```

免安装即跑（类似 npx）：

```bash
uvx spss-mcp status
uvx spss-mcp serve
```

开发者本地可编辑安装：

```bash
git clone https://github.com/kinginsun/spss-mcp.git
cd spss-mcp
pip install -e ".[dev]"
```

### 3.3 检查状态

```bash
spss-mcp status
```

macOS 正常示例：

```text
=== SPSS MCP Capability Status ===
pyreadstat : OK ...
pandas     : OK ...
SPSS batch : OK - /Applications/IBM SPSS Statistics 27/Contents/MacOS/stats
SPSS python: OK - .../Resources/Python3/...
```

Windows 则指向 `...\stats.exe`。若显示 `NOT FOUND`，先按第 10 节设置 `SPSS_INSTALL_PATH`。

### 3.4 配置客户端

```bash
spss-mcp configure-codex      # Codex → ~/.codex/config.toml（会先备份）
spss-mcp configure-claude     # Claude Code 用户配置
spss-mcp setup-info           # 打印手动片段（含 Cursor）
```

Cursor（`~/.cursor/mcp.json`）示例：

```json
{
  "mcpServers": {
    "spss-mcp": {
      "command": "uvx",
      "args": ["spss-mcp", "serve", "--transport", "stdio"],
      "env": {
        "SPSS_INSTALL_PATH": "/Applications/IBM SPSS Statistics 27"
      }
    }
  }
}
```

本地已 `pip install -e .` 时，也可把 `command` 设为 `spss-mcp`，`args` 为 `["serve", "--transport", "stdio"]`。改完后 **Reload MCP / 重启客户端**。

## 4. 第一次验证

重启后先跑最小任务，不要立刻上正式论文数据：

```text
请先调用 spss_check_status，告诉我当前有哪些能力可用。
然后检查 examples/data/survey_study.sav：
1. 列出变量名、标签、类型和缺失值信息；
2. 预览前 10 行；
3. 对 engagement_total 做均值、标准差、最小/最大与样本量；
4. 对 q1 到 q12 做 Cronbach's alpha；
5. 不要修改原始数据，只返回分析结果与生成文件路径。
```

成功时应看到：变量信息、描述表、信度结果、统计摘要，以及可选的 `.sps` / `.spv` 路径。

## 5. 给 Agent 下指令

高质量请求至少包含：

1. **数据文件**路径；
2. **研究问题**；
3. **变量角色**（因变量 / 自变量 / 分组 / 中介 / 调节 / 时间 / 个体 ID）；
4. **分析要求**（前提检验、效应量、事后比较、图）；
5. **交付格式**（论文结果段、表、语法、图、JSON）。

通用模板：

```text
请分析 [数据文件路径]。

研究问题：[一句话]
因变量：[变量名与含义]
自变量或分组：[变量名与含义]
其他变量：[协变量 / 中介 / 调节 / 时间 / 个体 ID]

请按以下流程执行：
1. 先检查样本量、类型、缺失、异常值与必要前提；
2. 若方法不合适，请说明并改用更合适方法；
3. 报告估计值、标准误、置信区间、检验统计量、自由度、p 与效应量；
4. 给出适合论文结果部分的中文解释（相关勿写成因果）；
5. 保存可复现的 SPSS syntax，不覆盖原始数据；
6. 若适合，生成论文级图片并返回绝对路径。
```

## 6. 常见研究场景（项目样例）

样例数据与归档图说明见 [examples/README.md](../examples/README.md)。

### 6.1 问卷：信度与组间差异

```text
请分析 examples/data/survey_study.sav。
先检查样本量、变量标签、缺失值和 q1-q12 取值范围。然后：
1. 对 q1-q12 做 Cronbach's alpha；
2. 对 engagement_total 做描述统计与正态性检查；
3. 按 gender 比较 engagement_total（判断是否适合独立样本 t）；
4. 按 major 做单因素 ANOVA，需要时事后比较；
5. 绘制 engagement_total 直方图和 Q-Q 图；
6. 输出表格、摘要、论文结果段、syntax 与图像路径。
```

### 6.2 实验：前后测与组间比较

```text
请分析 examples/data/experiment_study.sav（group、pretest、posttest、gain）。
先检查 group 编码与每组样本量，然后：
1. 两组 pretest / posttest 描述统计；
2. 比较两组 posttest 与 gain；
3. 对 pretest 与 posttest 做配对 t；
4. 报告均值差、95% CI、t、df、p 与效应量；
5. 生成按 group 分组的 posttest 箱线图；
6. 写出谨慎的论文结果解释。
```

### 6.3 相关与回归

```text
请对 examples/data/mediation_study.sav 做相关和回归。
变量：autonomy、satisfaction、performance。
1. Pearson 相关矩阵；
2. performance ~ autonomy + satisfaction 多元回归；
3. 报告 R²、调整 R²、模型检验、标准化系数、CI 与共线性；
4. 绘制 satisfaction–performance 散点图；
5. 用「相关 / 预测」表述，不要声称因果。
```

### 6.4 中介

```text
请对 examples/data/mediation_study.sav 做中介分析：
X = autonomy，M = satisfaction，Y = performance。
检查样本量与分布后调用中介工具；报告总/直接/间接效应、Sobel 与分步回归。
说明可支持的统计结论与不能支持的因果结论；保存 syntax 与结果文件。
```

### 6.5 调节

```text
请对 examples/data/mediation_study.sav 做调节分析：
X = autonomy，W = satisfaction，Y = performance。
对 X、W 中心化，建立含 X×W 交互的回归；报告交互项与模型解释度变化。
不要只根据主效应判断调节成立。
```

### 6.6 生存

```text
请分析 examples/data/survival_study.sav（treatment、time、status；status=1 为事件）。
1. 检查编码；2. 按 treatment 画 KM 曲线；3. 组间比较；
4. 报告中位生存时间、CI 与 log-rank；5. 说明删失处理；
6. 输出论文级 PNG 与可复现语法。
```

### 6.7 纵向：宽表 RM-ANOVA vs 长表 MIXED

项目提供两套对齐的纵向样例（勿混用工具期望的表结构）：

| 文件 | 结构 | 适用工具 |
|------|------|----------|
| `examples/data/longitudinal_study.sav` | 宽表：`time1`/`time2`/`time3` | `spss_repeated_measures_anova` |
| `examples/data/long_study.sav` | 长表：`id`/`time`/`score` | `spss_mixed` / `spss_genlinmixed` |

```text
请对 examples/data/longitudinal_study.sav 做重复测量 ANOVA：
组内因子为 time1–time3，分组变量 group；报告球形性、主效应与必要的事后比较。
```

```text
请对 examples/data/long_study.sav 做混合模型：
score ~ group + time，随机截距 subject=id；报告固定效应与模型摘要。
```

## 7. 论文级出图

常用 `spss_chart_*`：

| 工具 | 场景 |
|------|------|
| `spss_chart_histogram_density` | 连续变量分布 + 正态密度 |
| `spss_chart_qqplot` | 正态 Q-Q |
| `spss_chart_scatter` | 两连续变量关系 |
| `spss_chart_bar_error` | 分组均值 + 95% CI |
| `spss_chart_boxplot` | 组间分布 / 异常值 |
| `spss_chart_errorbar` | 均值与置信区间 |
| `spss_chart_line` / `spss_chart_area` | 趋势 / 重复测量 |
| `spss_chart_km_curve` | Kaplan-Meier |

```text
请使用 examples/data/survey_study.sav，对 engagement_total 画论文级直方图并叠加正态密度。
要求：PNG、300 dpi、1950×1500；返回绝对路径。
```

macOS 上 HTML 偶发内嵌 JPEG 时，工具会自动转为 PNG 再做 300 dpi 后处理。投稿前仍请检查字体、轴标题与期刊格式。

## 8. 输出与复现

| 产物 | 用途 |
|------|------|
| Markdown / JSON | 阅读与 Agent 消费 |
| `.sps` / `.spv` | 复现与 Viewer |
| PNG / TIFF / EMF | 论文与排版 |
| `logs/audit.jsonl` | 安全审计 |

派生变量请另存，勿覆盖原始文件。每次提交通常重新 `GET FILE`，临时 `COMPUTE` 不会跨会话保留。

## 9. 安全建议

- 先读元数据，再跑复杂分析；
- 勿向不可信客户端暴露含敏感标识的数据；
- 原始数据只读，派生另存；
- 陌生语法先 `dry_run=True`；
- 用 `SPSS_ALLOWED_DIRS` 限制可访问目录。

默认拦截 `HOST`、`ERASE`、`DELETE FILE` 等。详见 [security.md](security.md)。

## 10. 路径与环境变量

复制 `.env.example` 为 `.env`：

```ini
# macOS
SPSS_INSTALL_PATH=/Applications/IBM SPSS Statistics 27

# Windows
# SPSS_INSTALL_PATH=C:\Program Files\IBM\SPSS Statistics\32

SPSS_STARTUP_TIMEOUT=300
SPSS_TIMEOUT=120
# SPSS_ALLOWED_DIRS=/path/to/data;/another/dir
```

临时会话：

```bash
# macOS / Linux
export SPSS_INSTALL_PATH="/Applications/IBM SPSS Statistics 27"
spss-mcp status
```

```powershell
# Windows
$env:SPSS_INSTALL_PATH = "C:\Program Files\IBM\SPSS Statistics\32"
spss-mcp status
```

## 11. 常见问题

### `SPSS batch : NOT FOUND`

确认安装目录后设置 `SPSS_INSTALL_PATH`（macOS 指向 `.app` 上级目录或安装根；Windows 指向含 `stats.exe` 的目录），新开终端再 `status`。

### Agent 看不到工具

检查 `configure-*` / `mcp.json`、是否 Reload、本机 `spss-mcp status`、PATH 中能否找到命令、是否有旧配置冲突。

### 首次很慢或超时

首次启动引擎约 15–20 秒；提高 `SPSS_STARTUP_TIMEOUT` / `SPSS_TIMEOUT`；避免多开 SPSS 会话。

### 未授权 / 出图失败

确认授权有效；结束残留的 `stats` / `spssengine` 进程后再试。

### 数据路径被拒 / Error #61

把数据放在项目内、`examples/data/`、临时目录或 `SPSS_ALLOWED_DIRS`；本 fork 会把相对路径解析为绝对路径，但仍建议在 Prompt 里给清晰路径。

### 中文标签异常

Prompt 优先用变量名；先让 Agent 读变量标签再分析。

## 12. 一键完整分析模板

```text
请作为 SPSS 统计分析助手，分析 [数据文件路径]，不要修改原始文件。

研究背景：[对象、目的、假设]
数据说明：[样本量、变量、分组、时间结构]
核心问题：[统计问题]

请严格按顺序：
1. 读元数据（类型、标签、取值、缺失、样本量）；
2. 说明各问题适用方法与理由；
3. 前提检验与异常值检查；
4. 正式分析（估计值、SE、CI、统计量、df、p、效应量）；
5. 对应论文级图（PNG 300 dpi）；
6. 中文结果解释与可改的论文结果段；
7. 保存 syntax、Viewer、图像路径；
8. 返回 Markdown、结构化摘要、路径与警告；
9. 列出局限，勿把相关表述为因果。

若编码或设计不清，先提问，不要擅自假设。
```

## 13. 开发与验证

```bash
python scripts/make_sample_data.py
python scripts/method_verification.py
python scripts/tool_verification.py
python scripts/archive_sample_charts.py
pytest
```

延伸阅读：

- [技术报告](technical_report.md)
- [出图管线](poc_chart_pipeline.md)
- [结果解析](result_parsing.md)
- [方法验证](method_verification.md)
- [安全层](security.md)
- [样例数据与图](../examples/README.md)
