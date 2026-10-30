# 生态收录与发布说明

> 提交类操作需发布账号。本文件给出可直接使用的条目与检查清单。
>
> 当前产品线：**spss-mcp v1.1+**（本 fork：`kinginsun/spss-mcp`，macOS + Windows）  
> 上游能力基线：`flupke91/spss-studio-mcp` v1.0.0（Windows + SPSS 32）

## 1. 项目速览（用于收录/发布）

- **名称**：spss-mcp
- **一句话**：让 SPSS 成为 Agent 的「统计引擎 + 制图工厂」：论文级图片、深度结果解析、方法真机验证、安全执行。
- **类别**：data-analysis / statistics / mcp-server
- **标签**：`spss` `statistics` `mcp` `chart` `result-parsing` `psychology` `social-science`
- **平台**：macOS | Windows
- **核心能力**：
  - 11 类论文级图表（PNG/TIFF/EMF，300 dpi）
  - 16 类分析统计摘要（t/F/r/B/Wald/p/效应量）
  - 37+ 工具真机验收（上游 SPSS 32；本 fork 在 macOS SPSS 27 复验引擎与出图）
  - 中介/调节（Baron & Kenny + Sobel）
  - 安全层（拦截/白名单/dry_run/审计）
  - macOS 引擎探测、XD 启动、JPEG→PNG 出图归一化、相对路径绝对化

## 2. LobeHub 收录条目

- 仓库：https://github.com/kinginsun/spss-mcp
- 上游参考：https://github.com/flupke91/spss-studio-mcp
- LobeHub 插件市场提交入口：https://github.com/lobehub/lobe-chat-plugins  
  （创建 `plugins/<plugin-name>/`，含 `plugin.json` + `README.md`）

```yaml
# lobehub 条目示例
name: spss-mcp
description: >-
  spss-mcp：论文级图表导出（11 类图 PNG/TIFF/EMF @300dpi）、深度结果
  解析（Markdown+JSON+统计摘要）、37+ 方法真机验证、中介/调节与安全执行
  （危险拦截/白名单/dry_run/审计）。支持 macOS / Windows 本机 SPSS。
category: data-analysis
tags: [spss, statistics, chart, mcp]
```

## 3. PulseMCP 收录条目

- 提交入口：https://www.pulsemcp.com/submit
- 仓库：https://github.com/kinginsun/spss-mcp

- **Name**: spss-mcp
- **Short description**: Paper-ready charts, deep result parsing and safe execution for IBM SPSS Statistics via MCP (macOS + Windows).
- **Long description**: 引用 `README.md` 功能清单与 `docs/technical_report.md` 摘要；补充本 fork 的 macOS / SPSS 27 适配。
- **Transport**: stdio
- **Auth**: none（本地 SPSS 授权）
- **OS**: macOS, Windows
- **Install**: `uvx --from git+https://github.com/kinginsun/spss-mcp.git spss-mcp`

## 4. GitHub Release 草稿

- v1.0.0（上游能力基线）：`docs/release_notes_v1.0.md`
- v1.1.x（本 fork）：见根目录 `CHANGELOG.md`（macOS 引擎、出图 JPEG→PNG、路径与解析修复）

## 5. 提交前检查清单

- [x] 功能与验证：37 工具真机验收（26 方法 + 11 工具）、11 类图 × PNG/EMF/TIFF（上游 Windows）
- [x] boxplot 全格式修复（0.3.1）
- [x] macOS / SPSS 27 引擎探测与出图链路（本 fork 1.1.x）
- [x] 文档：README / QUICK_START / docs/tutorial / examples
- [x] 安全：拦截/白名单/dry_run/审计 + `docs/security.md`
- [x] CI：`.github/workflows/ci.yml`（lint + pytest）
- [x] 许可证：MIT（含上游说明）
- [x] 样例：`examples/data/*.sav` + `examples/charts/*.png`
- [ ] 发布账号：创建/更新 GitHub Release、提交 LobeHub/PulseMCP
- [ ] 公开仓库前检查：无敏感路径、无本地日志入库（`logs/` 已 gitignore）

## 6. 对外材料

- 技术报告：`docs/technical_report.md`（v1.0 能力基线；Windows + SPSS 32）
- 使用教程：`docs/tutorial.md`（v1.1+，macOS / Windows）
- 样例说明：`examples/README.md`
- 出图 PoC：`docs/poc_chart_pipeline.md`
- 更新日志：`CHANGELOG.md`

## 7. 发布步骤备忘

- [x] 上游公开仓库 `flupke91/spss-studio-mcp` 与 tag `v1.0.0`（2026-08-05）
- [ ] 本 fork `kinginsun/spss-mcp`：按 `CHANGELOG` 打 `v1.1.x` Release
- [ ] 提交 LobeHub / PulseMCP（指向本 fork 仓库与平台 macOS|Windows）
