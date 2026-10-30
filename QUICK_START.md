# spss-studio-mcp 快速开始

> 3 步完成部署（已在 macOS + IBM SPSS Statistics 27 真机验证；上游亦在 Windows + SPSS 32 验证）

---

## 第 1 步：安装

```bash
cd spss-studio-mcp
pip install -e ".[dev]"
spss-studio-mcp status   # 应显示 SPSS batch / python: OK
```

macOS 若未自动发现安装，可设置：

```bash
export SPSS_INSTALL_PATH="/Applications/IBM SPSS Statistics 27"
```

## 第 2 步：配置 MCP 客户端

```bash
spss-studio-mcp configure-codex     # Codex
spss-studio-mcp configure-claude   # Claude Code
spss-studio-mcp setup-info         # 打印手动配置片段（含 Cursor）
```

Cursor：把 `setup-info` 输出写入 `~/.cursor/mcp.json` 的 `mcpServers`，然后 Reload MCP。

## 第 3 步：使用

### 统计分析

- `对 examples/data/survey_study.sav 做描述统计和可靠性分析`
- `用 examples/data/experiment_study.sav 做独立样本 t 检验（group 分组，posttest）`
- `对 examples/data/mediation_study.sav 做中介分析：autonomy → satisfaction → performance`
- `对 examples/data/long_study.sav 做混合模型：score ~ group + time，subject=id`

### 论文级出图

- `画 examples/data/survey_study.sav 学习投入总分的直方图（带正态密度），PNG 300dpi`
- `用 examples/data/survival_study.sav 画按 treatment 分组的 KM 生存曲线`

图表工具返回 1950×1500 @300dpi 文件路径，可直接用于投稿。
