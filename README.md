# Deep Research Agent

一个面向研究型问答场景的 Agent 原型项目。

它的核心目标不是“把搜索结果堆出来”，而是把研究流程拆成更清楚的几层：

```text
Planner -> Search -> Selector -> Reflect -> Summarizer -> Reporter
```

你可以把它理解成一个会先列提纲、再查资料、再筛资料、最后写小结和总报告的研究助手。

## 项目目标

这个项目当前想解决的是：

1. 用户先输入一个大问题
2. 系统把大问题拆成更适合搜索的子问题
3. 系统搜索资料，并先筛掉杂乱结果
4. 系统判断信息是否足够，不够就继续改写 query 再搜
5. 最后输出每个子问题的小结，以及一份整体研究报告

它现在更像一个持续迭代中的原型系统，而不是已经完工的成品。

## 当前核心链路

### Planner

文件：

- `agent/planner.py`

作用：

- 根据用户原始问题判断 query 类型
- 按类型拆成更适合搜索的子问题

当前支持的 query 类型：

- `definition`
- `trend`
- `preference`
- `howto`
- `general`

### Search

文件：

- `agent/search.py`

作用：

- 根据当前 query 执行检索
- 返回标题、摘要、来源等基础搜索结果

### Selector

文件：

- `agent/selector.py`

作用：

- 对搜索结果做“编辑台式”的清洗和筛选

当前重点能力：

- 去掉明显营销稿
- 去掉重复转述
- 过滤低质量来源
- 优先保留更像报告、调研、研究、框架类的内容
- 最终只保留 Top-K 结果给后续总结模块

### Reflect

文件：

- `agent/reflector.py`

作用：

- 判断当前筛选后的结果，是否已经足够回答子问题

当前会检查的方向包括：

- 是否有足够可用结果
- 结果来源是否过于单一
- 是否缺少研究型内容
- 子问题如果问“驱动因素 / 风险 / 限制”，结果里是否真的出现相应信号
- 是否只是泛泛趋势话术重复

### Summarizer

文件：

- `agent/summarizer.py`

作用：

- 把筛选后的结果压缩成更像研究小结的结构

当前输出结构为：

1. 一句话结论
2. 2 到 3 条支撑点
3. 必要时补一句不确定性

### Reporter

文件：

- `agent/reporter.py`

作用：

- 把所有子问题的小结收束成一份最终报告
- 尝试形成一个更高层的整体判断

## 当前主流程

项目主入口：

- `app/main.py`

当前执行顺序：

1. 用户输入研究问题
2. Planner 拆子问题
3. Search 搜索资料
4. Selector 清洗并选出 Top-K 结果
5. Reflect 判断这些结果够不够
6. 如果不够，Rewriter 改写 query 继续搜索
7. Summarizer 输出子问题小结
8. Reporter 合成整体报告

## 当前目录结构

```text
deep_research_agent/
├─ agent/
│  ├─ planner.py
│  ├─ search.py
│  ├─ selector.py
│  ├─ reflector.py
│  ├─ rewriter.py
│  ├─ summarizer.py
│  ├─ reporter.py
│  └─ state.py
├─ app/
│  ├─ __init__.py
│  └─ main.py
├─ models/
│  └─ schema.py
├─ PROJECT_STATE.md
├─ PROJECT_LOG.md
└─ README.md
```

## 如何运行

在项目根目录执行：

```bash
python -m app.main
```

如果你使用虚拟环境，也可以先激活 `.venv` 再运行。

## 当前项目状态

这个项目当前处于“原型增强阶段”。

已经完成的方向：

- 主链路已跑通
- Planner 已从固定模板升级为按 query 类型拆题
- Selector 已进入第二轮增强，开始更严格筛结果
- Summarizer 已从“摘要拼盘”升级为“结论 + 支撑点 + 不确定性”
- Reflect 已开始收紧，不再轻易 `enough`
- Reporter 已开始从 summary 拼接器转向整体结论合成器

还可以继续优化的方向：

- 统一编码与终端显示
- 统一搜索结果的数据结构
- 提高 Summarizer 的抽象提炼能力
- 让 Reporter 给出更像研究总述的高层判断
- 增加测试与配置管理

## 项目文档

- `PROJECT_STATE.md`
  - 记录当前目标、架构、约束和下一步
- `PROJECT_LOG.md`
  - 记录改动历史、设计决策、验证情况和后续建议

## 后续计划

下一阶段更值得继续打磨的方向：

1. 继续增强 Selector，让进入 Summarizer 的结果更干净
2. 继续提升 Summarizer 的提炼能力，而不只是压缩摘要
3. 继续收紧 Reflect，减少“过早 enough”
4. 继续增强 Reporter，让整体结论更像研究报告里的总述

## 项目定位说明

这个仓库当前最重要的价值，不在于功能很多，而在于：

- 各模块职责越来越清楚
- 每次升级都围绕主链路质量
- 结构适合继续一步一步长成更成熟的系统
