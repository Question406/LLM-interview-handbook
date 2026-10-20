---
id: p3a-xai-mock-llm-dynamic-batching
section: xai
order: 614
level: S
title: "xAI：Mock LLM 推理循环：动态填槽和结果归属"
quick: "每个槽位记住 request id、已生成 token 和停止条件；每轮先按旧的槽位归属处理完 model 输出并释放完成的请求，再从队列补位，这样 token 不会记到新请求名下。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · mock-llm-dynamic-batching"
    url: https://www.1point3acres.com/interview/problems/company/xai/mock-llm-dynamic-batching
    type: secondary
---

## 题目

给一个 mock 的 LLM：`model(batch)` 接收一批 token 序列，为每条序列返回一个 next token。写一个推理循环，用固定数量的槽位做动态批处理：某个请求生成结束（遇到 EOS 或达到长度上限）后，它的槽位马上让给队列里等待的请求，并且每个 token 都要记到正确的请求名下。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

每个槽位要记住三样东西：它属于哪个 request id、这个请求已经生成了哪些 token、它的停止条件（`max_new` 和 EOS）。

每一轮的顺序很重要：先把本轮 model 的输出按旧的槽位归属全部处理完，释放已完成的槽位，再从队列里补新请求。如果先补位再处理输出，或者边处理边就地复用槽位，下标一错，旧请求的 token 就会写到新请求名下。

动手前要把这些边界讲清楚：

- `max_new` 为 0 的请求：直接返回空列表，不送进 model；
- EOS token 算不算输出：这份练习不算；
- 队列为空但还有活跃请求、所有请求都结束时的退出条件；
- 如果面试官追加「取消请求」，被取消的请求要在下一轮补位之前移出槽位，已生成的部分是否返回也要约定。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `generate(requests, model, slots, eos) -> dict`：`requests` 是 `(request_id, prompt, max_new)` 列表，`request_id` 唯一，`prompt` 是 token 列表；返回每个 `request_id` 到它新生成 token 列表的映射，所有请求都在结果里。
- `model(batch)`：`batch` 是若干条完整序列（prompt 加上已生成的 token），返回同样长度的 next token 列表；长度不对抛 `ValueError`。
- 请求遇到 `eos`（不计入输出）或生成满 `max_new` 个 token 就完成，下一轮从队列按顺序补位。
- `slots >= 1`，`max_new >= 0`，id 不能重复，违反时抛 `ValueError`。请求数不超过 1000，总生成 token 数不超过 $10^5$。

### 输入输出示例

```text
model 总是返回 9，slots = 1
generate([("a", [], 2), ("b", [], 1)], model, 1, eos=-1)   -> {"a": [9, 9], "b": [9]}
```

只有一个槽位，所以 a 连续占两轮，生成满 2 个后 b 才进来。

### 解题思路与正确性

`active` 列表和本轮 `model` 的输出按下标一一对应，用 `zip` 逐个处理，处理完才生成新的 `active` 并在下一轮开头补位，所以 token 不会归错请求。

终止性：每一轮里，每个活跃请求要么遇到 EOS 完成，要么多生成一个 token；`max_new` 是有限的，所以活跃请求总会完成，等待队列也会被逐个取空。

这份实现每轮都把完整序列重新拼出来交给 model，是为了让 mock 接口简单，不代表真实推理引擎的做法。

### 完整参考实现（Python 3）

```python
from collections import deque


def _validate(requests, slots):
    if slots < 1:
        raise ValueError("slots must be at least 1")
    ids = [request_id for request_id, _, _ in requests]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate request id")
    if any(max_new < 0 for _, _, max_new in requests):
        raise ValueError("max_new must be non-negative")


def generate(requests, model, slots, eos):
    """动态批处理解码：每轮把所有活跃请求的完整序列送进 model，各取一个 next token。

    requests 是 (request_id, prompt_tokens, max_new) 列表；返回 request_id -> 新生成的 token 列表。
    请求遇到 eos（不计入输出）或生成满 max_new 个 token 后立即腾出槽位，下一轮从队列补上。
    """
    _validate(requests, slots)
    waiting = deque((request_id, list(prompt), max_new) for request_id, prompt, max_new in requests)
    generated = {request_id: [] for request_id, _, _ in requests}
    active = []  # 每项是 (request_id, prompt, max_new)，和本轮 model 输出按下标一一对应

    while waiting or active:
        # 先用等待中的请求填满空槽；max_new 为 0 的请求直接完成，不占槽
        while waiting and len(active) < slots:
            request = waiting.popleft()
            if request[2] > 0:
                active.append(request)
        if not active:
            continue

        batch = [prompt + generated[request_id] for request_id, prompt, _ in active]
        next_tokens = model(batch)
        if len(next_tokens) != len(active):
            raise ValueError(f"model returned {len(next_tokens)} tokens for batch of {len(active)}")

        # 本轮结果全部按旧的 active 归属处理完，才进入下一轮补位
        still_running = []
        for (request_id, prompt, max_new), token in zip(active, next_tokens):
            if token == eos:
                continue
            generated[request_id].append(token)
            if len(generated[request_id]) < max_new:
                still_running.append((request_id, prompt, max_new))
        active = still_running

    return generated
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

def always_nine(batch):
    return [9] * len(batch)

# 单槽：a 生成满 2 个后 b 才进来
result = generate([("a", [], 2), ("b", [], 1)], always_nine, 1, -1)
assert result == {"a": [9, 9], "b": [9]}

# 以 1 开头的序列立刻遇到 EOS；max_new=0 的 c 不进入任何批次
calls = []

def eos_for_prompt_one(batch):
    calls.append(batch)
    return [-1 if sequence[0] == 1 else 7 for sequence in batch]

result = generate([("a", [1], 5), ("b", [2], 2), ("c", [3], 0)], eos_for_prompt_one, 2, -1)
assert result == {"a": [], "b": [7, 7], "c": []}
assert len(calls) == 2
assert calls[1] == [[2, 7]]  # 第二轮只剩 b，且带着它上一轮的输出

# 非法输入
expect_value_error(generate, [("a", [], 1)], always_nine, 0, -1)
expect_value_error(generate, [("a", [], 1), ("a", [], 1)], always_nine, 1, -1)
expect_value_error(generate, [("a", [], -1)], always_nine, 1, -1)
expect_value_error(generate, [("a", [], 1)], lambda batch: [], 1, -1)
```

### 复杂度与追问

设请求数为 R、所有请求的生成 token 总数为 G、单个请求最终序列长度为 L。每次 model 调用至少让一个请求多生成一个 token 或遇到 EOS 结束，所以调用次数不超过 G + R；槽位都占满时，一次调用能同时推进 `slots` 个请求。每轮重新拼接完整序列，单个请求的拷贝开销是 O(L²)，这份参考实现只追求正确性。

真实推理引擎不会每步重传整段历史：它为每个请求维护 KV cache，每步只输入上一个 token，再用一张稳定的「槽位 → request」映射表把输出对回请求。槽位释放时要同时回收它的 KV cache 块，新请求进来要先做一次 prefill。
