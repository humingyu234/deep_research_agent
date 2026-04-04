# Quick Checks

`quick_checks/` 用来放“轻验证”工具。

它和 `evals/` 的区别是：
- `quick_checks`
  - 快
  - 只验证某一层有没有明显写歪
  - 适合改完局部模块后先跑
- `evals`
  - 慢
  - 跑整条真实链路
  - 适合关键节点做完整回归

## 当前已提供

### 全量 quick checks

运行：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py
```

这会依次跑：
- `planner` quick checks
- `clarifier` quick checks
- `clarifier_integration` quick checks

### 只跑某一套

只跑 `planner`：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite planner
```

只跑 `clarifier`：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite clarifier
```

只跑 `clarifier_integration`：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite clarifier_integration
```

### 只跑单个 case

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite clarifier --case clarifier-preference-english-app
```

## 当前作用

### planner quick checks

检查：
- `classify_query()` 是否把题型分对
- `build_subquestions()` 是否覆盖该题型应有的关键方向

### clarifier quick checks

检查：
- `should_clarify()` 是否在该澄清时触发
- 澄清原因分类是否正确
- 澄清问题是否覆盖预期方向
- `build_clarified_query()` 是否把用户补充约束正确拼进新 query

### clarifier integration quick checks

检查：
- Clarifier 分类是否正确
- 澄清后 query 交给 Planner 时，题型是否仍然合理
- 澄清后的补充约束是否真的流进了子问题
- Planner 子问题模板是否仍然贴题

## 输出怎么看

每个 case 都会显示：
- 预期值
- 实际值
- `PASS / FAIL`
- 为什么通过 / 为什么失败

最后还会输出每套 quick check 的总览，告诉你：
- 哪类失败最多
- 下一步应该先修哪一层

## 推荐工作流

建议以后按这个节奏：

1. 改局部模块
2. 先跑 `quick_checks`
3. 通过后再跑 `mini_eval`
4. 关键节点再跑 `full eval`
