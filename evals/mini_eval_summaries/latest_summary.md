# Eval Summary 20260328_054914

- 测试题数量：3
- 出现 `insufficient` 的题目数量：2

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
  "reflect_false_insufficient": 2,
  "summary_noise": 0,
  "summary_not_answering": 0,
  "total_cases": 3,
  "cases_with_insufficient": 2
}
```

## 总览
- `baseline-definition-llm` | `definition` | insufficient=0 | tags=no_obvious_failure
- `selector-noise-english-learning-app` | `high-noise-preference` | insufficient=1 | tags=insufficient_but_sounds_final, reflect_false_insufficient
- `complex-ai-agent-employment` | `complex-comparison` | insufficient=1 | tags=insufficient_but_sounds_final, reflect_false_insufficient

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
- 详细运行记录：`evals\mini_eval_runs\20260328_054914_baseline-definition-llm.json`

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
- 总报告长度：541 字符


## selector-noise-english-learning-app
- 题目：现在市面上最好的 AI 英语学习软件是哪个？
- 类型：high-noise-preference
- 难度：hard
- 主要目标模块：search-selector-reporter
- 设计意图：高噪音推荐题，专门用于观察 selector 和 reporter 是否稳定。
- 子问题统计：4
- `insufficient` 数量：1
- 失败标签：insufficient_but_sounds_final, reflect_false_insufficient
- 详细运行记录：`evals\mini_eval_runs\20260328_054914_selector-noise-english-learning-app.json`

### 子问题状态
- `general` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 当前主流可选项有哪些？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 最值得参考的评价维度或选择标准是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `definition` | `enough` | 现在市面上最好的 AI 英语学习软件是哪个？ 各主要选项的优缺点、适用人群或使用场景分别是什么？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `insufficient` | 现在市面上最好的 AI 英语学习软件是哪个？ 在不同目标、预算或约束下，综合建议应该怎么给？
  原因：当前有效结果太少，信息覆盖面还不够。

### 快速观察
- 总报告是否生成：是
- 总报告长度：599 字符


## complex-ai-agent-employment
- 题目：AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？
- 类型：complex-comparison
- 难度：hard
- 主要目标模块：planner-reporter
- 设计意图：复杂比较题，覆盖当前 V1 最容易失真的深层因果解释场景。
- 子问题统计：4
- `insufficient` 数量：1
- 失败标签：insufficient_but_sounds_final, reflect_false_insufficient
- 详细运行记录：`evals\mini_eval_runs\20260328_054914_complex-ai-agent-employment.json`

### 子问题状态
- `definition` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 涉及的主要比较对象分别是什么表现？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `general` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 它们之间最关键的差异体现在哪些维度？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。
- `driver` | `insufficient` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 这些差异背后的主要原因或约束是什么？
  原因：当前材料更多是在描述趋势现象，还没有充分解释背后的驱动因素或作用机制。
- `general` | `enough` | AI Agent 普及对 2026 年中美两国的初级程序员就业分别有什么影响，有哪些应对策略？ 基于这些差异，可以得出什么判断、选择建议或应对策略？
  原因：当前结果不只是相关，而且已经较明确地回答了这道子问题，可以进入总结阶段。

### 快速观察
- 总报告是否生成：是
- 总报告长度：649 字符

