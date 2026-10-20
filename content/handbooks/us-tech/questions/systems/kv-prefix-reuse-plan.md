---
id: kv-prefix-reuse-plan
section: systems
order: 37
level: A
title: "KV Prefix ⑦：页对齐命中、完整命中与 Chunked Prefill 计划"
quick: "逻辑命中长度还要按完整页取整；如果只缓存 KV、没有末 token logits，完整命中时也要重放末 token，页级复用可能需要重放整尾页。"
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "Transformer per-layer attention states"
    url: https://arxiv.org/abs/1706.03762
    type: primary
  - title: "vLLM prefix cache design"
    url: https://docs.vllm.ai/en/latest/design/prefix_caching/
    type: primary
---

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，不是某家公司的已确认原题，也不是SGLang/vLLM源码逐字翻译。接口、简化条件和测试由手册定义。依赖Python 3与NumPy，使用CPU测试数值及状态语义，不报告GPU吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `plan_reuse(prompt_length,matched_tokens,page_size,chunk_budget,need_last_logits=True)`，返回可复用token数及绝对后缀区间列表。参数全整数，`prompt_length`≥1，0≤matched≤`prompt_length`，`page_size`和`chunk_budget`≥1。复用必须是完整页；后缀chunk无重叠无缺口，每块大小≤预算。`need_last_logits`=True表示索引只持有KV且这次需要输出prompt末token的logits，因此必须至少重算最后一个token；False仅用于已另有末logits/hidden state或无需采样的场景。

### 输入输出示例

prompt长度8、命中8、page size4、chunk budget3：复用4，后缀分成 `[4,7)`、`[7,8)`。token粒度page size1时只需复用7并重算最后1token。

### 解题思路与正确性

KV是attention的历史中间状态，并不是末token最终hidden state或词表logits。先确定需要重算的尾token，再按可共享整页边界回退；chunk使用绝对start/end，后续forward的RoPE位置跟cache实际长度走。

### 完整参考实现（Python 3）

```python
def plan_reuse(prompt_length, matched_tokens, page_size=1, chunk_budget=4,
               need_last_logits=True):
    values = (prompt_length, matched_tokens, page_size, chunk_budget)
    if any(type(v) is not int for v in values):
        raise ValueError('integer parameters required')
    if prompt_length < 1 or not 0 <= matched_tokens <= prompt_length or min(page_size, chunk_budget) < 1:
        raise ValueError('length or budget')
    reusable = matched_tokens//page_size*page_size
    if need_last_logits and reusable == prompt_length:
        # KV alone is not the final hidden state/logits. Replay at least the last token.
        reusable = (prompt_length-1)//page_size*page_size
    chunks = []
    for start in range(reusable, prompt_length, chunk_budget):
        chunks.append((start, min(prompt_length, start+chunk_budget)))
    return reusable, tuple(chunks)
```

### 可执行测试

把实现与以下测试放进同一文件执行；测试覆盖正确性，不是生产环境的性能基准。

```python
def test():
    assert plan_reuse(8, 8, 4, 3) == (4, ((4, 7), (7, 8)))
    assert plan_reuse(8, 8, 4, 3, False) == (8, ())
    assert plan_reuse(9, 7, 4, 2) == (4, ((4, 6), (6, 8), (8, 9)))
    assert plan_reuse(1, 1) == (0, ((0, 1),))
    for n in range(1, 31):
        for hit in range(n+1):
            for page in (1, 2, 4, 8):
                reused, chunks = plan_reuse(n, hit, page, 3)
                assert reused <= hit and reused % page == 0 and reused < n
                covered = [i for start, end in chunks for i in range(start, end)]
                assert covered == list(range(reused, n))
                assert all(0 < end-start <= 3 for start, end in chunks)
    # Execute the chunk plan through the real model in an integration test in engine.py.

if __name__ == '__main__':
    test()
```

### 复杂度与追问

计算复用边界O(1)，输出计划O(后缀长度/`chunk_budget`)。本题只做计划，不触碰物理页和模型；第⑧题把同一planner接入真实多层forward验证。

有额外缓存最终hidden/logits时可避免重算最后token，但需说明额外存储与失效条件。不能因为某个框架会重放一token，就声称所有prefix缓存方案都必然如此；这是本练习KV-only契约的选择。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[kv-prefix-transformer]]：第①题，说明只缓存 KV 时完整命中为什么拿不到末 token 的 logits。
- [[kv-prefix-engine]]：第⑧题，把这里的计划接进真实的多层 forward 验证。
