# Eval Summary 20260328_041432

- 测试题数量：5
- 出现 `insufficient` 的题目数量：0

## 评分层（计数视角）

```json
{
  "summary_repetition": 0,
  "insufficient_handling_error": 0,
  "planner_drift": 0,
  "selector_noise": 0,
  "report_over_repetition": 0,
  "reflect_focus_mixup": 0,
  "reflect_false_enough": 0,
  "reflect_false_insufficient": 0,
  "summary_noise": 0,
  "summary_not_answering": 1,
  "total_cases": 5,
  "cases_with_insufficient": 0
}
```

## 总览
- `baseline-definition-llm` | `definition` | insufficient=0 | tags=no_obvious_failure
- `driver-ai-agent-2026` | `driver` | insufficient=0 | tags=no_obvious_failure
- `selector-noise-english-learning-app` | `high-noise-preference` | insufficient=0 | tags=no_obvious_failure
- `timeline-solid-state-battery` | `timeline-trend` | insufficient=0 | tags=summary_not_answering
- `complex-ai-agent-employment` | `complex-comparison` | insufficient=0 | tags=no_obvious_failure

## 逐题摘要

## baseline-definition-llm
- 题目：什么是大语言模型的 Transformer 架构？
- 类型：definition
- 难度：easy
- 主要目标模块：planner-search-summarizer
- 设计意图：基准测试，检查系统在纯定义题上是否能稳定拆题、搜索和总结。
- 子问题统计：4
- `insufficient` 数量：0
- 失败标签：no_obvious_failure
- 详细运行记录：`evals\eval_runs\20260328_041432_baseline-definition-llm.json`

### 子问题状态
- `definition` | `enough` | 什么是大语言模型的 Transformer 架构？ 的定义或基本含义是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 什么是大语言模型的 Transformer 架构？ 的核心组成、关键机制或工作原理是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 什么是大语言模型的 Transformer 架构？ 容易和哪些相关概念混淆，它们的区别是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | 什么是大语言模型的 Transformer 架构？ 为什么值得关注，当前常见应用或代表场景有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：529 字符


## driver-ai-agent-2026
- 题目：为什么 2026 年 AI Agent 会加速落地？
- 类型：driver
- 难度：hard
- 主要目标模块：selector-reflector-summarizer
- 设计意图：击穿因果类软肋，观察是否能找到真正解释驱动因素的材料。
- 子问题统计：4
- `insufficient` 数量：0
- 失败标签：no_obvious_failure
- 详细运行记录：`evals\eval_runs\20260328_041432_driver-ai-agent-2026.json`

### 子问题状态
- `definition` | `enough` | 为什么 2026 年 AI Agent 会加速落地？ 当前最值得关注的核心问题是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `driver` | `enough` | 为什么 2026 年 AI Agent 会加速落地？ 背后的主要影响因素或关键变量有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | 为什么 2026 年 AI Agent 会加速落地？ 当前常见的表现、案例或实际情况有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `risk` | `enough` | 为什么 2026 年 AI Agent 会加速落地？ 还存在哪些争议、限制或值得继续研究的点？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：599 字符


## selector-noise-english-learning-app
- 题目：现在市面上最好的 AI 英语学习软件是哪个？
- 类型：high-noise-preference
- 难度：hard
- 主要目标模块：search-selector-reporter
- 设计意图：搜索结果天然高噪音，测试 selector 是否能压住营销稿和榜单软文。
- 子问题统计：4
- `insufficient` 数量：0
- 失败标签：no_obvious_failure
- 详细运行记录：`evals\eval_runs\20260328_041432_selector-noise-english-learning-app.json`

### 子问题状态
- `general` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 当前主流可选项有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 最值得参考的评价维度或选择标准是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 各主要选项的优缺点、适用人群或使用场景分别是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 在不同目标、预算或约束下，综合建议应该怎么给？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：537 字符


## timeline-solid-state-battery
- 题目：过去五年固态电池的技术突破时间线是什么？
- 类型：timeline-trend
- 难度：medium
- 主要目标模块：planner-summarizer-reporter
- 设计意图：测试长跨度趋势题，观察 summary 会不会写成流水账。
- 子问题统计：4
- `insufficient` 数量：0
- 失败标签：summary_not_answering
- 详细运行记录：`evals\eval_runs\20260328_041432_timeline-solid-state-battery.json`

### 子问题状态
- `definition` | `enough` | 过去五年固态电池的技术突破时间线是什么？ 过去几年的关键时间节点或里程碑有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 过去五年固态电池的技术突破时间线是什么？ 每个阶段最重要的技术突破、事件或代表案例是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `driver` | `enough` | 过去五年固态电池的技术突破时间线是什么？ 这条时间线背后的主要推动力量或转折点是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `change` | `enough` | 过去五年固态电池的技术突破时间线是什么？ 从当前时间线看，接下来可能的演进方向是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：558 字符


## complex-ai-agent-employment
- 题目：AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？
- 类型：complex-comparison
- 难度：hard
- 主要目标模块：planner-reporter
- 设计意图：测试复合嵌套题，观察系统是否能拆解、对比并最后收束出不重复的总报告。
- 子问题统计：4
- `insufficient` 数量：0
- 失败标签：no_obvious_failure
- 详细运行记录：`evals\eval_runs\20260328_041432_complex-ai-agent-employment.json`

### 子问题状态
- `definition` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 涉及的主要比较对象分别是什么表现？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 它们之间最关键的差异体现在哪些维度？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `driver` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 这些差异背后的主要原因或约束是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 基于这些差异，可以得出什么判断、选择建议或应对策略？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：658 字符

