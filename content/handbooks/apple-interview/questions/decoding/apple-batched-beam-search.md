---
id: apple-batched-beam-search
section: decoding
order: 3
level: S
title: "完整 Batched Beam Search：EOS、parent gather、KV 重排与 length penalty"
quick: "为 B 条请求各自运行 K-beam 完整生成，先 prefill，再按 parent 同步重排前缀、mask 和 KV。支持重复 parent、独立 EOS、无效空位与最终 length penalty，并用完整前缀参考验证。"
companies:
  - apple
tags:
  - Apple
  - Decoding
  - Batch Inference
  - Batch Decoding 2026-10-28
  - 完整编程练习
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "Hugging Face: how KV caching works"
    url: "https://huggingface.co/docs/transformers/main/en/cache_explanation"
    type: primary
  - title: "PyTorch stable sort"
    url: "https://docs.pytorch.org/docs/2.14/generated/torch.sort.html"
    type: primary
  - title: "GNMT: length normalization"
    url: "https://arxiv.org/abs/1609.08144"
    type: primary
---

## 题目描述

来源：本手册原创 batch beam search 练习。给 B 个不同长度的 prompts，每个请求独立保留 K 条候选，完成整个生成循环，而不只是一次 `[B,K,V]` top-k。必须正确处理 parent backpointer、重复 parent、EOS 和 KV cache 重排。

### 输入与接口

实现 `beam_search_batch(model, input_ids, attention_mask, eos, pad, width, max_new, alpha=0.0, allowed_fn=None)`。

输入 prompts、left padding、非空行、token IDs 和 model adapter 使用 [[apple-batched-generation]] 的约定；下方包含全部给定代码，不依赖其他文件。`width=K` 是正整数，可以大于可用合法候选数；max_new 是非负整数，alpha 是有限非负数。

`allowed_fn(step, rows, prefix)` 可选，返回 active beams 对应的 bool `[A,V]`。rows 是每条 active beam 所属原请求的 row ID，可能重复；prefix `[A,step]` 是该 beam 已生成的 tokens。每条 active beam 至少有一个合法 finite logit。Mask 后重新 normalization，再算 log-prob。

### 搜索规则与 cache 合同

每个请求开始只有 beam 0 的累计 log-prob 为 0，其他为 `-inf`。每轮在该请求自己的 `K*V` 个候选中保留 K 个，不跨 B 竞争。按累计 raw log-prob 降序；同分按本轮 parent beam index，再按新 token ID 升序。这个规则不等同于整条序列的字典序。

Finished beams 通过“只允许 pad、附加分数为 0”的虚拟 carry 与 active beams 竞争，不延长真实长度，不重复添加 EOS。候选不足 K 时，空位必须明确标为 invalid，不能伪造重复候选。新生成 EOS 计入长度；prompt EOS 不终止。

Cache 为 tensor 或嵌套 tuple/list/dict/None，所有 tensor 的 batch 轴都是 axis 0。初始 prefill 只跑 B 条请求，随后复制到 B*K。每轮选择后，先按 parent gather 所有 cache tensors 与 mask，再把新 token 送进 decode。一个 parent 选中多次时，要复制其 cache，而不是复用错误的其他 beam。此约定不覆盖任意框架自定义 Cache object。

### 输出与最终排序

返回 `tokens:[B,K,max_new]`、`lengths:[B,K]`、`finished:[B,K]`、`valid:[B,K]`、`scores:[B,K]`、`rank_scores:[B,K]`。Tokens 只含新增部分，未使用位置为 pad。Invalid beams 为全 pad、长度 0、finished=False、两种 score 都为 `-inf`。

搜索期间只用 raw score；结束后对保留下来的候选使用 `score / ((5+length)/6)**alpha` 排序，length 包含 EOS。最终排序同分保持搜索结果的顺序，不额外优先 finished。没有 EOS 但达到 max_new 的候选也返回。max_new=0 时每个请求只有一个有效的空候选。Width=1、alpha=0 应等价于相同约定下的 greedy。

这些是可测试的手册约定，不保证全局最优，也不宣称与任何特定框架的 beam search 完全一致。无需实现 active compaction 或 continuous batching。

### 输入输出示例

```text
两条 prompt 分别为 [3] 和 [1,3]，left-pad 到 [[3,3],[1,3]]，mask=[[False,True],[True,True]]。
模型在 token 3 后：P(0)=0.6, P(EOS=2)=0.4；
token 0 后：P(1)=0.9, P(EOS=2)=0.1；token 1 后：P(EOS=2)=1。
width=2, max_new=3, pad=3, alpha=0。

每个请求输出 tokens=[[0,1,2],[2,3,3]], lengths=[3,1], finished=[True,True]。
scores=[log(0.54),log(0.4)]，两条都 valid=True。
第二条候选早已结束，后面的两个 3 只是 filler，不增加分数或长度。
```

## 解题思路与参考答案

假设本轮最好的两个 child 都来自旧 beam 0。只复制 token 前缀还不够：两条 child 的下一次 attention 都必须读旧 beam 0 的历史 K/V，随后才分别加入各自的新 token。

我会把每个请求的候选整理成 `[K,V]`，在它自己的 flattened K*V 上排序。选中下标除以 V 得 parent，取模得 token；再加上请求 offset，才能得到 flattened B*K cache 的索引。Finished carry 不增加长度，invalid slots 则显式保留为无效。

### 给定的 cache helpers 与测试模型

本题使用真实 causal attention 模型验证 cache；面试可将这些 helper 视为给定，只完成后面的 `beam_search_batch`。

```python
import torch


def validate_prompt(input_ids, attention_mask, max_new, eos, pad):
    if input_ids.ndim != 2 or input_ids.dtype != torch.long:
        raise ValueError("input_ids must be long [B,P]")
    if input_ids.shape[0] == 0 or input_ids.shape[1] == 0:
        raise ValueError("B and P must be positive")
    if attention_mask.shape != input_ids.shape or attention_mask.dtype != torch.bool:
        raise ValueError("attention_mask must be bool [B,P]")
    if not attention_mask[:, -1].all():
        raise ValueError("each prompt must be nonempty and LEFT padded")
    if (attention_mask[:, :-1] & ~attention_mask[:, 1:]).any():
        raise ValueError("padding must be contiguous on the left")
    if type(max_new) is not int or max_new < 0 or eos < 0 or pad < 0:
        raise ValueError("invalid generation limits or token IDs")


def reorder_cache(cache, indices):
    """Exercise protocol: nested tensors, all with batch on axis 0."""
    if cache is None:
        return None
    if isinstance(cache, torch.Tensor):
        return cache.index_select(0, indices)
    if isinstance(cache, tuple):
        return tuple(reorder_cache(x, indices) for x in cache)
    if isinstance(cache, list):
        return [reorder_cache(x, indices) for x in cache]
    if isinstance(cache, dict):
        return {key: reorder_cache(value, indices) for key, value in cache.items()}
    raise TypeError("cache must use the exercise's tensor/container protocol")


class TinyCausalLM(torch.nn.Module):
    """Small real attention model; no downloads. Test adapter, not a trained LLM."""

    def __init__(self, vocab=7, width=8, max_positions=128):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(17)
            self.token = torch.nn.Embedding(vocab, width)
            self.position = torch.nn.Embedding(max_positions, width)
            self.qkv = torch.nn.Linear(width, 3 * width, bias=False)
            self.head = torch.nn.Linear(width, vocab, bias=False)
        self.width = width
        self.calls = []
        self.eval()

    def _forward(self, ids, mask, positions, cache):
        self.calls.append(ids.shape[1])
        x = self.token(ids) + self.position(positions)
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        past = 0 if cache is None else cache[0].shape[1]
        if cache is not None:
            k = torch.cat([cache[0], k], dim=1)
            v = torch.cat([cache[1], v], dim=1)
        if mask.shape != k.shape[:2]:
            raise ValueError("mask must cover both cached and new positions")
        qpos = past + torch.arange(ids.shape[1], device=ids.device)
        kpos = torch.arange(k.shape[1], device=ids.device)
        visible = mask[:, None, :] & (kpos[None, :] <= qpos[:, None])[None, :, :]
        scores = (q @ k.transpose(-1, -2)) / self.width**0.5
        scores = scores.masked_fill(~visible, -torch.inf)
        # Left-padding queries may see no key; their output is not consumed.
        empty = ~visible.any(dim=-1)
        scores = scores.masked_fill(empty[:, :, None], 0)
        weights = scores.softmax(dim=-1).masked_fill(empty[:, :, None], 0)
        return self.head(weights @ v)[:, -1, :], (k, v)

    def prefill(self, input_ids, attention_mask, position_ids):
        return self._forward(input_ids, attention_mask, position_ids, None)

    def decode(self, token_ids, attention_mask, position_ids, cache):
        if token_ids.shape[1] != 1:
            raise ValueError("decode expects exactly one new physical slot")
        return self._forward(token_ids, attention_mask, position_ids, cache)
```
### 完整 batched beam search

```python
import math


@torch.no_grad()
def beam_search_batch(
    model,
    input_ids,
    attention_mask,
    eos,
    pad,
    width,
    max_new,
    alpha=0.0,
    allowed_fn=None,
):
    """B independent searches; finished beams compete via zero-cost PAD carry."""
    validate_prompt(input_ids, attention_mask, max_new, eos, pad)
    if type(width) is not int or width < 1 or not math.isfinite(alpha) or alpha < 0:
        raise ValueError("width >= 1 and finite alpha >= 0 required")
    batch = input_ids.shape[0]
    device = input_ids.device
    tokens = torch.full((batch, width, max_new), pad, dtype=torch.long, device=device)
    lengths = torch.zeros((batch, width), dtype=torch.long, device=device)
    finished = torch.zeros((batch, width), dtype=torch.bool, device=device)
    scores = torch.full((batch, width), -torch.inf, dtype=torch.float64, device=device)
    scores[:, 0] = 0  # Only one initial hypothesis per request.
    if max_new:
        mask = attention_mask.clone()
        positions = (mask.long().cumsum(-1) - 1).clamp(min=0)
        logits, cache = model.prefill(input_ids, mask, positions)
        vocab = logits.shape[-1]
        if not 0 <= eos < vocab or not 0 <= pad < vocab:
            raise ValueError("token IDs out of vocabulary")
        repeat = torch.arange(batch, device=device).repeat_interleave(width)
        cache = reorder_cache(cache, repeat)
        mask = mask.index_select(0, repeat)
        logits = logits.index_select(0, repeat).double()
        for step in range(max_new):
            valid = torch.isfinite(scores)
            active = valid & ~finished
            flat_active = active.reshape(-1)
            active_ids = flat_active.nonzero(as_tuple=True)[0]
            local = logits[active_ids].clone()
            if torch.isnan(local).any() or torch.isposinf(local).any():
                raise ValueError("invalid logits")
            if allowed_fn is not None:
                allowed = allowed_fn(
                    step,
                    active_ids // width,
                    tokens.reshape(batch * width, max_new)[active_ids, :step],
                )
                if allowed.shape != local.shape or allowed.dtype != torch.bool:
                    raise ValueError("allowed_fn must return bool [active_beams,V]")
                local.masked_fill_(~allowed, -torch.inf)
            if not torch.isfinite(local).any(dim=-1).all():
                raise ValueError("every active beam needs an allowed token")
            log_probs = torch.full(
                (batch * width, vocab), -torch.inf, dtype=torch.float64, device=device
            )
            log_probs[active_ids] = local.log_softmax(dim=-1)
            carried = (valid & finished).reshape(-1)
            log_probs[carried, pad] = 0
            candidates = scores[:, :, None] + log_probs.reshape(batch, width, vocab)
            # Stable tie: parent index, then token ID. Never flatten the B axis.
            flat = candidates.reshape(batch, width * vocab)
            order = flat.argsort(dim=-1, descending=True, stable=True)[:, :width]
            new_scores = flat.gather(-1, order)
            parent, selected = order // vocab, order % vocab
            parent_flat = (
                torch.arange(batch, device=device)[:, None] * width + parent
            ).reshape(-1)
            tokens = tokens.gather(1, parent[:, :, None].expand(-1, -1, max_new))
            lengths = lengths.gather(1, parent)
            old_finished = finished.gather(1, parent)
            extended = active.gather(1, parent) & torch.isfinite(new_scores)
            tokens[:, :, step] = torch.where(extended, selected, pad)
            lengths += extended.long()
            finished = old_finished | (extended & (selected == eos))
            scores = new_scores
            valid_now = torch.isfinite(scores)
            tokens.masked_fill_(~valid_now[:, :, None], pad)
            lengths.masked_fill_(~valid_now, 0)
            finished &= valid_now
            if (finished | ~torch.isfinite(scores)).all() or step + 1 == max_new:
                break
            # Gather BEFORE feeding selected tokens; duplicate parents duplicate K/V.
            cache = reorder_cache(cache, parent_flat)
            mask = mask.index_select(0, parent_flat)
            next_positions = mask.sum(dim=-1, keepdim=True).long()
            added = extended.reshape(-1, 1)
            next_positions = torch.where(added, next_positions, 0)
            mask = torch.cat([mask, added], dim=-1)
            feed = torch.where(extended, selected, pad).reshape(-1, 1)
            logits, cache = model.decode(feed, mask, next_positions, cache)
            logits = logits.double()
    rank_scores = scores / (((5.0 + lengths.double()) / 6.0) ** alpha)
    ranking = rank_scores.argsort(dim=-1, descending=True, stable=True)
    return {
        "tokens": tokens.gather(1, ranking[:, :, None].expand(-1, -1, max_new)),
        "lengths": lengths.gather(1, ranking),
        "finished": finished.gather(1, ranking),
        "valid": torch.isfinite(scores).gather(1, ranking),
        "scores": scores.gather(1, ranking),
        "rank_scores": rank_scores.gather(1, ranking),
    }
```
## 简单测试怎么写

按顺序保存 helper、实现、以下测试为 `solution.py`，运行 `python solution.py`。先手算两条候选的 0.54 与 0.4，再用逐条、完整前缀重算的 list-based reference 检查每个 beam 的 tokens、score 和 EOS。这个参考不使用 KV cache，能检出 parent gather 漏做或做错。

```python
torch.set_num_threads(1)


class TableLM:
    """Hand-calculable transitions. Cache follows the same leading-batch protocol."""

    def prefill(self, ids, attention_mask, position_ids):
        return self.next(ids[:, -1]), ids.clone()

    def decode(self, ids, attention_mask, position_ids, cache):
        return self.next(ids[:, -1]), torch.cat([cache, ids], -1)

    def next(self, last):
        probabilities = torch.tensor(
            [
                [0.0, 0.9, 0.1, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.6, 0.0, 0.4, 0.0],
            ],
            dtype=torch.float64,
        )
        return probabilities[last].log()


ids = torch.tensor([[3, 3], [1, 3]])
mask = torch.tensor([[False, True], [True, True]])
out = beam_search_batch(TableLM(), ids, mask, eos=2, pad=3, width=2, max_new=3)
assert out["tokens"].tolist() == [[[0, 1, 2], [2, 3, 3]], [[0, 1, 2], [2, 3, 3]]]
assert out["lengths"].tolist() == [[3, 1], [3, 1]]
assert out["finished"].all() and out["valid"].all()
expected = torch.tensor([[math.log(0.54), math.log(0.4)]]).expand(2, -1).double()
assert torch.allclose(out["scores"], expected, atol=1e-7, rtol=0)


def reference_beams(model, prompt, width, steps, eos, pad, alpha):
    """Independent list-based search; re-evaluates each full unpadded prefix."""
    beams = [(tuple(), 0.0, False)]
    for _ in range(steps):
        candidates = []
        for generated, score, done in beams:
            if done:
                candidates.append((generated, score, True))
                continue
            sequence = torch.tensor([prompt + list(generated)])
            positions = torch.arange(sequence.shape[1])[None, :]
            logits, _ = model.prefill(
                sequence, torch.ones_like(sequence, dtype=torch.bool), positions
            )
            logp = logits.double().log_softmax(-1)[0]
            for token in range(logp.numel()):
                if torch.isfinite(logp[token]):
                    candidates.append(
                        (generated + (token,), score + logp[token].item(), token == eos)
                    )
        # Stable ties preserve enumeration order: parent index, then token ID.
        beams = sorted(candidates, key=lambda x: -x[1])[:width]
        if all(x[2] for x in beams):
            break
    return sorted(beams, key=lambda x: -x[1] / (((5 + len(x[0])) / 6) ** alpha))


# Real attention makes the result depend on the ENTIRE history and logical positions.
ids = torch.tensor([[0, 0, 4], [2, 3, 4]])
mask = torch.tensor([[False, False, True], [True, True, True]])
original = ids.clone()
for width in (1, 3):
    for alpha in (0.0, 0.6):
        model = TinyCausalLM()
        got = beam_search_batch(
            model, ids, mask, eos=1, pad=0, width=width, max_new=5, alpha=alpha
        )
        assert model.calls[0] == 3 and all(n == 1 for n in model.calls[1:])
        for row in range(2):
            expected = reference_beams(
                TinyCausalLM(), ids[row][mask[row]].tolist(), width, 5, 1, 0, alpha
            )
            for k, (sequence, score, done) in enumerate(expected):
                length = got["lengths"][row, k].item()
                assert got["tokens"][row, k, :length].tolist() == list(sequence), (
                    row,
                    k,
                )
                assert abs(got["scores"][row, k].item() - score) < 1e-5
                assert got["finished"][row, k].item() == done
                assert (got["tokens"][row, k, length:] == 0).all()
assert torch.equal(ids, original)
# Duplicate parents must duplicate all cache tensors without sharing writable storage.
cache = {"layer": (torch.arange(12).reshape(3, 4), torch.ones(3, 4))}
repeated = reorder_cache(cache, torch.tensor([2, 2, 0]))
assert repeated["layer"][0].tolist() == [[8, 9, 10, 11], [8, 9, 10, 11], [0, 1, 2, 3]]
repeated["layer"][0][0, 0] = 99
assert repeated["layer"][0][1, 0] == 8 and cache["layer"][0][2, 0] == 8


# Fewer legal paths than width: invalid slots are explicit, never fake duplicates.
def only_eos(step, rows, prefix):
    return torch.nn.functional.one_hot(
        torch.ones(rows.numel(), dtype=torch.long), 7
    ).bool()


limited = beam_search_batch(
    TinyCausalLM(), ids, mask, eos=1, pad=0, width=4, max_new=3, allowed_fn=only_eos
)
assert limited["valid"].tolist() == [[True, False, False, False]] * 2
assert limited["lengths"].tolist() == [[1, 0, 0, 0]] * 2
assert limited["scores"][:, 0].eq(0).all()
# Zero steps leaves exactly one valid, empty initial hypothesis per request.
empty = beam_search_batch(TinyCausalLM(), ids, mask, eos=1, pad=0, width=3, max_new=0)
assert empty["tokens"].shape == (2, 3, 0)
assert empty["valid"].tolist() == [[True, False, False]] * 2


# Deterministic ties are parent-major then token-major.
class UniformLM(TableLM):
    def next(self, last):
        return torch.zeros((last.numel(), 4), dtype=torch.float64)


tied = beam_search_batch(
    UniformLM(),
    torch.tensor([[3]]),
    torch.tensor([[True]]),
    eos=2,
    pad=3,
    width=2,
    max_new=2,
)
assert tied["tokens"].tolist() == [[[0, 0], [0, 1]]]
assert not tied["finished"].any()
print("Batched cached beam search: tests passed")
```
## 复杂度与追问

每轮完整排序的时间约为 `O(B K V log(KV))`，候选工作空间为 `O(BKV)`。为了确定性 tie rule，参考实现使用 stable full sort；实际引擎可选择更高效的 top-k，并定义自己的 tie 行为。KV cache 与输入计算还会随 beam width 增长，prefill 只做一次不代表 decode 成本免费。

**一个 parent 被选两次，cache 能共享吗？** 不可变历史可以通过专门的 copy-on-write/page 管理共享；本题用 index_select 复制，简单但有成本。后续写入不能让两个 child 互相污染。

**为什么不能只重排新 token？** Cache、mask、已有输出、lengths 和 finished 都属于同一条假设；只动一部分会把不同历史混起来。

**Length penalty 为什么只在最后？** 这是本题明确选择的算法。将它用于搜索期间会改变剪枝路径，不能悄悄替换后还声称结果相同。早停条件也要结合实际目标重新推导。

**sampling 的合法集合与 beam 的合法集合一样吗？** 二者都能用 allowed_fn 提供，但 beam 需要为每条候选保留独立状态；本题通过完整 prefix 重建约束。增量 grammar state 也必须随 parent 同步重排。
