# Deep Research Agent

一个正在持续迭代的研究型 Agent 系统原型。

它的目标不是“把搜索结果堆出来”，而是把复杂问题拆成更清楚的处理流程，并用评估闭环不断收紧质量。

当前项目已经从“单条 research 主链”升级到：

`Task Router -> Multi-Workflow System`

也就是先判断问题类型，再决定走哪条 workflow。

## 当前工作流

### 1. `RESEARCH`
适合：
- 客观、事实性、需要证据支持的问题
- 比较、时间线、驱动因素、趋势分析这类题

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
- 这条链当前优先保证“贴题、克制、不离谱”
- 默认不再把开放网页搜索结果直接喂进最终建议

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

## 核心模块

位于 [agent](/c:/Users/Administrator/Desktop/deep_research_agent/agent)：

- [router.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/router.py)：任务路由，决定问题走哪条 workflow
- [clarifier.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/clarifier.py)：需求澄清，补边界、目标、偏好
- [planner.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/planner.py)：研究题拆题
- [search.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/search.py)：搜索与缓存
- [selector.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/selector.py)：结果筛选
- [reflector.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/reflector.py)：证据是否足够
- [rewriter.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/rewriter.py)：不够时改写 query
- [summarizer.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/summarizer.py)：子问题总结
- [reporter.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/reporter.py)：最终报告收束
- [light_answer.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/light_answer.py)：Advice / Quick Answer 轻链生成
- [scratchpad.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/scratchpad.py)：中央草稿、来源索引
- [tasks.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/tasks.py)：任务状态与持久化
- [state.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/state.py)：运行时状态
- [env_loader.py](/c:/Users/Administrator/Desktop/deep_research_agent/agent/env_loader.py)：读取 `.env.local / .env`

入口位于 [main.py](/c:/Users/Administrator/Desktop/deep_research_agent/app/main.py)。

## 目录分层

### 源码
- [agent](/c:/Users/Administrator/Desktop/deep_research_agent/agent)：核心逻辑
- [app](/c:/Users/Administrator/Desktop/deep_research_agent/app)：入口
- [models](/c:/Users/Administrator/Desktop/deep_research_agent/models)：结构定义

### 验证
- [quick_checks](/c:/Users/Administrator/Desktop/deep_research_agent/quick_checks)：模块级快验证
- [evals](/c:/Users/Administrator/Desktop/deep_research_agent/evals)：慢速回归、基线、变体题

### 运行产物
- [outputs](/c:/Users/Administrator/Desktop/deep_research_agent/outputs)：任务、报告、日志
- `.cache/`：缓存

### 项目文档
- [PROJECT_LOG.md](/c:/Users/Administrator/Desktop/deep_research_agent/PROJECT_LOG.md)：完整开发历史
- [PROJECT_STATE.md](/c:/Users/Administrator/Desktop/deep_research_agent/PROJECT_STATE.md)：当前状态总览

## 当前结构纪律

项目从现在开始遵守这几条：

1. 不再为了局部短期优化，损害整体架构。
2. 不允许为了固定题好看而刷题。
3. 不轻易增加新模块名，优先做已有模块成熟化。
4. 不轻易增加新目录，优先放进现有分层。
5. 任何模块只有在“固定评估面 + 真实手测 + 新样本抽查”都过关后，才可以说接近稳定。

## 当前阶段判断

当前不是“继续加模块”的阶段，而是：

- 路由正确性
- workflow 边界
- 模块成熟度
- 真实手测体验

也就是说，项目现在最重要的不是“再长功能名”，而是“让已有系统真正做对”。

## 本地配置

项目支持自动读取：
- `.env.local`
- `.env`

参考模板见：
- [\.env.example](/c:/Users/Administrator/Desktop/deep_research_agent/.env.example)

## 运行

```powershell
.\.venv\Scripts\python.exe .\app\main.py
```

## 快速检查

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py
```

也可以只跑某一套：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite router
```
