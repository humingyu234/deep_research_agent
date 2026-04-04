# Deep Research Agent

一个面向复杂问题处理的 research agent 原型系统。

它的目标不是“把搜索结果堆出来”，而是把一个复杂问题拆成更清晰的研究流程，并通过持续评估，把系统一点点收敛成一个更可信的 agent。

当前项目已经从单条 research 主链，演进为：

`Task Router -> Multi-Workflow System`

也就是：先判断问题属于哪一类，再决定进入哪条 workflow，而不是把所有问题都硬塞进同一条重型 research 链。

---

## Why This Project Exists

很多 agent 原型都能“跑起来”，但真正困难的部分不是把模块接上，而是：

- 路由是否正确
- 工作流边界是否清晰
- 搜索结果是否真的可信
- 证据不足时系统是否足够诚实
- 一次次改动后，系统是否在真实问题上变得更稳，而不是只是在固定题上变好看

这个项目最重视的，不只是 workflow 本身，还有：

- 评估闭环
- failure taxonomy
- 真实手测
- 不足证据时的诚实降级
- 从“能跑”走向“可信”的收敛过程

---

## Current Workflows

### 1. `RESEARCH`
适合：
- 客观、事实性、需要证据支撑的问题
- 比较题、时间线题、驱动因素题、趋势分析题

当前链路：

`Clarifier -> Planner -> Search -> Selector -> Reflector -> Rewriter -> Summarizer -> Reporter`

### 2. `ADVICE`
适合：
- 个人建议
- 关系建议
- 职业选择
- 人生决策
- 主观偏好类问题

当前链路：

`Clarifier -> light advice workflow`

说明：
- 这条链优先保证“贴题、克制、不离谱”
- 默认不把开放网页搜索结果直接塞进最终建议

### 3. `QUICK_ANSWER`
适合：
- 简单事实
- 轻解释
- 直接问答

当前链路：

`light search -> quick answer synthesis`

### 4. `UNSUPPORTED`
适合：
- 输入极度混乱
- 当前系统不适合处理的问题

当前行为：
- 轻降级输出

---

## Core Modules

主要源码位于 `agent/`：

- `router.py`
  - 任务路由，决定问题走哪条 workflow
- `clarifier.py`
  - 需求澄清，补边界、目标、偏好
- `planner.py`
  - 把研究问题拆成子问题
- `search.py`
  - 搜索、缓存、provider 调度、来源质量控制
- `selector.py`
  - 结果初筛
- `reflector.py`
  - 判断当前证据是否足够进入总结
- `rewriter.py`
  - 证据不足时改写 query
- `summarizer.py`
  - 子问题总结
- `reporter.py`
  - 最终报告生成
- `light_answer.py`
  - Advice / Quick Answer 轻链输出
- `scratchpad.py`
  - 中央草稿、来源索引、citation appendix
- `tasks.py`
  - 任务状态与持久化
- `state.py`
  - 运行时状态
- `env_loader.py`
  - 读取 `.env.local / .env`

入口位于：

- `app/main.py`

---

## Current Architecture

### Source Code
- `agent/`：核心逻辑
- `app/`：CLI 入口
- `models/`：结构定义

### Validation
- `quick_checks/`
  - 模块级快速回归
- `evals/`
  - baseline / mini eval / variant eval / advice eval

### Runtime Artifacts
- `outputs/`
  - 任务、日志、报告
- `.cache/`
  - 搜索缓存

### Project Docs
- `PROJECT_LOG.md`
  - 完整开发历史、关键决策、踩坑记录
- `PROJECT_STATE.md`
  - 当前项目状态、主线、优先级判断

---

## Evaluation Philosophy

这个项目不把“固定题跑通”当成系统真正稳定。

当前评估方式包含：

- `quick_checks`
  - 模块级快速回归
- `mini_eval`
  - 高频小回归
- `variant_eval`
  - 固定泛化面
- `full_eval`
  - 更完整的主链验证
- `failure taxonomy`
  - 记录失败类型，而不是只看体感

当前共识：

一个模块只有同时满足下面几条，才接近可以说“稳定”：

1. 固定评估面通过
2. 真实手测通过
3. 新样本抽查不过分漂
4. 改进不是靠刷题和无限补规则实现的

也就是说：

**固定 eval 通过，只能说明“当前测试面稳定”；不能直接说明“真实问题分布已经稳了”。**

---

## Search Layer

当前搜索层已经升级到 `Search v2 Stage 1`，支持：

- 搜索 provider 调度
  - `Tavily`
  - `DDGS` fallback
- 来源质量分类
- source scoring
- 候选池过滤与排序
- stale results 检测
- 更严格的相似缓存复用策略

当前判断：

- `Tavily` 对 trend / comparison / timeline 类 research 题明显优于纯 DDGS
- 搜索层已经从“只会拿 snippet 回来”进化到“开始有候选池质量意识”

---

## Current Strengths

当前项目已经具备这些比较难得的部分：

- `Task Router + Multi-Workflow` 已经立起来
- `RESEARCH` 主链可运行且有真实收敛记录
- `ADVICE` / `QUICK_ANSWER` 已分流，不再所有问题都走 research
- `quick_checks + variant_eval + full_eval` 已形成基本评估闭环
- `failure taxonomy` 已进入日常迭代判断
- `Search v2` 已接入 provider 调度和来源质量层
- `outputs/tasks/ + central_report + report artifacts` 已经可追踪运行过程

---

## Current Limitations

这不是一个“已经完成”的系统，当前仍然有明确边界：

- planner 仍然会有题型贴合度偏泛的问题
- selector / reflector 仍需继续在真实问题上收敛
- 搜索层虽然已升级，但还没进入全文抓取阶段
- 当前的 citation 还是基础版，不是结论级严格绑定
- 系统已经从 toy demo 脱离，但还没有到“广义真实问题稳如产品”的阶段

如果你要用一句话概括当前状态，那就是：

**它已经是一个可信度不断上升的原型系统，但还不是一个完成态产品。**

---

## Local Setup

项目支持自动读取：

- `.env.local`
- `.env`

参考模板：

- `.env.example`

常见配置示例：

```env
DEEPSEEK_API_KEY=your_key_here
CLARIFIER_USE_LLM=1
PLANNER_USE_LLM=1

TAVILY_API_KEY=your_tavily_key_here
SEARCH_PROVIDER=auto
TAVILY_SEARCH_DEPTH=advanced
TAVILY_TOPIC=general
```

说明：
- `SEARCH_PROVIDER=auto`
  - 有 Tavily key 时优先用 Tavily
  - 否则回退到 DDGS

---

## Run

```powershell
.\.venv\Scripts\python.exe .\app\main.py
```

---

## Quick Checks

跑全部 quick checks：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py
```

只跑某一套：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite router
```

例如：

- `--suite planner`
- `--suite clarifier`
- `--suite rewriter`

---

## Project Discipline

当前项目遵守这些纪律：

1. 不为了局部短期优化损害整体架构
2. 不为了固定题好看而刷题
3. 优先做已有模块成熟化，而不是继续加模块名
4. 评估结论必须结合真实手测
5. 任何改动先看全局影响，再看局部收益

这意味着：

- 不贪心式修补
- 不因为某一题炸了就全局乱改
- 不因为某个模块局部看起来更聪明，就接受整体回退

---

## Current Stage

当前不是“继续加功能名”的阶段，而是：

- 收紧 workflow 边界
- 收紧 research 主链质量
- 保持评估面不回退
- 在真实问题分布上逐步提升可信度

换句话说：

现在最重要的不是“再长一个模块”，而是“让已有系统真正做对”。

---

## Long-Term Direction

长期方向不是无限补规则，而是：

- 更稳的 router
- 更强的 planner
- 更可靠的 research workflow
- 更诚实的 evidence handling
- 更好的 evaluate layer

后续一个明确方向是：

**把当前项目里的 evaluate 能力逐步抽象出来，并以开源为目标沉淀。**

这部分未来最值得开源的内容包括：

- quick checks
- variant / full eval runner
- failure taxonomy
- insufficient-aware evaluation
- summary / run artifact generation

---

## If You Are New Here

如果你第一次看这个项目，推荐阅读顺序：

1. `README.md`
2. `PROJECT_STATE.md`
3. `PROJECT_LOG.md`
4. `app/main.py`
5. `agent/search.py` / `agent/planner.py` / `agent/selector.py` / `agent/reflector.py`

这样会比直接扎进所有源码里更容易建立整体理解。
