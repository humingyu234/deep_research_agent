# PROJECT_LOG

## 1. 文档目的
- 记录项目关键改动、设计决策、验证结果、阶段判断与下一步计划。
- 避免每次回到项目时都重新梳理架构和上下文。
- 保留“为什么这么改、踩了什么坑、怎么解决”的完整历史。
- 作为后续 GitHub 整理、技术博客写作、项目复盘的原始素材。

## 2. 项目概况
- 项目名称：`deep_research_agent`
- 项目定位：一个以“拆题、搜索、筛选、反思、总结、汇报”为主链路的 research agent 系统原型。
- 长期目标：研究工作流引擎 / AI 研究顾问系统 / 未来可挂工作台形态的 engine。
- 当前阶段：`V1 主骨架稳定 + 固定泛化面稳定`

## 3. 主链路
`Planner -> Search -> Selector -> Reflector -> Rewriter -> Summarizer -> Reporter`

## 4. 评估闭环
- `quick_checks`：模块级快验证。
- `mini_eval`：高频小回归。
- `full_eval`：固定 baseline 稳定性验证。
- `variant_eval`：固定 5 题泛化验证。
- `failure_taxonomy`：记录每轮失败类型，不靠主观体感判断改动质量。

## 5. 当前总体判断
- 项目已经明显脱离 toy demo。
- 现阶段最有价值的不是某个单独模块，而是：
  - 白箱主链路
  - 评估闭环
  - failure taxonomy
  - 可持续迭代的方法论
- 当前已经不只是“baseline 稳”，连固定泛化面也已经稳定。

## 5.1 外部架构学习：当前已吸收的 5 条原则
- 最近开始并行阅读 `claw-code-parity` 这类 CLI agent / runtime 仓库，目标不是照抄代码，而是吸收更成熟的系统设计方法。
- 当前已经明确记住、后续会直接用于本项目判断的 5 条架构原则：
  1. 入口层要轻：
     - `main` 负责启动、接输入、初始化和转交，不应该继续膨胀成“前台 + 大脑 + workflow 拼接器”。
  2. 系统要有运行时大脑：
     - 真正复杂的调度、状态、权限、会话、对话循环，应该逐步收进更明确的 orchestration / runtime core，而不是散在入口附近。
  3. 工具层和工作流层要分开：
     - “会做什么事”与“什么时候做这件事”是两层。
     - 对本项目而言，像 `search` 更接近工具能力；`planner / reflector / summarizer` 更接近 workflow 节点。
  4. 配置、状态、权限、缓存、任务记录这类要当系统能力：
     - 不要在业务流程里随手加一段。
     - 要有清晰归属和分层。
  5. 先路由，再执行：
     - 不同问题走不同 workflow，不再把所有问题硬塞进同一条重 research 链。
- 以上 5 条后续将作为架构标尺：
  - 任何新增改动前先问：
    - 这会不会让入口继续变胖？
    - 这到底是工具层还是 workflow 层？
    - 这是不是系统能力，应该独立？
    - 这类问题是不是应该先被路由？

## 6. 关键历史记录

### 2026-03-28：Baseline 建立
#### 做了什么
- 跑通 `full_eval` 主链路。
- 建立 `baseline-v1-stable`。
- 明确区分：
  - `quick_checks`
  - `mini_eval`
  - `full_eval`

#### 解决了什么
- 项目从“能跑”进入“可回归、可对比、可持续优化”阶段。
- 后面每次改动不再靠感觉判断，而是有固定评估面。

#### 阶段判断
- 这是 V1 真正进入工程化迭代的起点。

---

### 2026-03-30 06:30：Clarifier 第一版接入
#### 为什么做
- 推荐题、复杂比较题、开放题存在明显的输入歧义。
- 如果不先澄清，后面的 planner / selector / summarizer 会被迫猜用户真实目标。

#### 做了什么
- 新增 `agent/clarifier.py`
- 扩展 `agent/state.py`
- 改造 `app/main.py`
- Clarifier 只接在 CLI 入口，不影响 baseline / eval 主链路。

#### 结果
- Clarifier 能触发推荐题、复杂比较题等场景。
- 后续又补了：
  - quick checks
  - integration checks
  - 与 planner 的基础衔接

#### 当前判断
- Clarifier 已从“能跑”推进到“局部可评估”。

---

### 2026-03-30 07:20：Planner 泛化修正
#### 为什么做
- 早期 `variant_eval` 暴露出明显泛化问题：
  - `definition` 和 `comparison` 混型
  - 抽象 timeline 问法识别不稳
  - 自然表达的 comparison 容易掉回通用模板

#### 做了什么
- 强化 `agent/planner.py`
- 重点补：
  - comparison 自然表达识别
  - abstract timeline 识别
  - contrastive definition 识别
  - driver 模板收口

#### 结果
- 固定 5 题版 `variant_eval` 稳定出现：
  - `planner_drift = 0`

#### 当前判断
- 规则路由还可以继续补明显边界。
- 但长期不会走“无限补规则”路线。
- planner 长期共识已经明确为：
  - `规则粗路由 + LLM 结构化规划 + 校验`

---

### 2026-03-30 07:51：driver 机制证据专项修复
#### 为什么做
- `planner` 稳住后，剩余问题集中在：
  - enterprise adoption
  - comparison 的 difference-cause
  - battery timeline 的 turning-point / driver
- 说明瓶颈重新回到机制证据质量，而不是题型识别。

#### 做了什么
- 读取失败题的最新运行 JSON。
- 定向增强：
  - `agent/selector.py`
  - `agent/rewriter.py`
- 补了 adoption、labor market、battery mechanism 等场景词。

#### 结果
- comparison / driver 类场景开始明显回升。

#### 当前判断
- `planner` 已不再是第一瓶颈。
- 当前真正要盯的是 `driver / mechanism / difference-cause` 证据层。

---

### 2026-03-30 08:00：搜索缓存第一版接入
#### 为什么做
- 完整 `eval` / `variant_eval` 最耗时的不是 planner / reflector / summarizer，而是重复联网搜索。
- 当只改下游逻辑时，每次都重新搜一遍浪费明显。

#### 做了什么
- 重写 `agent/search.py`
- 接入第一版搜索缓存：
  - `.cache/search/`
- 增加环境开关：
  - `SEARCH_CACHE_ENABLED`
  - `SEARCH_CACHE_REFRESH`
- 更新 `.gitignore`

#### 结果
- 相同 query 的重复联网搜索开始能复用。

#### 当前判断
- 这是第一层缓存，只先解“重复搜索”的浪费。
- 网页正文缓存留待后续需要时再补。

---

### 2026-03-30 08:18：variant_eval 回退修复
#### 为什么做
- 某一轮 5 题版 `variant_eval` 出现明显回退：
  - `planner_drift = 0`
  - `cases_with_insufficient = 4`
- 说明问题已不在 planner，而在：
  - `rewriter` 补词过长
  - `selector` 过度收紧

#### 做了什么
- 调整 `agent/rewriter.py`
  - 引入 `assemble_query()`
  - 限制建议词数量
  - 给 rewrite 统一长度上限
- 调整 `agent/selector.py`
  - 降低若干惩罚强度
  - recommendation 场景补 `review/comparison/rank`
  - 强过滤改成“至少保留 2 条才收紧”，避免把下游饿死

#### 结果
- 这轮修复的目标不是提升能力上限，而是修正过拟合式回退。

#### 当前判断
- 泛化场景里，不能只朝“更严格”一个方向收。
- query 长度、selector 收紧强度和候选保留数必须一起平衡。

---

### 2026-03-30 08:32：搜索稳态修复
#### 为什么做
- 某轮 `variant_eval` 看起来像 selector / rewriter 回退，实际读取 JSON 后发现大量是 `SEARCH_ERROR`。
- 也就是说，整题饿死的真实问题来自搜索层联网页面失败。

#### 做了什么
- 再次重写 `agent/search.py` 的回退逻辑。
- 新增：
  - query 归一化
  - 短 query 降级
  - 首句 query
  - prefix query
  - 相近缓存回退
  - 双写缓存
- 搜索缓存版本从 `v1` 升到 `v2`

#### 遇到的困难
- 表面上像 selector / rewriter 坏了，实际核心是 `SEARCH_ERROR`。
- 第一版缓存只支持 exact query，面对 rewriter 的长 query 几乎没帮助。
- `search.py` 历史上还有编码污染，局部补丁风险高。

#### 怎么解决
- 先读最新运行记录，再判断问题，不凭摘要拍脑袋。
- 不直接上重型数据库，先做轻量“相近缓存 + query 降级”。
- 对 `search.py` 采用整文件重写。

#### 结果
- recommendation / comparison / driver adoption 等题重新恢复到“至少有可用结果”。

#### 当前判断
- 第一瓶颈一度明确就是 `search` 稳态，而不是 planner。
- 修复目标不是提升模型理解，而是先防止因网络失败导致整题饿死。

---

### 2026-03-30 09:32：搜索修复生效，variant_eval 明显回升
#### 结果
- 固定 5 题版 `variant_eval` 回升到：
  - `cases_with_insufficient = 1`
  - `planner_drift = 0`
  - `reflect_false_insufficient = 1`

#### 说明
- 搜索层大面积无结果问题已退去。
- recommendation / comparison / driver adoption 已恢复正常。
- 剩余尾巴只剩：
  - `variant-timeline-solid-state-commercialization`
  - 其中 `driver` 子问题仍偏趋势描述，不够机制解释

#### 当前判断
- 重新回到“质量细修”阶段，不再是“基础设施救火”阶段。

---

### 2026-03-30 09:45：timeline-driver 单点收口
#### 为什么做
- 固定 5 题 `variant_eval` 只剩一个尾巴：
  - battery timeline 的 `driver`

#### 做了什么
- 定点增强 `agent/selector.py`
- 定点增强 `agent/rewriter.py`
- 加强 battery mechanism 相关信号：
  - 良率
  - 成本曲线
  - 界面稳定
  - 制造 / 可制造性
  - 车企 / OEM
  - 供应链
  - 政策 / 法规
  - 硫化物 / 氧化物路线

#### 当前判断
- 这是最后一个明显尾巴的定点修补。
- 如果仍不过，就要怀疑 reflector / summarizer，而不是继续折腾 planner / search / selector / rewriter。

---

### 2026-03-30 09:58：Reflector 二次收口
#### 为什么做
- 继续读运行记录后确认：
  - 机制材料其实已经被 selector / rewriter 带进来了
  - 但 reflector 仍主要按通用 driver 词判断，不够识别电池场景机制词

#### 做了什么
- 定点修改 `agent/reflector.py`
- 引入：
  - `BATTERY_SIGNAL_HINTS`
  - `BATTERY_DRIVER_HINTS`
  - battery mechanism support 放行逻辑

#### 结果
- 最终把 timeline-driver 这一个尾巴收掉。

#### 当前判断
- reflector 已不再死卡通用 driver 词命中，而能识别领域机制信号。

---

### 2026-03-30 10:08：固定 5 题 variant_eval 全通过
#### 这轮结果
- `cases_with_insufficient = 0`
- `planner_drift = 0`
- `reflect_false_insufficient = 0`
- `summary_noise = 0`
- `summary_not_answering = 0`

#### 通过的固定变体题
- `variant-definition-transformer-importance`
- `variant-driver-enterprise-agent-adoption`
- `variant-preference-speaking-english-tools`
- `variant-timeline-solid-state-commercialization`
- `variant-comparison-junior-swe-demand`

#### 这说明什么
- 当前不只是 baseline 稳，固定泛化面也已经稳住。
- V1 已从“结构稳定”推进到“结构 + 固定泛化面稳定”。

#### 阶段判断
- 这是一个阶段性收口点。

#### 待提醒事项
- 后面要统一处理运行产物管理：
  - `evals/*_summaries/`
  - `evals/*_runs/`
  - `.cache/`

---

### 2026-03-30 10:10：task system v1 提前落钩
#### 为什么做
- 当时判断项目已进入下一阶段升级，于是先落最轻的基础设施钩子。

#### 做了什么
- 扩展 `agent/state.py`
- 新增 `agent/tasks.py`
- 重写 `app/main.py`
- 支持：
  - task id
  - `task.json`
  - 状态流转
  - 日志路径
  - 报告路径

#### 遇到的困难
- `app/main.py` 旧版本存在明显乱码，普通增量补丁不稳定。

#### 怎么解决
- 对 `app/main.py` 采用整文件替换。

#### 当前判断
- 这是一个轻量基础设施钩子，不影响 eval 主链路。
- 当前先冻结，不继续扩。
- 原因不是它不对，而是当前主线顺序需要和近线能力升级重新对齐。

---

### 2026-03-30 10:20：日志编码事故与修复
#### 发生了什么
- `PROJECT_LOG.md` / `PROJECT_STATE.md` 出现大量乱码。
- 问题不是终端显示，而是文件内容本身被混编码污染。

#### 根因判断
- 历史日志里已经混入过脏内容。
- 后续为了不中断主线，曾继续在脏文件上追加内容。
- 结果导致文件一部分正常、一部分乱码。

#### 怎么修
- 不再局部补丁。
- 直接整文件重写为干净 UTF-8 中文版。

#### 当前决定
- `PROJECT_LOG.md` 保持“完整历史记录版”
- `PROJECT_STATE.md` 保持“当前状态总览版”
- 以后这两者职责分开：
  - `PROJECT_LOG.md`：开发过程、决策、踩坑、解决方式
  - `PROJECT_STATE.md`：当前状态、当前主线、当前判断

## 7. 当前结论
- V1 主骨架稳定。
- 固定 5 题 variant 泛化面稳定。
- 当前不应再无节制补规则。
- 后续应按已经约定好的升级顺序推进，而不是一边救火一边乱切线。

## 8. 后续提醒
- 后面要继续把“近线能力升级”和“基础设施升级”顺序彻底对齐。
- 后面要统一收：
  - 运行产物保留/清理策略
  - `.cache/` 的开源策略
  - eval 历史文件的整理策略

---

### 2026-03-30 10:35：参考“四刀”后完善后续计划，并落第三刀基础版
#### 背景
- 重新对齐了外部那套四刀思路：
  1. 意图收敛与反问
  2. 迭代式搜-读-想循环
  3. 动态记忆与草稿综合
  4. 严格溯源与引用绑定
- 对照当前项目状态后确认：
  - 第一刀：`Clarifier` 已有第一版，并已进入局部可评估状态
  - 第二刀：`Search -> Reflector -> Rewriter` 多轮 loop 已经在主链路里
  - 第三刀：此前只有 `task system v1` 钩子，但还没有真正的中央草稿
  - 第四刀：此前只有 source 保留，没有显式 `Source_ID` 绑定

#### 这轮做了什么
- 新增 `agent/scratchpad.py`
  - 负责生成高密度 scratchpad 条目
  - 负责维护 `Source_ID`
  - 负责渲染 `central_report.md`
- 扩展 `agent/state.py`
  - 新增 `scratchpad_entries`
  - 新增 `citation_index`
- 扩展 `agent/tasks.py`
  - `task.json` 现在会持久化：
    - scratchpad 条目
    - citation index
- 重写 `app/main.py`
  - 每完成一个子问题，就压缩成一条 scratchpad 记录
  - 每条记录都挂 `Source_ID`
  - 每轮都更新中央草稿：
    - `outputs/tasks/<task_id>/central_report.md`

#### 这轮结果
- `agent/state.py`、`agent/tasks.py`、`agent/scratchpad.py`、`app/main.py` 已全部通过 `py_compile`
- 本地冒烟验证通过：
  - scratchpad 条目可生成
  - `Source_ID` 可生成
  - `Central Report` 可渲染

#### 这轮意义
- 这不是完整的 context compression，也还不是严格 citation system 的最终版
- 但已经把第三刀和第四刀最关键的“落点”搭起来了：
  - 不再只是保留原始 results
  - 开始沉淀中央草稿
  - 开始显式绑定 `Source_ID`

#### 当前判断
- 现在项目里四刀映射已经更完整：
  - 第一刀：Clarifier v1
  - 第二刀：多轮搜-读-想 loop
  - 第三刀：scratchpad / central report 基础版
  - 第四刀：Source_ID 基础版
- 后续如果继续沿这条线推进，最自然的顺序是：
  1. 把 scratchpad 从“每题一条压缩记录”升级成更成熟的 context compression
  2. 把 `Source_ID` 从 task 内部引用，升级成最终输出层可见的 citation 绑定

---

### 2026-03-30 10:48：把 Source_ID 从内部索引推进到最终输出层
#### 背景
- 上一轮已经把 `scratchpad_entries`、`citation_index`、`central_report.md` 落了地。
- 但当时的 `Source_ID` 还只存在于任务内部：
  - `task.json`
  - `central_report.md`
- 用户打开最终研究报告时，还看不到显式引用附录。

#### 这轮做了什么
- 扩展 `agent/scratchpad.py`
  - 新增 `render_report_citation_appendix(state)`
  - 把 scratchpad 内部记录整理成最终可见的引用附录
- 更新 `app/main.py`
  - 新增 `build_final_report(state)`
  - 最终输出不再只是 reporter 生成的正文
  - 现在会自动在正文后拼接：
    - 子问题对应的 `Source_ID`
    - `Source_ID -> title | source` 的索引表

#### 这轮结果
- 最终研究报告现在已经能展示基础版 citation 附录。
- 第四刀不再只停留在 task 内部状态，而是进入用户可见层。

#### 遇到的问题
- 这一步如果直接重写 reporter，风险会比较高，因为会碰到已经稳定的报告主逻辑。

#### 怎么解决
- 这轮没有去动 `agent/reporter.py` 的主体逻辑。
- 改成在 `app/main.py` 的最终输出阶段拼接 citation appendix。
- 这样风险最小，也便于后续再决定要不要把 citation 深度并入 reporter。

#### 当前判断
- 现在第三刀和第四刀都已经有了用户可感知的基础形态：
  - 第三刀：中央草稿
  - 第四刀：最终报告可见的引用附录
- 下一步如果继续沿这条线推进，更应该做的是：
  1. 把 scratchpad 真正推进成 context compression
  2. 再考虑更细粒度的“结论句级 citation 绑定”

---

### 2026-03-30 11:12：重新确立高标准要求，明确禁止“固定题刷题”
#### 这轮为什么要记下来
- 真实手测问题：
  - `如果我想实现财富自由 我在20-30岁之间应该在意什么？需要怎么面对失败？你觉得应该在意这个阶段能不能赚钱吗？`
- 这次体验直接暴露出两个问题：
  - `Clarifier` 没触发
  - `Planner` 把开放人生策略题误拆成 timeline 题
- 这说明：
  - 固定题通过 != 真实问题也稳
  - 之前对部分模块“已经收了”的判断标准过早

#### 这轮重新确立的要求
- 从现在开始，绝对不能再把“固定题跑通”当成“系统整体扎实”。
- 以后目标不是“把固定题刷得更好看”，而是：
  - 让 `Selector / Reflector / Summarizer / Reporter` 在明确范围内对真实问题分布更稳
  - 遇到边界题时，系统要能诚实降级，而不是假装很懂
- 明确禁止：
  - 只围绕固定 baseline / fixed variant 反复打补丁
  - 因为固定 eval 过了，就宣称某模块“已经收了”

#### 新的关闭标准
- 以后任何模块如果要说“收稳”，至少同时满足：
  1. 固定评估面通过
  2. 真实手测通过
  3. 新样本抽查不过分漂
  4. 改进不是靠无限补表面规则实现的
- 如果达不到这四条，只能说：
  - “初版可用”
  - 或“在当前测试面上稳定”
  - 不能说“已经稳了”

#### 对后续模块质量的高标准要求
- 后面要重点盯住的不是“某道题能不能过”，而是：
  - `Selector`：对不同题型的选材是否稳定、不被噪音带偏
  - `Reflector`：是否能稳地识别“够 / 不够 / 方向对但证据弱”
  - `Summarizer`：是否真正回答问题，而不是把不成熟材料包装得像成熟结论
  - `Reporter`：是否最终仍然贴题、不夸大、不重复、不跑偏
- 高标准目标不是“所有问题都完美”，而是：
  - 在明确范围内广泛稳定
  - 超出边界时诚实降级

#### 新版优先级
- 经过这次纠偏后，后续最合理的顺序调整为：
  1. 先重做“关闭标准”，不再允许固定题刷题式收尾
  2. `Clarifier v2`
     - 方向：规则快速拦截 + 小模型判断是否需要澄清 + 生成关键追问
  3. `LLM Planner v1`
     - 方向：规则粗路由 + LLM 结构化规划 + 校验
  4. 新验证方式
     - 固定评估面 + 新样本抽查 + 真实手测并行
  5. 再继续：
     - `task system`
     - `skill loading`
     - `context compression`
  6. 更后面：
     - `Deep Scraper`
     - 更细粒度 citation / fact-check

#### 当前决定
- 不再继续无限补规则 `Planner`。
- `Clarifier` 不再被视为“已收尾模块”，而是重新回到主线升级对象。
- `task system / scratchpad / citation appendix` 先保留现状，但暂时不继续深挖，避免再被新想法带偏主线。

---

### 2026-03-30 11:24：启动 Clarifier v2，改成“规则 + 可开关模型判定”
#### 背景
- 真实手测问题暴露出：
  - `Clarifier` 之前的关闭判断过早
  - 它在固定样本上通过，但在真实开放题上漏触发
- 高标准要求下，这一步不能再继续靠“固定题通过”自我证明。

#### 这轮做了什么
- 重构 `agent/clarifier.py`
  - 旧版改成 `_rule_based_should_clarify(query)`
  - 新增可开关模型层：
    - `_llm_enabled()`
    - `_llm_should_clarify(query)`
    - `_extract_json_block(text)`
  - `should_clarify(query)` 现在的顺序是：
    1. 规则先拦明显问题
    2. 如果规则没拦住，且显式开启 `CLARIFIER_USE_LLM=1` 并提供 `DEEPSEEK_API_KEY`
    3. 再交给模型判断是否需要澄清
- 同时对规则层只做了一次很克制的补强：
  - 不再用“长度 <= 30”限制所有宽泛开放题
  - 对明显的个人策略/人生规划类问题加了一层高信号触发
- 更新 `quick_checks/clarifier_cases.json`
  - 新增长开放策略题回归样本
  - 不是为了刷刚才那道原题，而是为了防止这一类明显该澄清的问题再次漏掉

#### 这轮设计原则
- 这轮不是继续无限补规则。
- 真正的方向是：
  - 规则只做快速粗筛
  - 模型负责处理边界模糊、规则看不清的情况
- 这样做的目的不是“让 Clarifier 在固定题上更好看”，而是让它开始具备更抽象的泛化能力。

#### 当前判断
- `Clarifier` 现在不应再被视为纯规则终局。
- `Clarifier v2` 已正式启动，但当前只能算：
  - “规则层更稳”
  - “模型层已接上接口”
- 还不能说“Clarifier 已收稳”，因为后面还需要：
  - 真实手测
  - 新样本抽查
  - 模型开启后的实际体验验证

---

### 2026-03-30 11:31：修正 Clarifier 对“财富自由 / 人生阶段”类题的漏触发
#### 发生了什么
- 用户真实手测后反馈：
  - 刚才那类“财富自由 / 20-30 岁 / 面对失败 / 该不该在意赚钱”的问题仍然没有触发 `Clarifier`
- 这说明上一轮补的规则层仍然不够彻底。

#### 根因判断
- 上一轮虽然加了 `PERSONAL_STRATEGY_HINTS`
- 但实际判断里，这类问题仍然被挂在“宽泛开放题”的门后面
- 结果导致：
  - 某些长开放人生策略题依然会漏掉

#### 这轮做了什么
- 更新 `agent/clarifier.py`
  - 把 `PERSONAL_STRATEGY_HINTS` 升级成独立触发分支
  - 新增高信号关键词：
    - `财务独立`
    - `财务自由`
    - `赚钱`
    - `面对失败`
- 更新 `quick_checks/clarifier_cases.json`
  - 新增：
    - `clarifier-broad-financial-freedom-stage`
  - 直接覆盖用户刚才真实手测暴露出的这一类题型

#### 这轮结果
- `agent/clarifier.py` 已通过 `py_compile`
- `clarifier quick checks: 7/7 passed`
- 刚才用户手测暴露的这类问题，现在已经进入固定 clarifier 回归样本

#### 当前判断
- 这次修完后，`Clarifier` 对“个人策略 / 财富自由 / 阶段选择 / 如何面对失败”这类明显需要先收敛意图的问题更稳了
- 但仍然只能说：
  - “规则层又收住了一段”
  - 不能说“Clarifier 已彻底收稳”
- 后面仍然要继续按高标准盯：
  - 真实手测
  - 新样本抽查
  - 模型版开启后的体验

---

### 2026-03-30 11:40：把 Clarifier 调整成“模型主判定，规则兜底”
#### 背景
- 用户明确指出：
  - `Clarifier` 不该再继续走“穷举规则”路线
  - 高标准做法应当是：
    - 模型主判定
    - 规则只做很粗的明显兜底
- 这次反馈本质上是在纠偏：
  - 之前把早期保守策略错误延续到了 `Clarifier`

#### 这轮做了什么
- 更新 `agent/clarifier.py`
  - `ClarificationResult` 新增 `source`
    - 用来标记本次澄清来自 `llm` 还是 `rule`
  - `_llm_enabled()` 改成：
    - 只要有 `DEEPSEEK_API_KEY` 就默认可用
    - 只有显式设置 `CLARIFIER_USE_LLM=0` 才关闭
  - `should_clarify(query)` 改成：
    1. 有模型就先走模型
    2. 模型失败或不可用，再回退到规则
- 更新 `app/main.py`
  - CLI 现在会明确打印：
    - `[需求澄清][llm]`
    - 或 `[需求澄清][rule]`

#### 这轮意义
- `Clarifier` 现在不再是“规则主判定 + 模型 fallback”
- 而是正式切到：
  - “模型主判定 + 规则兜底”
- 这一步是对高标准要求的真正对齐，而不是继续打补丁

#### 当前判断
- 从这一刻开始，`Clarifier` 的主方向已经纠正过来。
- 后面仍然要验证的不是“固定题还过不过”，而是：
  - 真实手测里，模型是否真的更贴题
  - 情感/伴侣/人生策略/开放选择这类题是否不再被错误套模板

---

### 2026-03-30 11:52：补充项目级全局原则
#### 新增原则
- 不要为了局部某个短期改错或者优化，损害整体全部的系统优化。
- 不可以陷入贪心式修补。
- 后续所有改动，都要优先从全局看：
  - 会不会伤整体架构
  - 会不会让顺序跑偏
  - 会不会为了眼前修一题，把长期路线做歪

#### 这条原则的直接含义
- 不允许因为某个局部手测炸了，就立刻无节制补规则。
- 不允许因为某个局部结果好看，就误判为系统整体已经扎实。
- 不允许为了短期“先过掉”某个问题，牺牲后续整体演进路线。

#### 后续执行要求
- 以后每次改动前都要先判断：
  1. 这是在做全局正确的升级，还是局部贪心止血？
  2. 这一步会不会带来副作用，伤到更大的系统稳定性？
  3. 这一步是否符合当前已经约定好的主线顺序？

---

### 2026-03-30 12:02：接入本地环境自动加载，取消“每次手动设 key”
#### 背景
- 用户明确要求：
  - 标准继续按刚才定好的高标准走
  - 但不希望每次都在终端手动输入 `DEEPSEEK_API_KEY`
- 当前问题是：
  - 即使 `Clarifier` 已切到“模型主判定”，如果当前终端没有环境变量，仍然会退回规则

#### 这轮做了什么
- 新增 `agent/env_loader.py`
  - 自动读取项目根目录下：
    - `.env.local`
    - `.env`
- 更新 `agent/clarifier.py`
  - 模块加载时自动调用 `load_local_env()`
- 新增 `.env.example`
  - 作为本地配置模板
- 更新 `.gitignore`
  - 忽略：
    - `.env`
    - `.env.local`

#### 这轮结果
- 以后只要把 key 放进项目根目录的 `.env.local`
- 再直接运行：
  - `.\.venv\Scripts\python.exe .\app\main.py`
- `Clarifier` 就会自动读取本地环境配置，不需要每次手动在终端里重新 set

#### 当前判断
- 这一步没有改变主线路由逻辑，只是把“模型环境准备”变成默认本地行为
- 这样更符合当前全局要求：
  - 不为了局部手动操作干扰整体体验
  - 让后续真实手测更接近正常使用方式

#### 后续补充
- 已在项目根目录创建 `.env.local`
- 默认内容为：
  - `DEEPSEEK_API_KEY=your_deepseek_key_here`
  - `CLARIFIER_USE_LLM=1`
- 出于安全考虑，没有把真实 key 写进日志或代码文件

---

### 2026-03-31 10:15：正式插入 Task Router v1，入口从“单主链”切到“先路由，再选 workflow”
#### 背景
- 连续真实手测暴露出：当前最大问题已经不再是某个局部模块不够强，而是问题一开始就可能走错链。
- 典型例子：
  - 伴侣/人格匹配/人生建议这类题，被硬塞进 `driver / risk / change` 的 research 主链。
- 这说明：
  - 继续只补 `Clarifier` 或 `Planner`，是在错误前提上强化单主链。
  - 项目现在真正缺的是：`Task Router`

#### 这轮做了什么
- 新增 `agent/router.py`
  - 模型主判定
  - 强制结构化 JSON
  - 输出：
    - `task_type`
    - `confidence_score`
    - `needs_clarification`
    - `routing_reason`
  - 当前任务类型枚举：
    - `RESEARCH`
    - `ADVICE`
    - `QUICK_ANSWER`
    - `UNSUPPORTED`
- 新增 `agent/light_answer.py`
  - 为 `ADVICE / QUICK_ANSWER / UNSUPPORTED` 提供轻量 workflow
  - 不再硬走当前 research pipeline
- 重写 `app/main.py`
  - 入口现在改成：
    1. 先 `Task Router`
    2. 再决定走：
       - `RESEARCH` 重链
       - `ADVICE` 轻建议链
       - `QUICK_ANSWER` 快答链
       - `UNSUPPORTED` 轻降级链
  - `Clarifier` 不再是系统的绝对第一步，而是挂到合适 workflow 里
- 扩展：
  - `agent/state.py`
  - `agent/tasks.py`
  - 新增 task 级字段：
    - `task_type`
    - `router_source`
    - `routing_reason`
    - `routing_confidence`
- 扩展 `quick_checks`
  - 新增 `quick_checks/router_cases.json`
  - 新增 router suite

#### 验证结果
- `py_compile` 通过：
  - `agent/router.py`
  - `agent/light_answer.py`
  - `app/main.py`
  - `agent/state.py`
  - `agent/tasks.py`
  - `quick_checks/run_quick_checks.py`
- `router quick checks` 结果：
  - `3/3 passed`
  - 覆盖：
    - research 题
    - advice 题
    - quick answer 题

#### 这轮意义
- 这是当前项目从“单 workflow 系统”往“多 workflow 系统”的第一次正式架构升级。
- 重点不是再加一个模块名，而是：
  - 先判断任务类型
  - 再把问题送进正确链路
- 这次改动直接对应了前面反复确认的高标准要求：
  - 不再为了局部止血，继续在错误链路上打补丁
  - 不再把所有问题都硬塞进 research pipeline

#### 当前判断
- 核心模块名层面已经基本齐了。
- 现在项目的主要工作不再是“继续加模块”，而是：
  - 路由正确性
  - workflow 边界
  - 模块成熟度
- `Task Router v1` 已经正式进入当前主线。
- 当前顺序需要更新为：
  1. `Task Router v1`
  2. `Clarifier v2`
  3. `LLM Planner v1`
  4. 固定评估面 + 新样本抽查 + 真实手测

#### 当前还没收住的地方
- `Task Router v1` 现在只算起步版本，虽然 quick checks 已过，但还没经过足够多真实手测。
- `ADVICE / QUICK_ANSWER` 轻链这次先做的是可运行版本，不是最终成熟版。
- 当前目标不是立刻把多 workflow 一次做到完美，而是先把“明显走错链”的系统性问题消掉。

---

### 2026-03-31 10:28：先切掉 Advice 轻链的开放网页污染
#### 背景
- 第一轮 Advice 手测里，虽然：
  - `Task Router` 已经把伴侣建议题正确送进 `ADVICE`
  - `Clarifier` 也开始能问出贴题问题
- 但最终轻链结果仍然严重不合格：
  - 引用了情色站、小说站、同人站等明显脏来源
  - 说明当前 Advice 链如果继续默认复用开放网页搜索，会直接污染最终建议

#### 这轮做了什么
- 只改了一处：
  - `app/main.py`
- 新逻辑是：
  - `QUICK_ANSWER` 仍可默认走一次轻搜索
  - `ADVICE` 暂时默认不走开放网页搜索
  - 改成“模型建议为主，搜索不做默认输入”

#### 为什么这么做
- 这是一个非常克制、但全局上更正确的修正。
- 当前目标不是让 Advice 链立刻看起来“信息更多”，而是先保证：
  - 不被脏网页污染
  - 不把明显垃圾来源带进最终输出
- 这符合前面已经明确写下的项目原则：
  - 不能为了局部短期“多一点参考”，损害整体系统体验和路线

#### 验证
- `app/main.py` 已通过 `py_compile`

#### 当前判断
- 这一步不是 Advice workflow 的最终解。
- 它只是先把最伤体验的污染源切掉，让 Advice 轻链回到“至少不离谱”的状态。
- 下一步再继续盯：
  - Advice 输出是否贴题
  - 文风是否真像建议而不是伪研究报告
  - 是否还需要更克制的证据辅助机制

---

### 2026-03-31 10:40：收结构纪律，不再靠“继续长文件”推进项目
#### 背景
- 用户明确提出担心：
  - 文件越来越多
  - 继续做下去会不会越来越乱
- 这和当前项目阶段是对得上的：
  - 模块名层面已经基本齐了
  - 现在更需要的是结构纪律，而不是继续加功能名

#### 这轮做了什么
- 重写 `README.md`
  - 用干净版本重新说明：
    - 当前是 `Task Router -> Multi-Workflow System`
    - 当前有哪些 workflow
    - 核心模块分别做什么
    - 目录应该如何理解
    - 当前结构纪律是什么
- 更新 `PROJECT_STATE.md`
  - 新增“当前目录纪律”一节
  - 明确：
    - 源码只收在 `agent/ / app/ / models/`
    - 验证只收在 `quick_checks/ / evals/`
    - 运行产物只收在 `outputs/ / .cache/`
    - 不再轻易增加新的平行目录

#### 这轮意义
- 这一步没有增加任何新能力。
- 它的作用是把“项目现在到底是什么、哪些目录属于什么层、以后不该怎么继续长”写清楚。
- 这是当前阶段很必要的动作，因为项目已经从“缺模块”进入“怕发散、怕变乱”的阶段。

#### 当前判断
- 从这一刻开始，项目的默认原则应当是：
  - 少增文件
  - 少增目录
  - 优先做已有模块成熟化
  - 优先让结构更清楚，而不是继续堆复杂度

---

### 2026-03-31 10:55：补第一版 `advice_eval`，把新 workflow 纳入自动回归
#### 背景
- 当前系统已经从“单条 research 主链”切到了：
  - `Task Router -> Multi-Workflow`
- 但 `ADVICE` 轻链虽然手测已开始变好，仍然有几个明显风险：
  - 只是靠手感判断，不够量化
  - 容易再次出现 research 串味
  - 容易再次出现模板味过重、约束使用弱等问题
- 用户明确提出：
  - 希望像之前一样，测试能自动、能量化

#### 这轮做了什么
- 在现有 `evals/` 目录下补了第一版：
  - `evals/advice_eval_cases.json`
  - `evals/run_advice_eval.py`
- 没有新开平行测试目录，继续遵守当前目录纪律：
  - 验证仍然只收在 `evals/`

#### 这版 Advice Eval 目前检查什么
- `router_misroute`
- `clarifier_miss`
- `research_leak`
- `source_pollution`
- `constraint_usage_weak`
- `boundary_missing`
- `overclaim`
- `template_mbti_overreach`

#### 当前运行结果
- 已成功自动跑完 4 道 advice 题。
- 当前汇总结果是：
  - `router_misroute = 0`
  - `clarifier_miss = 0`
  - `research_leak = 0`
  - `source_pollution = 0`
  - `template_mbti_overreach = 2`
  - `clean_cases = 2 / 4`
- 这说明：
  - `Router + Clarifier` 这一层已经开始明显起作用
  - Advice 轻链已经不再出现最离谱的 research 串味和脏来源污染
  - 但“MBTI 模板味过重”仍然是当前最主要的 Advice 质量尾巴

#### 当前判断
- `advice_eval` 的意义不是证明 Advice 链“已经稳定”。
- 它的意义是：
  - 正式把新 workflow 拉回到“自动回归、可量化”轨道
  - 防止后面又退回只靠手感修 Advice
- 当前最值得继续收的，不是继续加模块，而是：
  1. `Router` 的真实分流稳定性
  2. `Advice` 输出去模板味、增强约束利用

---

### 2026-03-31 11:07：继续收 Advice 输出质量，先把模板味与边界表达压下去
#### 背景
- 第一版 `advice_eval` 跑完后，最明显的 Advice 尾巴变成了：
  - `template_mbti_overreach = 2`
  - `boundary_missing = 2`
- 这说明：
  - 方向已经对了
  - 但 Advice 输出还偏“MBTI 模板文”
  - 同时自动评估也在提示边界提醒不够稳定

#### 这轮做了什么
- 只收一处：
  - `agent/light_answer.py`
- 这次没有继续加新模块，也没有再开新目录。
- 具体动作是：
  1. 整文件重写成干净 UTF-8 版本，顺手清掉旧乱码风险
  2. Advice 生成层新增“强约束 / 弱约束”拆分
  3. 把“都行 / 看情况 / 无所谓”这类表达降级成弱约束，不再当成强偏好展开
  4. 把 Advice 输出强制固定成 4 段：
     - `## 我的直接判断`
     - `## 为什么这么看`
     - `## 边界提醒`
     - `## 可执行建议`
  5. 进一步压低 MBTI 类型名的使用：
     - 不允许再堆配对表
     - 最多只允许极少量、明确标注“仅供参考”的例子

#### 验证
- `agent/light_answer.py` 已通过 `py_compile`
- `advice_eval` 已重新跑完

#### 新结果
- 最新 `advice_eval` 结果已变成：
  - `router_misroute = 0`
  - `clarifier_miss = 0`
  - `research_leak = 0`
  - `source_pollution = 0`
  - `constraint_usage_weak = 0`
  - `boundary_missing = 0`
  - `template_mbti_overreach = 0`
  - `clean_cases = 4 / 4`

#### 当前判断
- 这不代表 Advice 链“已经对所有问题稳定”。
- 但至少说明：
  - `Router -> Clarifier -> Advice workflow` 这条新线
  - 已经从“方向正确但毛刺明显”
  - 进入了“第一版自动回归面干净”的状态
- 现在更合理的下一步不是继续大改，而是：
  - 让用户再做 2 到 3 轮真实手测
  - 看真实体验是否也同步变好

---

### 2026-04-01：固化后续开发方式，并正视当前项目的真实短板
#### 后续开发方式（必须执行）
- 以后每次大改、整文件重写、关键链路调整后，都要先做一轮 AI review。
- AI review 重点不看语法，而看：
  - 整体架构是否合理
  - 有没有明显 bug / edge cases / 状态流转问题
  - 当前改动的 Top 3 风险点和改进建议
- AI review 之后，必须继续做“行为验证”，而不是只看代码：
  - `quick_checks`
  - `advice_eval`
  - `variant_eval`
  - 真实手测
- 对核心文件的人工把关重点，后续固定为：
  - `app/main.py`
  - `agent/router.py`
  - `agent/clarifier.py`
  - `agent/light_answer.py`
- 人工把关时重点看：
  - 函数签名
  - 状态流转
  - prompt 模板
  - workflow 边界
- 后续每次关键改动完成后，日志里应补：
  - `AI review 结果`
  - `测试是否通过`
  - `架构风险判断`

#### 当前项目的真实评价（不客气版，已接受）
##### 值得肯定的部分
- 已经建立了评估闭环：
  - `quick_checks`
  - `evals`
  - `failure taxonomy`
- 结构纪律意识很强：
  - 避免平行目录爆炸
  - 优先整文件重写而不是脏补丁
  - 已开始明确源码 / 验证 / 运行产物分层
- 能主动纠偏：
  - 固定题刷题倾向
  - 只看固定 eval、不看真实手测的倾向
- 架构方向已经从单链升级到：
  - `Task Router + Multi-Workflow`
- 已开始往更严肃研究 Agent 方向走：
  - `scratchpad`
  - `Source_ID`
  - `citation appendix`

##### 必须正视的部分
- 迭代速度一度过快，review 和架构控制没有完全跟上。
- 曾多次出现：
  - 同一天高频改动
  - 整文件重写过多
  - 先救火再回头对齐主线
  - 先落钩子再冻结
- 这说明虽然日志在写，但实际执行中仍然容易滑向：
  - 快速 Vibe Coding
  - 局部救火
  - 先改再想
- 模块边界曾明显模糊：
  - `app/main.py` 一度承担过多胶水、路由、调度、输出拼接职责
  - `Clarifier / Router / Planner` 边界不够清晰
  - `Advice workflow` 早期只是“先切掉 research 污染”，远未成熟
- 高标准与实际执行曾有落差：
  - 口头强调“不刷固定题”“全局正确”“不贪心止血”
  - 但实际仍容易被某一轮 eval 或某一题手测牵着走

#### 由此得出的硬规则
- 大改前先回答：
  - 这刀解决的到底是什么架构问题？
- 任何整文件重写之后，先做：
  1. AI review
  2. 自动测试
  3. 真实手测
  再决定是否继续扩
- `app/main.py` 后续只允许承担调度与入口职责，不再继续塞业务判断。
- 遇到单题爆炸，先判断：
  - 是局部现象
  - 还是系统性问题
  不再直接用“救火式扩逻辑”处理

---

### 2026-04-02：Advice 链连续真实手测通过，更新当前判断但不夸大
#### 这轮发生了什么
- 在没有新增代码改动的前提下，连续做了多轮真实 `ADVICE` 手测，覆盖了：
  - 伴侣建议
  - 职业转行建议
  - 职场压力建议
  - 高中阶段关系处理
  - 医生面对 AI 冲击的职业焦虑
  - 大学生对官僚主义的价值观焦虑
- 这一轮重点不是“继续改代码”，而是验证：
  - `Task Router` 是否还会误分流
  - `Clarifier` 是否还能贴题追问
  - `Advice workflow` 是否会重新串回 research 口吻
  - 是否还会出现污染来源或明显离谱的建议

#### 这轮得到的结论
- 当前 `ADVICE` 链在真实手测面上表现明显稳定：
  - `Router` 没有误送回 `RESEARCH`
  - `Clarifier` 基本能问到贴题约束
  - Advice 输出保持了建议口吻
  - 未再出现脏来源污染
  - 对用户补充约束的利用较前几轮明显更好
- 当前更准确的判断应是：
  - `ADVICE` 链已经从“初版像样”进入“接近稳定可用”
  - 但还不能夸大成“已经对所有 advice 题稳定”

#### 特别记住：判断更新 != 代码提升
- 这轮没有新增代码改动。
- 因此，不应表述成“系统又被提升了一档”。
- 更准确的表述是：
  - 由于连续真实手测通过，当前我们对 `ADVICE` 链稳定性的认知更新了
  - 这是“验证带来的判断更新”，不是“新改动带来的能力提升”
- 后续必须严格区分：
  1. 代码改动带来的能力提升
  2. 更多验证带来的状态判断更新

#### 当前决策
- Advice 链当前不再继续大改。
- 当前最合理的做法是：
  - 先把这条线视为“已通过第一轮真实手测门槛”
  - 进入暂时稳住状态
  - 将主注意力切回项目主线
- 后续若 Advice 再出问题，再按：
  - AI review
  - 自动回归
  - 真实手测
  这三步处理，不重新回到局部救火式乱改。

---

### 2026-04-02：启动 `LLM Planner v1`
#### 为什么现在做
- 当前 `ADVICE` 链先稳住后，Research 主链里最限制上限的仍然是 `Planner`。
- 旧 `planner.py` 仍然是规则底盘，而且文件本身还有历史乱码残留。
- 继续在旧规则文件上补丁不划算，适合做一次“整文件、按架构重写”。

#### 做了什么
- 整文件重写 `agent/planner.py`，改成：
  - `LLM structured planning` 为主
  - `rule templates` 为回退
  - `light validator fallback` 为兜底
- 保留现有外部接口：
  - `classify_query()`
  - `build_subquestions()`
  - `plan_subquestions()`
- 新增 `PlannerDecision`，内部明确记录：
  - `query_type`
  - `sub_questions`
  - `source`
  - `reason`
  - `note`
- 扩展：
  - `agent/state.py`
  - `agent/tasks.py`
  让任务状态里能记录 planner 的来源和类型
- 调整 `app/main.py`
  - 在 research workflow 中打印：
    - `[规划器][llm]`
    - 或回退信息
- 更新 `.env.example`
  - 新增 `PLANNER_USE_LLM=1`

#### 当前验证
- `agent/planner.py`、`agent/state.py`、`agent/tasks.py`、`app/main.py` 已通过 `py_compile`
- `planner quick checks`：`6/6 passed`

#### 当前判断
- `LLM Planner v1` 已经真正接上主链，不再只是口头路线。
- 当前形态不是“纯 LLM 黑箱”，而是：
  - LLM 主规划
  - 规则模板回退
  - 轻校验兜底
- 这符合之前定下的长期路线：
  - `规则粗路由 + LLM 结构化规划 + 校验`

#### 当前仍然要记住的风险
- `planner quick checks` 目前主要还是在验证规则回退模板，不代表 LLM 规划面已经完全收稳。
- `LLM Planner v1` 仍需后续继续做：
  - Research 真实手测
  - 更高层回归
  - 必要时再收校验层

### 2026-04-03 | 轻量 Runtime 收口（第一刀）
#### 本轮动作
- 按“入口层要轻、系统要有运行时大脑”的标尺，先在 `app/main.py` 内引入了一个轻量 `Runtime` 包装层。
- 这一步没有新增新能力，也没有重写 workflow，只做了一件事：
  - 让 `main()` 不再直接调用 `run_task(...)`
  - 改为先实例化 `Runtime()`，再由 `runtime.run_task(...)` 接住入口

#### 为什么先做这一刀
- 当前项目已经进入 `Task Router + Multi-Workflow` 阶段，后续调度分支只会继续增加。
- 如果不先给入口加一个最轻的“运行时壳”，`app/main.py` 会继续向超级胶水文件膨胀。
- 这一步属于工程化收口，不会和“不要继续乱加模块/乱发散”的纪律冲突。

#### 当前验证
- `app/main.py` 已通过 `py_compile`

#### 当前判断
- 这还不算完成了 Runtime 重构，只是第一刀：
  - 先把入口调用关系收进 `Runtime`
  - 后续再视需要把更多调度职责逐步内聚进去
- 这是当前最克制、最符合全局纪律的动作。

### 2026-04-03 | Runtime 收权（第二刀）
#### 本轮动作
- 继续沿着上一刀推进，把 `Runtime` 从“薄壳包装”推进到“真正拥有任务生命周期入口”：
  - `Runtime.run_task(...)` 现在自己负责：
    - 构建 `ResearchState`
    - 更新 routing 状态
    - 调用 `apply_route(...)`
    - 选择并分发 workflow
- `main()` 仍然只做：
  - 读取输入
  - 创建任务
  - 建立日志输出
  - 调用 `runtime.run_task(...)`

#### 当前验证
- `app/main.py` 已通过 `py_compile`

#### 当前判断
- 这一步已经不再只是“抽类”，而是开始真正把入口控制权收进 `Runtime`。
- 还没有开始大拆 `run_research_workflow(...)`，因此本轮改动面可控。
- 下一步如果继续沿这条线走，最合理的是抽 `run_research_workflow(...)` 里的研究循环，而不是继续扩入口层。

## 2026-04-03 18:35 Runtime 收权后的入口修复
- 在 Runtime.run_task 中保留任务初始化、路由和 workflow 分发控制权，并加入顶层 failed 状态兜底。
- 修复 app/main.py 中一批历史遗留的乱码打印文案，恢复主入口与 research 循环的可编译状态。
- 当前状态：Runtime 已不再是纯包装壳，但旧的全局 run_task 仍保留为遗留路径，尚未删除；research loop 抽取尚未开始。
- 验证：`py_compile app/main.py` 通过。
- 清理 app/main.py 中已脱离主调用路径的旧全局 `run_task(...)` 死代码；现在入口只通过 `Runtime.run_task(...)` 进入任务生命周期。
## 2026-04-04 Research 主循环收口（第三刀）
- 从 `run_research_workflow(...)` 中抽出 `_research_loop(...)`，把搜索、筛选、反思、改写的多轮循环独立出来。
- `run_research_workflow(...)` 现在主要保留高层编排：clarify -> plan -> iterate sub-questions -> finalize report。
- 这一步没有新增能力，只是继续把 `RESEARCH` 主链从面条代码往可维护结构收拢。
- 验证：`py_compile app/main.py` 通过。
## 2026-04-04 Runtime 内聚继续推进
- 将 `_maybe_clarify(...)`、`_apply_route(...)`、`_checkpoint(...)`、`_emit_search_trace(...)` 全部收进 `Runtime`，让运行时核心不再只拥有入口，还开始拥有生命周期中的关键动作。
- `run_research_workflow(...)` 已继续瘦身：搜索、筛选、反思、改写的多轮循环被抽成 `Runtime._research_loop(...)`。
- 当前 `main.py` 的结构已从“能跑的大脚本”进入“有 Runtime 核心的入口文件”阶段，但仍保留部分 report/helper 级函数，后续继续按成熟化而不是大重构推进。
- 当前判断：这一轮改动主要是结构收口，不是新增能力；下一步应先做冒烟验证，再决定是否继续统一 light workflow 的 checkpoint 方式。
- 验证：`py_compile app/main.py` 通过。

## 2026-04-04 Search v2 Stage 1
- Rebuilt agent/search.py into Search v2 stage 1.
- Added source scoring, domain trust classification, weak-source filtering, stale-result detection, and stricter similar-cache reuse.
- Normalized legacy cached results on read so old cache entries also flow through the new ranking/filter layer.
- Current next step: run representative RESEARCH questions and then decide whether to tighten source bias further or move to reflector calibration.


## 2026-04-04 Search v2 Stage 1.5: Tavily Provider ??
- ? `agent/search.py` ??? provider ???`SEARCH_PROVIDER=auto|tavily|ddgs`
- ?? `TAVILY_API_KEY`?`TAVILY_SEARCH_DEPTH`?`TAVILY_TOPIC` ????
- ?? `_provider_order()`?`_search_once_tavily()`?`_search_once_ddgs()`?? `_search_once()` ????
- ???????? Tavily key ??? Tavily?? key ?????? DDGS
- ???? Search v2 ?????????stale detection????????
- ???????`py_compile agent/search.py`??? Tavily key ? DDGS fallback ??

## 2026-04-04 Search v2 Stage 1.6: Domain Trust ??
- ?? Tavily ????????????????? `unknown` ???????
- ??? `high`?`accenture.com`?`xinhuanet.com`?`ccf.org.cn`?`csia.org.cn`?`huawei.com`/`e.huawei.com`?`paper.people.com.cn`?`nsfc.gov.cn`
- ??? `medium`?`news.qq.com`?`baike.baidu.com`?`pdf.dfcfw.com`?`ifc.org`?`stcn.com`
- ??????????????????????? source scoring ???????????????? Tavily ??? `unknown` ???


### 2026-04-04 20:50 Reflector ?????????
- ???? `agent/reflector.py`
  - ?? `get_source_scores(...)`
  - ?? `has_strong_evidence_pool(...)`
  - ?? `has_stage_judgment_support(...)`
- ? `driver / risk / change` ????????????????? `insufficient`
- ????????? + ?????? + ????? + ????/??????????????? `enough`
- ??????????????????/????
- ??????? `evals/run_variant_eval.py`
  - `cases_with_insufficient`: 3 -> 1
  - `reflect_false_insufficient`: 3 -> 1
- ?????`reflector` ????????????? reflector??????? 1 ? hard case ????? planner/search/source ?????


## 2026-04-04 20:50 Reflector ?????????

### ????
- ? `agent/reflector.py` ??? `get_source_scores()`?`has_strong_evidence_pool()`?`has_stage_judgment_support()`?
- ? `driver / risk / change` ???????????????????????????????/???/?????????????????????????? `insufficient`?
- ?????????????????????????

### ??????
- ??????? Reflector ????????????????????????????????????
- Search + Tavily ?????????????Reflector ?????????? `reflect_false_insufficient`?

### ??
- `variant_eval` ????`variant-driver-enterprise-agent-adoption` ???? `insufficient`???? driver/risk ???????????????
- ???????? 2 ?? `reflect_false_insufficient`?
  - `variant-timeline-solid-state-commercialization`
  - `variant-comparison-junior-swe-demand`
- ??? Reflector ???????????????????????????? planner/reporter ???????

## 2026-04-04 Selector 定点收口：comparison + timeline-change
- 这轮没有做全局重写 `agent/selector.py`，而是只针对剩余顽固失败样例做定点修正。
- 对 `comparison` / employment 类子问题：
  - 增加了 `COMPARISON_CONTEXT_HINTS` 与 `EDUCATION_ADMISSIONS_HINTS`
  - 提高了“就业/劳动力市场/岗位/技能门槛”上下文信号权重
  - 对招生、课程、留学、培训类误命中材料加了更强惩罚
  - 对“高分域名但明显不贴 comparison/employment 主题”的结果更敢丢
- 对 `timeline` 里固态电池瓶颈/变化方向子问题：
  - 提高了 `battery_driver_hits` / `mechanism_hits` 的偏好
  - 对缺少“瓶颈 / 约束 / 产业化挑战”信号的材料加了更强惩罚
  - 让 selector 更倾向保留真正讲 constraint / bottleneck / breakthrough direction 的结果
- 验证：
  - `py_compile agent/selector.py` 通过
  - `variant_eval` 跑通
  - `variant-timeline-solid-state-commercialization` 变成 `insufficient=0`
  - `variant-comparison-junior-swe-demand` 从 `insufficient=3` 降到 `insufficient=2`
- 结论：
  - 这刀是有效的，但不是银弹
  - timeline/change 已明显拉起
  - comparison 仍残留两个 `general` 子问题，主因更像 planner/search 覆盖仍偏弱，而不是 selector 单点失效

## 2026-04-04 Evaluate 抽象与未来开源方向
- 新增明确方向：后续要把当前项目内逐步形成的 evaluate 能力抽象出来，并以未来可开源为目标持续沉淀。
- 当前认为最有开源价值的不是整个 `deep_research_agent` 主体，而是评估收敛层，包括：
  - quick checks
  - variant/full eval
  - failure taxonomy
  - insufficient-aware evaluation
  - summary / run artifact 生成
- 后续原则：在不影响当前项目推进的前提下，尽量避免把 evaluate 相关脚本和数据结构写死成一次性项目私有逻辑，而是优先保留可抽象、可迁移、可复用的边界。
## 2026-04-04 Planner ???????
- ?????? gent/planner.py ???????????? comparison / driver ??????????
- ??????????????????
  - cases_with_insufficient ???? 0 ??? 4
  - eflect_false_insufficient ? 0 ??? 4
  - planner_drift ?????
- ??????
  - ? gent/planner.py ?????????
  - ???? py_compile agent/planner.py
  - ???? ariant_eval
- ???????
  - cases_with_insufficient = 0
  - remaining tags ???? planner_drift????????????
- ???
  - ???????? planner ???
  - ?????????????? evaluate ??? remaining drift ?????

## 2026-04-04 23:19 Planner 小修：收回 definition 误伤
- 在 agent/planner.py 新增 is_definition_like_query(...)，识别『为什么重要』『核心区别』『区别是什么』『有什么区别』这类定义型问法。
- classify_query(...) 现在会先用 definition-like 判定拦住『带比较/原因措辞的定义题』，避免被误打成 comparison/driver。
- 验证：重新运行 variant_eval，cases_with_insufficient 从 1 回到 0，variant-definition-transformer-importance 恢复为 no_obvious_failure。
- 当前状态：comparison/driver 的定点补强仍保留，但 planner_drift 还剩 3，后续应继续小步修题型贴合度，不再做大重写。
