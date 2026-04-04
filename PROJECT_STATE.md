# PROJECT_STATE

## 当前目标
先把入口从“单 research 主链”稳定升级为“Task Router + 多 workflow 系统”，在这个基础上再继续推进 `Clarifier v2` 与 `LLM Planner v1`，而不是继续在单链上做局部补丁。

## 当前架构
`Task Router -> workflow selection`

当前已有 workflow：
- `RESEARCH`
  - `Clarifier -> Planner -> Search -> Selector -> Reflector -> Rewriter -> Summarizer -> Reporter`
- `ADVICE`
  - `Clarifier -> light search -> advice synthesis`
- `QUICK_ANSWER`
  - `light search -> quick answer synthesis`
- `UNSUPPORTED`
  - 轻降级输出

## 当前稳定面
- `baseline-v1-stable` 已建立。
- `mini_eval` 已建立并可日常使用。
- `variant_eval` 固定 5 题已稳定通过。
- `Clarifier v2` 已切到“模型主判定，规则兜底”。
- `Task Router v1` 已接入 CLI，并通过 `router quick checks`。
- 搜索缓存第一版已接入。
- 本地环境已支持自动读取 `.env.local / .env`。

## 当前最新判断
- `full_eval`：主骨架稳定。
- `variant_eval`：固定泛化面稳定。
- 当前项目已经从“V1 能跑”推进到“V1 稳定可迭代”。
- 但这不再等同于“真实问题分布上已经扎实”。

## 当前瓶颈判断
- 当前最关键的瓶颈已经不是“模块名还缺什么”，而是：
  - 任务是否先走对 workflow
  - `Clarifier` 与 `Planner` 是否只服务该服务的问题
  - `ADVICE / QUICK_ANSWER` 轻链是否足够贴题
- 现阶段更重要的是：
  - 保持稳定面不回退
  - 禁止“固定题刷题式”优化
  - 先把路由正确性和 workflow 边界收稳

## 当前升级顺序共识
### 近线能力升级
- 先重做“什么叫收稳”的关闭标准。
- `Task Router v1` 优先。
- `Clarifier v2` 紧随其后。
- `LLM Planner v1` 已启动，当前进入第一轮验证期。
- 固定评估面继续作为监控面，但不再被视为充分条件。
- 后续验证方式必须同时包含：
  - 固定评估面
  - 新样本抽查
  - 真实手测

### 后续基础设施升级
- `task system`
- `skill loading`
- `context compression`

说明：
- `task system v1` 已提前接入一个轻量钩子，但当前先冻结，不继续扩。
- `scratchpad / central_report / citation appendix` 也先保留现状，不作为当前主线继续深挖。
- 后续是否继续做这些基础设施，等近线能力升级顺序推进后再继续。

## 长期方向
- 不靠无限补规则治本。
- 绝对不能出现“固定题刷题”的现象。
- planner 的长期演进路线：
  - `规则粗路由 + LLM 结构化规划 + 校验`
- clarifier 的长期演进路线：
  - `模型主判定 + 规则粗兜底 + 澄清后重写研究输入`
- router 的长期演进路线：
  - `模型主判定 + 结构化 JSON + 多 workflow 分流`
- 更后面再考虑：
  - `Deep Scraper`
  - 更强 planner
  - 产品化 workspace

## 当前高标准要求
- 目标不是“固定题全过”，而是：
  - `Selector / Reflector / Summarizer / Reporter` 在明确范围内对真实问题分布更稳、更诚实
- 以后任何模块如果要判定为“收稳”，至少同时满足：
  1. 固定评估面通过
  2. 真实手测通过
  3. 新样本抽查不过分漂
  4. 改进不是靠无限补表面规则实现的
- 如果做不到以上条件，只能说：
  - “初版可用”
  - 或“在当前测试面稳定”
  - 不能说“已经稳了”

## 当前项目级全局原则
- 不要为了局部某个短期改错或者优化，损害整体全部的系统优化。
- 不可以陷入贪心式修补。
- 任何改动都要先从全局看：
  - 是否伤整体架构
  - 是否让顺序跑偏
  - 是否为了眼前修一题而损害长期路线
- 后续默认工作方式：
  - 关键改动先做 AI review
  - 再做自动测试
  - 再做真实手测
  - 重点验证行为，不迷信代码表面是否“看起来合理”

## 对照“四刀”的当前状态
- 第一刀 `Clarification & Refinement`：
  - 已从 `Clarifier v1` 进入 `Clarifier v2` 启动阶段
  - 已切到“模型主判定，规则兜底”
  - 已有 quick checks / integration checks
- 第二刀 `Iterative Search-Read-Reason`：
  - 已有 `Search -> Reflector -> Rewriter` 多轮循环
- 第三刀 `Dynamic Synthesis & Scratchpad`：
  - 已补基础版 `scratchpad / central_report`
  - 但完整 `context compression` 还没做完
- 第四刀 `Citation & Fact-checking`：
  - 已补基础版 `Source_ID`
  - 最终报告已开始展示基础版 citation appendix
  - 但更细粒度的结论级 citation 绑定还没做完

## 已记住的后续整理项
- 运行产物清理与保留策略。
- `.cache/`、`evals/*_runs/`、`evals/*_summaries/` 的开源整理。
- 历史乱码/编码脏文件统一清理。
- 本地敏感配置统一走 `.env.local`，不写死进代码。

## 文档分工
- `PROJECT_LOG.md`：完整历史记录版，保留关键改动、决策、坑点、解决方式与阶段判断。
- `PROJECT_STATE.md`：当前状态总览版，只保留当前项目状态、主线、顺序共识与后续提醒。

## 当前目录纪律
- 源码只继续收在：
  - `agent/`
  - `app/`
  - `models/`
- 验证只继续收在：
  - `quick_checks/`
  - `evals/`
- 运行产物只继续收在：
  - `outputs/`
  - `.cache/`
- 不再轻易增加新的平行目录。
- 不再为了某个局部实验就长一套新的结构。
- 以后优先做“现有模块成熟化”，不是“继续加模块名”。

## 当前新增架构标尺
- 从 `claw-code-parity` 这类 CLI agent / runtime 仓库中，当前已经明确吸收并会持续拿来对照本项目的 5 条原则：
  1. 入口层要轻：
     - `app/main.py` 只负责启动、初始化、转交，不继续承担越来越多业务判断。
  2. 系统要有运行时大脑：
     - 后续要逐步长出更明确的 orchestration / runtime core，不让复杂调度散在入口附近。
  3. 工具层和工作流层要分开：
     - `search` 更偏工具能力，`planner / reflector / summarizer` 更偏 workflow 节点。
  4. 配置、状态、缓存、任务记录等要当系统能力处理：
     - 不再在业务流程里随手散写。
  5. 先路由，再执行：
     - `Task Router + Multi-Workflow` 继续作为主线方向，不再回退成“所有问题一条链”。
- 这 5 条不是“学习笔记”，而是当前项目后续所有架构判断的标尺。

## 当前新增验证面
- `router quick checks`
  - 已接入，当前通过。
- `advice_eval`
  - 已接入第一版自动回归。
  - 当前先覆盖 4 道 advice 题。
  - 最新一轮结果：
    - `clean_cases = 4 / 4`
    - `router_misroute = 0`
    - `clarifier_miss = 0`
    - `research_leak = 0`
    - `source_pollution = 0`
    - `template_mbti_overreach = 0`
    - `boundary_missing = 0`

## 当前主线
- 当前不再继续加模块名。
- 当前主注意力已从 Advice 链切回 `RESEARCH` 主链。
- 当前最值得收的两件事是：
  1. `LLM Planner v1` 的真实规划质量
  2. `Task Router` 的持续分流稳定性
- `Advice workflow` 当前先稳住，不继续大改。
- `LLM Planner v1` 当前状态：
  - 已接入主链
  - 已通过 `py_compile`
  - 已通过 `planner quick checks: 6/6`
  - 但仍只算“第一轮验证通过”，不能直接说已经收稳
- `Runtime` 收口已开始做第一刀：
  - `app/main.py` 已新增轻量 `Runtime` 包装层
  - `main()` 已改为通过 `runtime.run_task(...)` 进入主流程
  - 这一步属于入口减压，不属于新增能力
- `Runtime` 收权已进入第二刀：
  - `Runtime.run_task(...)` 已开始真正拥有任务生命周期入口
  - 当前已接管：
    - `ResearchState` 初始化
    - routing 阶段状态更新
    - route 应用与 workflow 分发
  - 当前仍未大拆 `run_research_workflow(...)`

## 当前必须记住的项目短板
- 迭代速度过快时，容易出现：
  - review 跟不上
  - 架构控制跟不上
  - 先救火再对齐主线
- `app/main.py` 这类胶水层必须严控职责，不能再次膨胀成超级入口文件。
- `Clarifier / Router / Planner` 的边界必须持续保持清晰。
- 任何时候都不能因为某一轮 eval 或某一题手测炸了，就立刻走局部救火式扩逻辑。

### 2026-04-03 Runtime 状态补充
- Runtime.run_task 已实际拥有 ResearchState 初始化、路由执行和 workflow 分发入口。
- main.py 当前可编译、可继续迭代；本轮以入口稳定性恢复为主，未开始抽取 _research_loop。
- 遗留事项：删除旧全局 run_task、继续把 research 主循环从 run_research_workflow 中抽出。
- 旧的全局 `run_task(...)` 已删除，入口层不再保留双轨任务启动路径。
- `_research_loop(...)` 已从 `run_research_workflow(...)` 中抽出；Research 主链当前已完成入口收权后的第一轮内部收口。
- `PROJECT_LOG` 中早先那句“research loop 抽取尚未开始”已过期，应以本轮状态为准。
### 2026-04-04 Runtime 当前状态更新
- `Runtime` 已开始真正承担：clarify、route、checkpoint、search trace、research loop、light workflow、research workflow。
- `main()` 当前仅保留：读输入、创建 task、建立日志、调用 `runtime.run_task(...)`。
- `RESEARCH` 主链的第一轮内部收口已完成：`_research_loop(...)` 已独立出来。
- 当前更适合先稳住并做真实冒烟，不宜立刻继续大拆。

## 2026-04-04 Search Status Update
- Search is now in v2 stage 1: candidate pool quality control is live.
- Search currently supports: domain trust classification, source scoring, weak-source filtering, stale-results early stop, tighter similar-cache reuse, and legacy-cache normalization.
- Search v2 has not yet introduced full-page scraping or planner-type-specific source bias templates.
- Main current bottleneck should be revalidated on real RESEARCH samples before touching reflector.

## ???????2026-04-04?
- Search v2 ??? provider ????
- ?? `agent/search.py` ???
  - `SEARCH_PROVIDER=auto`?? Tavily key ??? Tavily??? DDGS
  - `SEARCH_PROVIDER=tavily`??? Tavily?????? DDGS
  - `SEARCH_PROVIDER=ddgs`???? DDGS
- ??????????????????????????????? DDGS???????? provider ? Research ?????
- ??????????? provider ??????
  1. ?? Tavily key ???????? 3 ???? research ?
  2. ?? Tavily ? DDGS ? trend / comparison / timeline ???????????
  3. ?????????? Search v2 Stage 2????? source bias / provider bias?

## ???????2026-04-04?
- Search v2 ? source scoring ????? Tavily ?????????
- ??? `trust_counts` ?????????
  - ?????/??/????????????? `unknown`
  - ??????? Search v2 Stage 2???????????? source bias
- ????????
  1. ??????????? `trust_counts` ??? status ????????
  2. ????? `reflector` ????? `false_insufficient`


## 2026-04-04 Reflector ????
- `reflector` ????????????????
- ?????? `driver / risk / change` ??????????????????????????????????? `enough`????????
- ?? `variant_eval` ???
  - `cases_with_insufficient = 1`
  - `reflect_false_insufficient = 1`
- ?????
  - `rewriter` ????
  - `search` ??? Tavily + Search v2 ?????????
  - `reflector` ????????????
- ?????????????? 1 ? hard case ??????????? planner/source bias???????? reflector?


## 2026-04-04 ???????Reflector ????

- `reflector.py` ???????????????????? `insufficient`?
- ?????driver/risk ???????????????????????????
- ?????timeline/change ? complex-comparison ????? `reflect_false_insufficient`????????????? Reflector??????????????????????
- ??????????? 2 ??????????????????? Reflector?

## 2026-04-04 Selector 当前状态更新
- `selector.py` 已完成一轮定点收口，当前重点处理的是：
  - comparison 题里的弱相关就业/教育类误命中
  - timeline-change 题里的瓶颈/约束类材料筛选
- 当前验证信号：
  - `variant-timeline-solid-state-commercialization` 已恢复到 `insufficient=0`
  - `variant-comparison-junior-swe-demand` 仍有 2 个 `general` 子问题不足
  - `variant-driver-enterprise-agent-adoption` 仍保留 1 个 driver 机制解释不足样例
- 当前判断：
  - `selector` 这轮有效，但 remaining failures 已不再主要是全局 selector 噪音
  - 下一步更像需要定点检查 comparison-general 子问题的 planner/search 覆盖，以及 driver 子问题的机制材料供给

## 2026-04-04 Evaluate 方向记录
- 已确认后续新增一个长期方向：把当前项目中的评估收敛能力逐步抽象为独立 evaluate layer，并以未来开源为目标设计边界。
- 当前判断：最值得抽象和开源的是评估层，而不是立即开源整个 research agent 主体。
- 需要持续沉淀的对象包括：
  - case schema
  - runner
  - failure taxonomy
  - insufficient handling
  - summary / report artifact pipeline

### Planner 当前状态（2026-04-04 23:19）
- 已修正：definition 题在同时带『为什么重要』『核心区别』等措辞时，不再误判为 comparison/driver。
- 当前回归结果：variant_eval -> cases_with_insufficient=0，reflect_false_insufficient=0，planner_drift=3。
- 当前判断：planner 已恢复稳定，remaining issue 是题型贴合度仍偏泛，尤其 preference / timeline / driver 的模板仍需后续定点收敛。
