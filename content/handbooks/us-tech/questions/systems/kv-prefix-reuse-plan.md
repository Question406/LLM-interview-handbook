---
id: kv-prefix-reuse-plan
section: systems
order: 37
level: A
title: KV Prefix ⑦：页对齐命中、完整命中与 Chunked Prefill 计划
quick: >-
  先把命中长度向下对齐到完整页，再安排后缀的 chunk。只有 KV、又需要末 token logits 时，即使完全命中也得重放末
  token；按页共享时可能要重放整个尾页。
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Transformer per-layer attention states
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
  - title: vLLM prefix cache design
    url: 'https://docs.vllm.ai/en/latest/design/prefix_caching/'
    type: primary
---

## 题目描述

给定 prompt 长度、已经命中的前缀 token 数、页大小、后续计算预算以及是否需要末位置 logits，规划本次能复用多少 token，并把必须重新计算的后缀分成连续的绝对位置区间。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

实现 `plan_reuse(prompt_length,matched_tokens,page_size=1,chunk_budget=4,need_last_logits=True)`，返回可复用 token 数和后缀的绝对区间列表。参数必须是整数，`prompt_length`≥1，0≤matched≤`prompt_length`，`page_size` 与 `chunk_budget`≥1。复用只取完整页，后缀 chunk 既不能重叠，也不能留缺口，每块不超过预算。

`need_last_logits`=True 表示索引只持有 KV，而本次需要 prompt 末 token 的 logits，因此至少要重算最后一个 token。只有另存末 logits / hidden state，或本次无需 sampling 时，才设为 False。

返回值为 `(reused, chunks)`，`chunks` 是由 `(start,end)` 组成的 tuple。`reused` 为满足页对齐且不超过 `matched_tokens` 的最大值；需要末 logits 时还须 `reused < prompt_length`。每块从当前后缀起点延伸 `min(chunk_budget, 剩余长度)` 个 token。
### 示例

```text
plan_reuse(8,8,4,3,True) -> (4, ((4,7),(7,8)))
plan_reuse(8,8,1,3,True) -> (7, ((7,8),))
plan_reuse(8,8,4,3,False) -> (8, ())
```

## 解题思路与参考答案

我会先按完整页确定可复用前缀，再把待计算后缀切成预算内的 chunk。若只缓存 KV、这次又需要末 token 的 logits，完全命中也要回退，至少重算最后一个 token。

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，代码为手册独立实现。接口、简化条件和测试由手册定义。依赖 Python 3与 NumPy，使用 CPU 测试数值及状态语义，不报告 GPU throughput。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `plan_reuse(prompt_length,matched_tokens,page_size,chunk_budget,need_last_logits=True)`，返回可复用 token 数和后缀的绝对区间列表。参数必须是整数，`prompt_length`≥1，0≤matched≤`prompt_length`，`page_size` 与 `chunk_budget`≥1。复用只取完整页，后缀 chunk 既不能重叠，也不能留缺口，每块不超过预算。

`need_last_logits`=True 表示索引只持有 KV，而本次需要 prompt 末 token 的 logits，因此至少要重算最后一个 token。只有另存末 logits / hidden state，或本次无需 sampling 时，才设为 False。

### 输入输出示例

prompt 长度8、命中8、page size4、chunk budget3：复用4，后缀分成 `[4,7)`、`[7,8)`。token 粒度 page size1时只需复用7并重算最后1token。

### 解题思路与正确性

例如 prompt 长度 8，命中 8，page size 为 4，只缓存 KV 时需要回退到位置 4，再重算尾页。KV 是 attention 的历史中间状态，不能直接给出末 token 的最终 hidden state 或 vocabulary logits。先确定尾部重算需求，再按整 page boundaries 回退，chunk 使用绝对 start/end，forward 的 RoPE 位置随 cache 实际长度推进。

### 完整参考实现（Python 3）

```python
def plan_reuse(
    prompt_length, matched_tokens, page_size=1, chunk_budget=4, need_last_logits=True
):
    values = (prompt_length, matched_tokens, page_size, chunk_budget)
    if any(type(v) is not int for v in values):
        raise ValueError('integer parameters required')
    if (
        prompt_length < 1
        or not 0 <= matched_tokens <= prompt_length
        or min(page_size, chunk_budget) < 1
    ):
        raise ValueError('length or budget')
    reusable = matched_tokens // page_size * page_size
    if need_last_logits and reusable == prompt_length:
        # KV alone is not the final hidden state/logits. Replay at least the last token.
        reusable = (prompt_length - 1) // page_size * page_size
    chunks = []
    for start in range(reusable, prompt_length, chunk_budget):
        chunks.append((start, min(prompt_length, start + chunk_budget)))
    return reusable, tuple(chunks)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert plan_reuse(8, 8, 4, 3) == (4, ((4, 7), (7, 8)))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

把实现与以下测试放进同一文件执行；测试覆盖正确性，不是生产环境的性能基准。

```python
def test():
    assert plan_reuse(8, 8, 4, 3) == (4, ((4, 7), (7, 8)))
    assert plan_reuse(8, 8, 4, 3, False) == (8, ())
    assert plan_reuse(9, 7, 4, 2) == (4, ((4, 6), (6, 8), (8, 9)))
    assert plan_reuse(1, 1) == (0, ((0, 1),))
    for n in range(1, 31):
        for hit in range(n + 1):
            for page in (1, 2, 4, 8):
                reused, chunks = plan_reuse(n, hit, page, 3)
                assert reused <= hit and reused % page == 0 and reused < n
                covered = [i for start, end in chunks for i in range(start, end)]
                assert covered == list(range(reused, n))
                assert all(0 < end - start <= 3 for start, end in chunks)
    # Execute the chunk plan through the real model in an integration test in engine.py.


if __name__ == '__main__':
    test()
```

### 复杂度与追问

确定 reusable prefix length 需要 O(1)，输出计划需要 O(后缀长度/`chunk_budget`)。本题只生成计划，物理页和模型都不改；第⑧题会把同一 planner 接进多层 forward 验证。

如果额外缓存最终 hidden / logits，可以避免重算末 token，但要另外管理存储与失效条件。这里的重放来自 KV-only 契约，其他 prefix 缓存方案可能有不同选择。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[kv-prefix-transformer]]：第①题，说明只缓存 KV 时完整命中为什么拿不到末 token 的 logits。
- [[kv-prefix-engine]]：第⑧题，把这里的计划接进真实的多层 forward 验证。
