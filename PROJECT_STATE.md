# 当前目标
重构 Planner，让子问题拆解不再模板化

# 当前架构
Planner -> Search -> Reflect -> Rewriter -> Summarize -> Reporter

# 当前约束
- 保持 plan_subquestions(state) -> state 不变
- state.sub_questions 仍为 List[str]
- 非必要不改 main.py

# 当前下一步
1. 先完成 planner.py 重构
2. 再加 selector.py
3. 再升级 summarizer
