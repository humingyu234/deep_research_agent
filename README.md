# Deep Research Agent

一个面向“研究型问答”场景的 Agent 原型项目。

它的核心思路不是直接把用户问题丢给搜索，然后机械拼接结果，而是把整个过程拆成一条更清楚的链路：

```text
Planner -> Search -> Selector -> Reflect -> Summarizer -> Reporter
```

你可以把它理解成一个会先列研究提纲、再查资料、再筛资料、最后写小结和总报告的研究助手。

---

## 项目在做什么

这个项目当前想解决的问题很直接：

1. 用户先给出一个大问题
2. 系统把大问题拆成更适合搜索的子问题
3. 系统对搜索结果做筛选，而不是全量吃掉
4. 系统判断信息是否足够，不够就继续改写 query 再搜
5. 最终输出每个子问题的小结，以及一份整体研究报告

它现在更像一个持续迭代中的原型系统，而不是已经完工的产品。

---

## 当前核心链路

### 1. Planner

文件：

- `agent/planner.py`

作用：

- 根据用户原始问题判断 query 类型
- 按类型拆成更适合搜索的子问题

当前已经支持的 query 类型包括：

- `definition`
- `trend`
- `preference`
- `howto`
- `general`

---

### 2. Search

文件：

- `agent/search.py`

作用：

- 根据当前 query 执行检索
- 返回标题、摘要、来源等基础搜索结果

---

### 3. Selector

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

这一步很关键，因为当前 Summarizer 还不是强语义总结器，所以前面必须先把“菜洗干净”。

---

### 4. Reflect

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

---

### 5. Summarizer

文件：

- `agent/summarizer.py`

作用：

- 把筛选后的结果压缩成更像研究小结的结构

当前输出结构为：

1. 一句话结论
2. 2~3 条支撑点
3. 必要时补一句不确定性

目标不是“写更长”，而是“提炼得更像样”。

---

### 6. Reporter

文件：

- `agent/reporter.py`

作用：

- 把所有子问题的小结收束成一份最终报告

当前 Reporter 的目标不是简单拼接 summary，而是形成一个更高层的整体判断。

---

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

---

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

---

## 如何运行

在项目根目录执行：

```bash
python -m app.main
```

如果你在虚拟环境里运行，也可以先激活 `.venv` 再执行。

---

## 当前项目状态

这个项目当前处于“原型增强阶段”。

已经完成的方向：

- 主链路已跑通
- Planner 已从固定模板升级为按 query 类型拆题
- Selector 已进入第二轮增强，开始更严格筛结果
- Summarizer 已从“摘要拼盘”升级为“结论 + 支撑点 + 不确定性”
- Reflect 已开始收紧，不再轻易 `enough`
- Reporter 已开始从 summary 拼接器转向整体结论合成器

还没有完成的方向：

- 统一编码与终端显示
- 统一搜索结果的数据结构
- 提高 Summarizer 的抽象提炼能力
- 让 Reporter 给出更像研究总述的高层判断
- 增加测试与配置管理

---

## 项目文档

- `PROJECT_STATE.md`
  - 记录当前目标、架构、约束和下一步
- `PROJECT_LOG.md`
  - 记录改动历史、设计决策、验证情况和后续建议

---

## 接下来会继续做什么

下一阶段更值得继续打磨的方向：

1. 继续增强 Selector，让进入 Summarizer 的结果更干净
2. 继续提升 Summarizer 的提炼能力，而不只是压缩摘要
3. 继续收紧 Reflect，减少“过早 enough”
4. 继续增强 Reporter，让整体结论更像研究报告里的总述

---

## 项目定位说明

这个仓库现在最重要的价值，不在于功能很多，而在于：

- 各模块职责越来越清楚
- 每次升级都围绕主链路质量
- 结构适合继续一步一步长成更成熟的系统

diff --git a/c:\Users\Administrator\Desktop\deep_research_agent\README.md b/c:\Users\Administrator\Desktop\deep_research_agent\README.md
new file mode 100644
--- /dev/null
+++ b/c:\Users\Administrator\Desktop\deep_research_agent\README.md
@@ -0,0 +1,144 @@
+# deep_research_agent
+
+一个以“拆题、检索、筛选、反思、总结、汇报”为主链路的研究型 Agent 原型项目。
+
+当前项目的重点，不是做一个功能堆满的成品，而是把核心链路逐步打磨清楚：
+
+`Planner -> Search -> Selector -> Reflect -> Summarizer -> Reporter`
+
+## 项目目标
+
+这个项目想解决的是：
+
+- 用户给出一个大问题
+- 系统先把大问题拆成更适合搜索的子问题
+- 再搜索、筛选和判断信息质量
+- 最后把结果压缩成研究小结和整体报告
+
+直观理解，它像一个“会先列提纲，再查资料，再整理观点”的研究助手。
+
+## 当前架构
+
+项目当前的核心模块如下：
+
+- `app/main.py`
+  - 主流程入口，负责把各模块串起来
+- `agent/state.py`
+  - 状态容器，保存原问题、子问题、搜索结果和总结
+- `agent/planner.py`
+  - 根据 query 类型拆题
+- `agent/search.py`
+  - 执行搜索
+- `agent/selector.py`
+  - 对搜索结果去重、过滤、打分、选 Top-K
+- `agent/reflector.py`
+  - 判断当前结果是否足够回答子问题
+- `agent/rewriter.py`
+  - 在信息不足时改写搜索 query
+- `agent/summarizer.py`
+  - 生成“一句话结论 + 支撑点 + 不确定性”
+- `agent/reporter.py`
+  - 合成最终研究报告
+
+## 当前主流程
+
+1. 用户输入研究问题
+2. Planner 拆出子问题
+3. Search 搜索资料
+4. Selector 过滤杂乱结果
+5. Reflect 判断信息是否足够
+6. 不够则 Rewriter 改写 query 继续搜
+7. Summarizer 生成每个子问题的小结
+8. Reporter 合成整体结论
+
+## 当前特点
+
+- Planner 已支持按 query 类型拆题，而不是所有问题都套固定模板
+- Selector 已支持：
+  - 去重
+  - 去营销稿
+  - 压掉重复转述
+  - 优先保留更像报告/调研/框架的内容
+  - 默认只保留 Top-3 结果给 Summarizer
+- Summarizer 当前输出结构为：
+  - 一句话结论
+  - 2~3 条支撑点
+  - 必要时补一句不确定性
+- Reflect 已开始做更严格的质量检查，而不是轻易 `enough`
+
+## 运行方式
+
+当前项目是一个命令行原型。
+
+在项目根目录运行：
+
+```bash
+python -m app.main
+```
+
+如果你使用虚拟环境，也可以先激活 `.venv` 再运行。
+
+## 当前目录结构
+
+```text
+deep_research_agent/
+├─ agent/
+│  ├─ planner.py
+│  ├─ search.py
+│  ├─ selector.py
+│  ├─ reflector.py
+│  ├─ rewriter.py
+│  ├─ summarizer.py
+│  ├─ reporter.py
+│  └─ state.py
+├─ app/
+│  └─ main.py
+├─ models/
+│  └─ schema.py
+├─ PROJECT_STATE.md
+├─ PROJECT_LOG.md
+└─ README.md
+```
+
+## 当前状态
+
+当前项目仍然属于“原型增强阶段”：
+
+- 主链路已经跑通
+- 架构比最初清楚很多
+- 但还没有完成生产级工程化
+
+目前已知还可以继续优化的方向包括：
+
+- 统一编码和终端显示
+- 统一搜索结果的数据结构
+- 增强 Reflect 的判定策略
+- 提升 Summarizer 的抽象能力
+- 给 Reporter 更强的总体归纳能力
+- 增加测试
+
+## 项目文档
+
+- `PROJECT_STATE.md`
+  - 当前目标、架构、约束与下一步
+- `PROJECT_LOG.md`
+  - 项目改动日志、设计决策、验证情况和后续建议
+
+## 后续计划
+
+接下来更值得继续打磨的方向：
+
+1. 继续增强 Selector，让输入给 Summarizer 的结果更干净
+2. 提升 Summarizer 的提炼能力，而不只是压缩摘要
+3. 继续收紧 Reflect，减少“过早 enough”
+4. 让 Reporter 生成更像研究报告的总体判断
+
+## 说明
+
+这个仓库当前更像一个持续迭代中的研究型 Agent 实验项目。
+
+它的价值不在于“功能一下子很多”，而在于：
+
+- 每一层职责越来越明确
+- 每次升级都围绕主链路质量
+- 适合继续一步一步长成一个更成熟的系统
