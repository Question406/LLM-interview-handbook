---
id: xai-async-dag-task-scheduler
section: xai
order: 939
level: A
title: "xAI：实现 bounded-concurrency DAG task scheduler 与失败传播"
quick: "我会先校验整个 dependency graph，避免跑了一半才发现 cycle。运行时把还没启动、正在运行、已结束三种状态分开；只有所有 prerequisites success 的 job 才能进入运行队列。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI：实现 bounded-concurrency DAG task scheduler 与失败传播"
    url: "https://aceoffer.app/interviews/xai/coding-questions"
    type: secondary
---

## 题目描述

来源：AceOffer 的 xAI 目录列出 Concurrent Job / Task Scheduler。下面明确 async jobs、dependency graph、失败传播与 cancellation 规则，给出可运行练习。

### 输入、接口与规则

实现 async `run_jobs(jobs, deps, limit=2) -> (status, results)`。jobs 是按插入顺序排列的 dict：string ID -> 无参数 async callable；deps 是相同 IDs 到 prerequisite ID set 的 dict，所有引用必须存在。limit 为正整数。每个 job 最多执行一次，只有 prerequisites 全部 success 后才能启动，任一时刻运行中的 jobs≤limit。

正常完成返回 status，值仅有 success/failed/skipped；results 只包含 success jobs 的返回值。普通 Exception 使当前 job failed，所有依赖该失败的 descendants skipped，独立 jobs 继续；不要求 deterministic completion order。启动任何 job 前须检测 cycle，cycle 或未知 prerequisite 抛 ValueError。外部 cancellation 到达时，cancel 并 await 已启动的 tasks，然后重新抛出 cancellation。不要求 retries、持久化或真实分布式调度；不修改输入。

### 输入输出示例

```text
jobs={a:返回 1,b:抛 RuntimeError,c:返回 3,d:返回 4}
deps={a:set(),b:set(),c:{a},d:{b}}，limit=2。
status={a:success,b:failed,c:success,d:skipped}，results={a:1,c:3}。
```

## 回答思路

> **Situation / Task：** Dependency readiness 与 concurrency limit 同时成立，失败不能让 descendants 永久等待。  
> **Approach / Why：** 先 topological validation，再维护 pending/running/status；完成事件触发下一轮 readiness 检查。  
> **Result / Check：** 记录实际 active count，并测试失败后独立任务继续、cycle 前零启动、外部 cancellation cleanup。

## 解题思路与参考答案

我会先校验整个 dependency graph，避免跑了一半才发现 cycle。运行时把还没启动、正在运行、已结束三种状态分开；只有所有 prerequisites success 的 job 才能进入运行队列。

失败后，依赖它的 pending jobs 会被标记 skipped，这个结果会继续传播给 descendants。等待 FIRST_COMPLETED 后释放 slots，再启动新的 ready jobs。外部 cancellation 需要在 finally 路径里 cancel 并 await 所有正在运行的 tasks，防止 caller 已经退出而后台任务还在继续。

### 完整参考实现

```python
import asyncio
from collections import deque


async def run_jobs(jobs, deps, limit=2):
    if limit <= 0 or set(jobs) != set(deps):
        raise ValueError('invalid keys/limit')
    if any(not set(required) <= jobs.keys() for required in deps.values()):
        raise ValueError('unknown dependency')
    children = {key: [] for key in jobs}
    degree = {key: len(deps[key]) for key in jobs}
    for key in jobs:
        for parent in deps[key]:
            children[parent].append(key)
    ready = deque(key for key in jobs if not degree[key])
    visited = 0
    while ready:
        key = ready.popleft()
        visited += 1
        for child in children[key]:
            degree[child] -= 1
            if degree[child] == 0:
                ready.append(child)
    if visited != len(jobs):
        raise ValueError('cycle')
    pending = dict.fromkeys(jobs)
    running = {}
    status = {}
    results = {}
    try:
        while pending or running:
            changed = True
            while changed:
                changed = False
                for key in list(pending):
                    if any(
                        status.get(parent) in ('failed', 'skipped')
                        for parent in deps[key]
                    ):
                        status[key] = 'skipped'
                        del pending[key]
                        changed = True
            for key in list(pending):
                if len(running) >= limit:
                    break
                if all(status.get(parent) == 'success' for parent in deps[key]):
                    running[asyncio.create_task(jobs[key]())] = key
                    del pending[key]
            if not running:
                if pending:
                    raise RuntimeError('scheduler stalled')
                break
            done, _ = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                key = running[task]
                try:
                    results[key] = task.result()
                    status[key] = 'success'
                except Exception:
                    status[key] = 'failed'
                del running[task]
        return status, results
    finally:
        for task in running:
            task.cancel()
        if running:
            await asyncio.gather(*running, return_exceptions=True)
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
async def test_scheduler():
    active = 0
    peak = 0
    started = []
    finished = set()
    deps = {'a': set(), 'b': set(), 'c': {'a'}, 'd': {'b'}, 'e': {'d'}}

    def make(key):
        async def job():
            nonlocal active, peak
            assert all(p in finished for p in deps[key])
            started.append(key)
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(0)
                if key == 'b':
                    raise RuntimeError('test failure')
                finished.add(key)
                return key.upper()
            finally:
                active -= 1

        return job

    jobs = {key: make(key) for key in deps}
    status, results = await run_jobs(jobs, deps, 2)
    assert status == {
        'a': 'success',
        'b': 'failed',
        'c': 'success',
        'd': 'skipped',
        'e': 'skipped',
    }
    assert results == {'a': 'A', 'c': 'C'} and peak <= 2 and active == 0
    before = list(started)
    try:
        await run_jobs({'a': make('a'), 'b': make('b')}, {'a': {'b'}, 'b': {'a'}})
    except ValueError:
        pass
    else:
        raise AssertionError('cycle accepted')
    assert started == before
    entered = asyncio.Event()
    cleaned = asyncio.Event()
    block = asyncio.Event()

    async def waiting():
        entered.set()
        try:
            await block.wait()
        finally:
            cleaned.set()

    runner = asyncio.create_task(run_jobs({'x': waiting}, {'x': set()}))
    await entered.wait()
    runner.cancel()
    try:
        await runner
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError('cancellation swallowed')
    assert cleaned.is_set()
    assert await run_jobs({}, {}) == ({}, {})


asyncio.run(test_scheduler())
print('async DAG scheduler tests passed')
```

## 复杂度与追问

这个清晰的 reference 每轮扫描 pending，worst-case scheduler bookkeeping 为 `O(V*(V+E))`，外加 jobs 的实际运行成本；空间 `O(V+E)`。优化版可维护 remaining prerequisite counts 与 ready queue，把 bookkeeping 降为 `O(V+E)`。不要把 bounded concurrency 自动等同于 CPU parallelism。
