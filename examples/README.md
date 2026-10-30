# 真机样例数据与归档图

> 六组贴近论文场景的 `.sav` + 11 张代表性 PNG，用于演示与回归验证 `spss_chart_*`。
>
> 图片规格：PNG **1950×1500 @300 dpi**  
> 引擎：上游在 **Windows + SPSS 32** 归档；本 fork 在 **macOS + SPSS 27** 复验分析与出图链路。

## 目录

- `data/` — 场景数据（含变量 / 值标签）
- `charts/` — 真机导出的归档 PNG

## 数据集

| 文件 | 场景 | 样本量 | 关键变量 |
|------|------|--------|----------|
| `data/survey_study.sav` | 问卷：大学生学习投入 | 200 | `gender` / `major` / `q1`–`q12` / `cognitive` / `affective` / `behavioral` / `engagement_total` |
| `data/experiment_study.sav` | 实验：记忆训练前后测 | 120 | `group`（训练/对照）/ `pretest` / `posttest` / `gain` |
| `data/survival_study.sav` | 生存：治疗方案随访 | 150 | `treatment` / `time` / `status`（1=事件，0=删失） |
| `data/mediation_study.sav` | 中介：自主性→满意度→绩效 | 300 | `autonomy` / `satisfaction` / `performance` |
| `data/longitudinal_study.sav` | 纵向**宽表**：3 次重复测量 | 60 | `id` / `group` / `time1` / `time2` / `time3` → `spss_repeated_measures_anova` |
| `data/long_study.sav` | 纵向**长表**：id × time | 180 | `id` / `group` / `time` / `score` → `spss_mixed` / `spss_genlinmixed` |

宽表与长表分数已对齐，便于 RM-ANOVA 与 MIXED 对照；不要把宽表直接丢给 MIXED，也不要把长表当成 RM-ANOVA 的多列时间变量。

## 图表清单（`charts/`）

| 图 | 场景 | 工具 |
|----|------|------|
| `survey_engagement_histogram_density.png` | 问卷 | `spss_chart_histogram_density` |
| `survey_engagement_by_major.png` | 问卷 | `spss_chart_bar_error` |
| `survey_engagement_by_gender.png` | 问卷 | `spss_chart_errorbar` |
| `experiment_posttest_boxplot.png` | 实验 | `spss_chart_boxplot` |
| `experiment_gain_errorbar.png` | 实验 | `spss_chart_errorbar` |
| `experiment_posttest_bar.png` | 实验 | `spss_chart_bar` |
| `survival_km_curve.png` | 生存 | `spss_chart_km_curve` |
| `survival_time_histogram.png` | 生存 | `spss_chart_histogram` |
| `mediation_autonomy_performance_scatter.png` | 中介 | `spss_chart_scatter` |
| `mediation_satisfaction_performance_scatter.png` | 中介 | `spss_chart_scatter` |
| `mediation_performance_histogram_density.png` | 中介 | `spss_chart_histogram_density` |

## 自然语言示例（给 Agent）

```text
对 examples/data/experiment_study.sav 做独立样本 t 检验（group 分组，posttest）
用 examples/data/mediation_study.sav 做中介：autonomy → satisfaction → performance
画 examples/data/survey_study.sav 学习投入总分直方图（带正态密度），PNG 300dpi
对 examples/data/long_study.sav 做混合模型：score ~ group + time，subject=id
对 examples/data/longitudinal_study.sav 做重复测量 ANOVA（time1–time3，group）
用 examples/data/survival_study.sav 按 treatment 画 KM 曲线
```

## 复现

```bash
# 1) 重新生成样例数据（固定随机种子）
python scripts/make_sample_data.py

# 2) 真机导出归档图（需本机 SPSS + 授权）
python scripts/archive_sample_charts.py
```

macOS 若未自动发现安装：

```bash
export SPSS_INSTALL_PATH="/Applications/IBM SPSS Statistics 27"
```

## 在 MCP 工具中使用

任选 `.sav` 作为 `data_file`，例如：

- KM：`spss_chart_km_curve(time="time", status="status", group="treatment", data_file="examples/data/survival_study.sav")`
- 直方图：`spss_chart_histogram_density(variable="engagement_total", data_file="examples/data/survey_study.sav")`
- 箱线：`spss_chart_boxplot(variable="posttest", category="group", data_file="examples/data/experiment_study.sav")`

完整 Agent 教程见 [docs/tutorial.md](../docs/tutorial.md)。
