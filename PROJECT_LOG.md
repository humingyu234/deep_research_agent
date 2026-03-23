# 项目日志

## 1. 文档目的
- 记录项目关键改动、设计决策、验证情况与下一步建议
- 为后续开发、复盘和交接提供统一上下文
- 避免每次进入项目时都从头重新梳理架构和历史

## 2. 项目概况
- 项目名称：`deep_research_agent`
- 项目定位：一个以“拆题、检索、筛选、总结、汇报”为主链路的 research agent 原型
- 当前阶段：原型增强阶段
- 当前重点：提升主链路输出质量，而不是优先做大规模工程化包装

## 3. 当前目标
- 让系统从“能跑通”升级到“结果更贴题、总结更稳、结构更清楚”
- 当前重点链路：
  - `Planner -> Search -> Selector -> Reflect -> Summarizer -> Reporter`

## 4. 当前架构
- 入口文件：`app/main.py`
- 状态容器：`agent/state.py`
- 规划模块：`agent/planner.py`
- 检索模块：`agent/search.py`
- 筛选模块：`agent/selector.py`
- 反思模块：`agent/reflector.py`
- 改写模块：`agent/rewriter.py`
- 总结模块：`agent/summarizer.py`
- 报告模块：`agent/reporter.py`

## 5. 核心改动记录

### 5.1 仓库分析与基线梳理
- 阅读仓库结构和主流程，确认项目整体是一个紧凑型 research agent 原型
- 识别原始链路为：
  - `Planner -> Search -> Reflect -> Rewriter -> Summarize -> Reporter`
- 初步发现的问题：
  - `planner.py` 对所有 query 使用固定拆题模板
  - `summarizer.py` 直接消费全部搜索结果，缺少有效压缩
  - `reporter.py` 偏向旧模板式总结
  - `reflector.py` 在没有结果筛选层之前就直接判断，容易被噪音干扰
  - 终端存在中文编码显示噪音

### 5.2 Planner 能力升级
- 重构了 `agent/planner.py`
- 保持对外接口不变：
  - `plan_subquestions(state: ResearchState) -> ResearchState`
  - `state.sub_questions`
  - `state.sub_questions: List[str]`
- 在内部新增：
  - `classify_query(query: str) -> str`
  - `build_subquestions(query: str, query_type: str) -> List[str]`
- 支持的 query 类型：
  - `definition`
  - `trend`
  - `preference`
  - `howto`
  - `general`
- 收益：
  - 拆题不再一刀切
  - 子问题更贴近用户真实意图

### 5.3 增加项目辅助文档
- 新增 `PROJECT_STATE.md`
  - 记录当前目标、架构、约束和下一步计划
- 新增 `PLANNER_REVIEW_PROMPT.md`
  - 用于辅助复盘和讲解 planner 模块

### 5.4 第一版 Selector 接入
- 新增 `agent/selector.py`
- 将链路从：
  - `Search -> Reflect -> Summarize`
- 升级为：
  - `Search -> Selector -> Reflect -> Summarize`
- 初版 selector 能力：
  - 去重
  - 低质量来源过滤
  - 简单相关性打分
  - Top-K 选择

### 5.5 Summarizer 第一轮升级
- 重写了 `agent/summarizer.py`
- 从“snippet 拼盘”升级为：
  - 一句判断
  - 若干支撑点
- 解决的核心问题：
  - 有信息，但不会压缩

### 5.6 Reporter 第一轮升级
- 重写了 `agent/reporter.py`
- 从“模板式结尾”升级为：
  - 根据 summaries 合成整体结论
  - 提取每个 summary 的核心判断
  - 自动补充风险/限制语气

### 5.7 Reflector 第一轮升级
- 重写了 `agent/reflector.py`
- 从直接判断原始结果，改为判断 selector 筛过的结果
- 当前判断维度：
  - 是否有可用结果
  - 结果数是否足够
  - 摘要密度是否够
  - 与子问题是否具备基本相关性

### 5.8 主流程接线重构
- 重写了 `app/main.py`
- 当前主流程：
  1. planner 拆子问题
  2. search 搜索
  3. selector 筛结果
  4. reflector 判断是否足够
  5. rewriter 在不足时改写 query
  6. summarizer 对精选结果做总结
  7. reporter 合成总报告

### 5.9 Selector 第二轮收紧
- 根据最新需求，进一步增强了 `agent/selector.py`
- 本轮重点：
  - 去掉明显营销稿
  - 去掉重复转述
  - 更偏向保留“报告 / 调研 / 框架 / 研究”气质的内容
  - 默认只喂给 Summarizer Top-3 结果
- 新增能力：
  - `is_marketing_like()`：识别软文/营销稿
  - `result_similarity()`：压掉高度相似的重复转述
  - 强化研究型内容的加分逻辑
- 本轮收益：
  - Selector 更像“资料编辑台”
  - Summarizer 得到的输入更干净

### 5.10 Summarizer 第二轮升级
- 进一步增强了 `agent/summarizer.py`
- 输出结构明确为：
  - 一句话结论
  - 2~3 条支撑点
  - 必要时补一句不确定性
- 新增能力：
  - `build_support_points()`：先抽证据点
  - `build_uncertainty_sentence()`：自动补充不确定性
  - 根据子问题类型生成更像“结论句”的 lead sentence
- 本轮收益：
  - 总结更像研究小结
  - 不再只是“网页摘要连贴”

### 5.11 Reflector 第二轮收紧
- 进一步增强了 `agent/reflector.py`
- 本轮新增检查：
  - 来源多样性是否过低
  - 是否缺少报告/研究/框架型内容
  - 如果子问题问的是驱动因素，是否真的出现因果词
  - 如果子问题问的是风险/限制，是否真的出现风险信号
  - 是否只是泛泛趋势语句重复
- 本轮收益：
  - Reflect 不再那么容易“一轮 enough”
  - 对研究型问题的把关更严格

### 5.12 Reporter 第二轮收束
- 进一步增强了 `agent/reporter.py`
- 当前目标：
  - 不只是拼接子 summary
  - 而是生成一个更高层的总体判断
- 本轮收益：
  - 总结更像“总述”
  - 更接近真正研究报告里的“整体结论”

## 6. 关键设计决策

### 6.1 保持外部接口稳定
- 优先保证 `planner` 外部接口不变，避免级联修改
- 当前系统仍然围绕 `ResearchState` 组织数据流
- 搜索结果仍保留 `list[dict]`，避免这一阶段引入大范围类型迁移

### 6.2 先提纯输入，再增强推理
- 优先补 Selector，而不是先把 Reflect 做复杂
- 原因：
  - 如果输入结果太杂，后面的反思和总结都会被拖累

### 6.3 让 Summarizer 只吃“干净菜”
- 当前 Summarizer 仍然是规则压缩型，不是高阶语义总结器
- 因此前置 Selector 必须更严格，避免“脏数据直接进总结”

### 6.4 优先做高收益规则升级
- planner 仍然使用规则做 query 分类
- selector 仍然是启发式排序与过滤
- reporter 默认仍是规则合成，LLM 路径只做预留

### 6.5 优先提升可读性和可讲解性
- 当前代码和日志都朝“便于理解、便于教学、便于迭代”的方向整理
- 这样更适合当前项目阶段，也更适合继续逐步升级

## 7. 本轮涉及文件
- `agent/planner.py`
- `agent/selector.py`
- `agent/summarizer.py`
- `agent/reporter.py`
- `agent/reflector.py`
- `app/main.py`
- `PROJECT_STATE.md`
- `PLANNER_REVIEW_PROMPT.md`
- `PROJECT_LOG.md`

## 8. 已完成验证
- 已人工确认仓库结构与模块职责
- 已完成导入级验证：
  - `app.main` 可成功导入
- 已完成轻量功能验证：
  - `plan_subquestions()`
  - `select_top_results()`
  - `reflect()`
  - `summarize()`
  - `generate_report()`

## 9. 当前已知问题
- 终端环境仍然可能出现中文显示乱码
- `agent/__int__.py` 命名不规范，后续可清理
- `search.py` 与 `real_search.py` 存在职责重叠
- 搜索结果仍为松散 `dict` 结构，后续维护风险偏高
- selector 当前仍然是规则型排序，不是真正的检索排序模型
- summarizer 当前仍然是规则型提炼器，抽象能力有限

## 10. 建议的下一步

### 10.1 短期
- 统一仓库文件编码与终端输出编码
- 决定是否保留 `search.py` 与 `real_search.py` 双入口
- 将结果结构逐步与 `models/schema.py` 对齐

### 10.2 中期
- 给 selector 增加“为什么这条入选”的调试解释
- 让 summarizer 学会更抽象地改写支撑点，而不只是压缩截断
- 让 reporter 支持处理互相矛盾的 summaries
- 让 reflector 支持按 query 类型做更细的判定策略

### 10.3 长期
- 增加测试：
  - planner 分类测试
  - selector 排序测试
  - summarizer 输出结构测试
  - reporter 合成逻辑测试
- 增加配置管理：
  - top-k
  - 来源过滤规则
  - search mode
- 引入 snippet 之外的正文读取能力

## 11. 当前工作假设
- 当前优先级是架构质量和迭代速度，而不是生产级打磨
- 当前更适合做“小范围高收益”的改动
- 当前输出质量的瓶颈主要仍在检索质量和结果筛选层

## 12. 维护建议
- 每次关键架构改动后更新本日志
- 每次新增模块时补一条“职责说明 + 接入位置”
- 如果后续开始多人协作，这份文档可直接作为交接材料
