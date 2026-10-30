# SPSS Studio MCP (macOS + Windows)

> 让 SPSS 成为 Agent 的「统计引擎 + 制图工厂」：论文级图片、深度结果解析、方法真机验证、安全执行。

**简体中文** ｜ [English](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)]()

面向 **IBM SPSS Statistics** 的 MCP（Model Context Protocol）服务器，供 Cursor / Claude Code / Codex 等 Agent 调用本机 SPSS。

本仓库基于上游 [`flupke91/spss-studio-mcp`](https://github.com/flupke91/spss-studio-mcp)（MIT），在其能力之上增加了 **macOS / SPSS 27+** 适配与若干兼容性修复，并在 **macOS + IBM SPSS Statistics 27** 真机验证通过。

## 能力概览

- **论文级出图**：11 类 `spss_chart_*`，PNG / TIFF / EMF（1950×1500 @300 dpi）
- **深度结果解析**：OMS 文本 → Markdown + JSON + 统计摘要
- **分析方法**：描述 / t / ANOVA / 回归 / 因子 / 信度 / 生存 / 混合模型 / 中介调节等
- **安全执行**：危险命令拦截、路径白名单、`dry_run`、审计日志
- **跨平台引擎**：Windows（`stats.exe`）与 macOS（`SPSS Statistics.app` + 捆绑 Python3 XD）

## 本 fork 相对上游的主要改动

| 项 | 说明 |
|----|------|
| macOS 探测 | 自动发现 `/Applications/IBM SPSS Statistics *` |
| XD 启动 | 设置 `SPSS_HOME`、`DYLD_*`，修复捆绑 `libpython` 加载 |
| 出图 | macOS HTML 内嵌 JPEG → 自动转 PNG，再缩放至 300 dpi |
| 路径 | 相对路径解析为绝对路径，避免 SPSS Error #61 |
| 解析 | 避免把 ANOVA 表中的 Error SS 误判为 `Error #` |
| 样例数据 | 宽表 / 长表纵向数据对齐，便于 RM-ANOVA 与 MIXED |

## 系统要求

- Python 3.10+
- 本机已授权的 **IBM SPSS Statistics**（已在 **27（macOS）** 验证；上游在 **32（Windows）** 验证）
- macOS：安装包内需含 `Resources/Python3`（XD API）

## 快速开始（macOS）

```bash
cd spss-studio-mcp
pip install -e ".[dev]"
spss-studio-mcp status   # 应显示 SPSS batch / python: OK
```

可选：在 `.env` 中指定安装目录：

```bash
SPSS_INSTALL_PATH=/Applications/IBM SPSS Statistics 27
```

配置 Cursor（`~/.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "spss-studio": {
      "command": "spss-studio-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "SPSS_INSTALL_PATH": "/Applications/IBM SPSS Statistics 27"
      }
    }
  }
}
```

也可用：

```bash
spss-studio-mcp configure-claude
spss-studio-mcp configure-codex
spss-studio-mcp setup-info
```

## 自然语言示例

```text
对 examples/data/experiment_study.sav 做独立样本 t 检验（group 分组，posttest）
用 examples/data/mediation_study.sav 做中介分析：autonomy → satisfaction → performance
画 examples/data/survey_study.sav 学习投入总分的直方图（带正态密度），PNG 300dpi
对 examples/data/long_study.sav 做混合模型：score ~ group + time，随机截距 subject=id
```

纵向数据约定：

- 重复测量 ANOVA（宽表）：`examples/data/longitudinal_study.sav`（`time1`/`time2`/`time3`）
- MIXED（长表）：`examples/data/long_study.sav`（`id`/`time`/`score`）

## 架构

```text
MCP 客户端（Cursor / Claude Code / Codex）
        │  MCP 协议（stdio）
        ▼
工具层    50+ 工具：文件/元数据 · 分析方法 · 图表 · 中介/调节
        ▼
语法构建   方法模板 + Pydantic 校验 ｜ 安全层
        ▼
引擎层    SPSS Python3 XD 持久会话（StartSPSS / Submit）
        ▼
输出层    OMS TEXT → Markdown/JSON ｜ HTML → PNG/TIFF ｜ DOCX → EMF
        ▼
IBM SPSS Statistics（本机授权；macOS 或 Windows）
```

## 文档

- [Agent 使用教程](docs/tutorial.md)
- [技术报告](docs/technical_report.md)
- [结果解析](docs/result_parsing.md)
- [安全层](docs/security.md)
- [更新日志](CHANGELOG.md)

## 致谢与许可证

- 上游：[`flupke91/spss-studio-mcp`](https://github.com/flupke91/spss-studio-mcp)（MIT）
- 更早上游：`Exekiel179/SPSS-MCP`（MIT）
- 本仓库同样以 **MIT** 发布
