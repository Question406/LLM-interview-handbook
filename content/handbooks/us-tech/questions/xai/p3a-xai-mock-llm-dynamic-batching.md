---
id: p3a-xai-mock-llm-dynamic-batching
section: xai
order: 614
level: S
title: "xAI：Mock LLM 推理循环：动态填槽和结果归属"
quick: "我会为每个槽位保存 request id、已生成 token 和 EOS、max_new 停止条件，一轮输出全部按旧归属处理后，再释放和补位。这样旧请求的 token 不会写给新请求；max_new 为 0 直接完成，EOS 是否计入输出也要事先约定。"
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

## 题目描述

用一个同步的 mock 模型实现动态批量解码。多个请求按顺序等待，最多 slots 条同时生成；请求完成后立即释放槽位供后续请求使用，返回每条请求独立的新 token 列表。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `generate(requests, model, slots, eos) -> dict`：`requests` 是 `(request_id, prompt, max_new)` 列表，`request_id` 唯一，`prompt` 是 token 列表；返回每个 `request_id` 到它新生成 token 列表的映射，所有请求都在结果里。
- `model(batch)`：`batch` 是若干条完整序列（prompt 加上已生成的 token），返回同样长度的 next token 列表；返回数量与 batch 中的请求数相同。
- 请求遇到 `eos`（不计入输出）或生成满 `max_new` 个 token 就完成，下一轮从队列按顺序补位。
- `slots >= 1`，`max_new >= 0`，id 不能重复，请求数不超过 1000，总生成 token 数不超过 $10^5$。

### 示例

```text
model 总是返回 9，slots = 1
generate([("a", [], 2), ("b", [], 1)], model, 1, eos=-1)   -> {"a": [9, 9], "b": [9]}
```

## 解题思路与参考答案

我会先处理完一轮 model 输出，再把空槽交给新请求，槽位与 request 的对应关系在这一轮里保持不变。比如 a 生成结束时，它刚返回的 token 仍属于 a，不能先让 b 占槽再按槽号记账。

## 题目

给一个 mock 的 LLM：`model(batch)` 接收一批 token 序列，为每条序列返回一个 next token。写一个推理循环，用固定数量的槽位做动态批处理：某个请求生成结束（遇到 EOS 或达到长度上限）后，它的槽位马上让给队列里等待的请求，并且每个 token 都要记到正确的请求名下。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

每个槽位保存 request id、该请求已生成的 token，以及 `max_new` 和 EOS 两个停止条件。输出处理、完成判断和补位都围绕同一份映射进行。

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

循环能结束，是因为每一轮每个活跃请求要么遇到 EOS，要么多生成一个 token。`max_new` 有上限，所以所有活跃请求最终都会释放槽位，等待队列也会逐个取空。

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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert result == {"a": [9, 9], "b": [9]}` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
