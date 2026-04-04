# Contributing

感谢你对 `deep_research_agent` 的关注。

这个项目当前仍在快速迭代，但我们希望它的迭代方式尽量保持工程化、可回归、可解释，而不是靠刷题或局部补丁堆起来。

## Before You Start

在改动代码前，请先理解这个项目的两个核心原则：

1. 先保证系统整体不回退，再追求局部更聪明。
2. 固定评估面通过，不等于真实问题分布已经稳定。

如果你是第一次参与，建议先阅读：

1. `README.md`
2. `PROJECT_STATE.md`
3. `PROJECT_LOG.md`

## Local Setup

1. 创建虚拟环境并安装依赖
2. 复制 `.env.example` 为 `.env.local`
3. 填入你自己的 API key

项目会自动读取：

- `.env.local`
- `.env`

请不要把真实密钥提交进 Git。

## Run

```powershell
.\.venv\Scripts\python.exe .\app\main.py
```

## Validation

### Quick checks

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py
```

只跑某个 suite：

```powershell
.\.venv\Scripts\python.exe .\quick_checks\run_quick_checks.py --suite rewriter
```

### Variant eval

```powershell
.\.venv\Scripts\python.exe .\evals\run_variant_eval.py
```

### Full eval

```powershell
.\.venv\Scripts\python.exe .\evals\run_eval.py
```

## Contribution Rules

### 1. Do not optimize for one fixed case
不要为了某一道固定题好看，而把整个系统带偏。

### 2. Prefer small, attributable changes
优先做小步、可归因的改动。

好的改动方式：
- 只动一个模块
- 改动目的明确
- 改完能用 quick checks / eval 回归验证

### 3. Respect workflow boundaries
不要把所有问题都重新塞回同一条 research 链。

当前默认边界：
- `RESEARCH`：证据驱动问题
- `ADVICE`：主观建议问题
- `QUICK_ANSWER`：轻问答
- `UNSUPPORTED`：当前不适合处理的输入

### 4. Keep runtime artifacts out of source changes
运行产物应继续留在：
- `outputs/`
- `.cache/`

不要把本地日志、缓存、密钥文件提交进仓库。

### 5. Explain why, not only what
如果你改了：
- `planner`
- `search`
- `selector`
- `reflector`

请在提交说明里写清楚：
- 改了什么
- 为什么这么改
- 预期改善哪类失败模式

## Good First Areas

如果你想从较安全的地方开始，比较推荐：

- `quick_checks/` 的补充与整理
- `evals/` 的摘要整理
- `README / CONTRIBUTING / docs` 改进
- `search.py` 的 domain trust 规则补充
- `failure taxonomy` 的细化

## Long-Term Direction

这个项目后面希望逐步把 evaluate 层抽象出来，并最终以开源为目标沉淀。

最可能先开放出来的不是整个 agent 本体，而是：

- quick checks
- variant/full eval runner
- failure taxonomy
- insufficient-aware evaluation
- run artifact summarization
