# PROJECT_STATE

## 当前目标
在保持 `Task Router + Multi-Workflow` 稳定的前提下，继续收敛 `RESEARCH` 主链的真实质量；后续再把当前形成的 evaluate 能力抽象出来，并逐步走向可开源的评估层。

## 当前架构
`Task Router -> workflow selection`

当前已有 workflow：
- `RESEARCH`
  - `Clarifier -> Planner -> Search -> Selector -> Reflector -> Rewriter -> Summarizer -> Reporter`
- `ADVICE`
  - `Clarifier -> light advice workflow`
- `QUICK_ANSWER`
  - `light search -> quick answer synthesis`
- `UNSUPPORTED`
  - 轻降级输出

## 当前稳定面
- `baseline-v1-stable` 已建立。
- `mini_eval` 已建立并可日常使用。
- `variant_eval` 固定 5 题当前已恢复稳定。
- `Clarifier v2` 已切到“模型主判定，规则兜底”。
- `Task Router v1` 已接入 CLI，并通过 `router quick checks`。
- `Runtime` 已完成入口收口，当前承担任务全生命周期管理。
- 搜索层当前已支持 Tavily + DDGS fallback。
- 本地环境已支持自动读取 `.env.local / .env`。

## 当前最新判断
- 当前项目已经从“V1 能跑”推进到“V1 稳定可迭代”。
- 当前真正要收的是 Research 链的题型贴合度和真实问题分布稳定性。
- `cases_with_insufficient` 和 `reflect_false_insufficient` 当前已压回到低位。
- 当前剩余显性尾巴更偏：`planner_drift`。

## 当前瓶颈判断
- 当前第一瓶颈不再是：
  - 单纯搜索源太差
  - 或 reflector 全局过严
- 当前更像是：
  - `planner` 在部分题型上仍然拆得偏泛
  - 题型感不够强
- 已知最需要继续关注的题型：
  - `preference`
  - `timeline`
  - `driver` 中仍偏泛的模板

## 当前升级顺序共识
### 近线能力升级
- 先稳定 workflow 分流和 research 主链。
- 不再为了单题大改模块。
- 继续坚持：
  - 固定评估面
  - 新样本抽查
  - 真实手测
- planner 的后续修正必须：
  - 小步
  - 可归因
  - 可回滚

### 后续基础设施升级
- `task system`
- `skill loading`
- `context compression`
- evaluate 层抽象

说明：
- `task system v1` 当前先冻结，不继续扩。
- `scratchpad / central_report / citation appendix` 当前先保留现状，不作为主线继续深挖。
- evaluate 层抽象已被正式记录为长期方向。

## 长期方向
- 不靠无限补规则治本。
- 绝对不能出现“固定题刷题”的现象。
- planner 的长期演进路线：
  - `规则粗路由 + LLM 结构化规划 + 校验`
- clarifier 的长期演进路线：
  - `模型主判定 + 规则粗兜底 + 澄清后重写研究输入`
- router 的长期演进路线：
  - `模型主判定 + 结构化 JSON + 多 workflow 分流`
- 搜索层的长期演进路线：
  - `更好的 provider + 候选池质量控制 + 未来可能的全文抓取`
- evaluate 层长期方向：
  - 将 `quick checks / variant_eval / failure taxonomy / insufficient-aware evaluation / run artifacts` 抽象为可复用能力，并最终考虑开源。

## 当前高标准要求
- 目标不是“固定题全过”，而是：
  - Research 链在明确范围内对真实问题分布更稳、更诚实
- 任何模块如果要判定为“收稳”，至少同时满足：
  1. 固定评估面通过
  2. 真实手测通过
  3. 新样本抽查不过分漂
  4. 改进不是靠无限补表面规则实现的

## 当前项目级全局原则
- 不要为了局部某个短期改错或者优化，损害整体系统。
- 不可以陷入贪心式修补。
- 任何改动都要先从全局看：
  - 是否伤整体架构
  - 是否让顺序跑偏
  - 是否为了眼前修一题而损害长期路线
- 后续默认工作方式：
  - 关键改动先做 review
  - 再做自动测试
  - 再做真实手测
  - 重点验证行为，不迷信代码表面是否“看起来合理”

## 当前主线状态
### Runtime
- `app/main.py` 当前已经较稳定。
- `Runtime.run_task(...)` 已承担：
  - state 初始化
  - route 应用与 workflow 分发
  - clarify / checkpoint / trace / research workflow / light workflow
- `main()` 当前保持较薄。

### Planner
- 当前 `agent/planner.py` 是：
  - `LLM 优先 + fallback` 结构
- 已修正 definition-like 题被误送进 `comparison/driver` 的问题。
- 当前剩余问题不再是“整体答不出来”，而是 `planner_drift` 仍存在尾巴。

### Rewriter
- 已按题型收过一轮。
- 已建立 `rewriter quick checks`。
- 当前已不是第一瓶颈。

### Search
- 当前进入 `Search v2 Stage 1`：
  - domain trust classification
  - source scoring
  - weak-source filtering
  - stale-results early stop
  - tighter similar-cache reuse
  - legacy-cache normalization
- 当前 provider：
  - Tavily 优先
  - DDGS fallback
- 当前判断：搜索层可以先稳住，不再作为第一刀继续猛改。

### Selector
- 已针对 comparison/employment 和 timeline-change 做过定点收口。
- 当前更像局部尾巴，而不是全局第一瓶颈。

### Reflector
- 已加入阶段性判断能力。
- `false_insufficient` 已明显下降。
- 当前不宜继续全局放松。

### Summarizer / Reporter / Scratchpad
- 当前结构可继续用。
- 暂不作为主线继续大改。

## 已记住的后续整理项
- 运行产物清理与保留策略。
- `.cache/`、`evals/*_runs/`、`evals/*_summaries/` 的开源整理。
- evaluate 层的可复用抽象。
- GitHub 门面继续成熟化。

## 文档分工
- `PROJECT_LOG.md`：完整历史记录版。
- `PROJECT_STATE.md`：当前状态总览版。

## 当前目录纪律
- 源码继续收在：
  - `agent/`
  - `app/`
  - `models/`
- 验证继续收在：
  - `quick_checks/`
  - `evals/`
- 运行产物继续收在：
  - `outputs/`
  - `.cache/`
- 不再轻易增加新的平行目录。
- 优先做“现有模块成熟化”，不是“继续加模块名”。

## 当前新增架构标尺
- 入口层要轻。
- 系统要有运行时大脑。
- 工具层和工作流层要分开。
- 配置、状态、缓存、任务记录等要当系统能力处理。
- 先路由，再执行。

## 强制编码原则（2026-04-05 起必须遵守）
1. 所有源码、模板、case 文件统一使用 UTF-8。
2. 不再使用可能隐式改编码的 shell 整文件重写流程。
3. 触碰中文密集文件后，提交前必须做编码 sanity check。
4. 只要发现 mojibake，先停功能开发，先修编码。

## 当前下一步
- 继续小步收 `planner_drift`。
- 保持 `search / selector / reflector` 主线稳定。
- 逐步把 evaluate 能力抽象为可复用层。

## Encoding Discipline Addendum
- The encoding rules above are project-level hard constraints, not optional advice.
- All future development and cleanup work must follow them.
- If encoding safety conflicts with speed, protect encoding first and do not write Chinese-heavy files through unsafe flows.
