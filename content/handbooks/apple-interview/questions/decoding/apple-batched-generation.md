---
id: apple-batched-generation
section: decoding
order: 2
level: S
title: "完整 Batch generation：greedy / sampling、独立 EOS 与 KV cache"
quick: "对不同长度的 left-padded prompts 先 prefill，再用单 token decode 更新 KV。每条请求独立维护 EOS、长度和 position IDs；greedy、multinomial 与 Gumbel 共用完整循环。"
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
  - title: "PyTorch multinomial: independent distributions in matrix rows"
    url: "https://docs.pytorch.org/docs/2.14/generated/torch.multinomial.html"
    type: primary
---

## 题目描述

来源：本手册原创 batch generation 练习。服务同时收到长度不同的 prompts，需要一次 prefill，随后用 KV cache 逐 token 生成。每条请求可以使用 greedy、multinomial 或 Gumbel sampling，生成 EOS 的请求独立结束，其他请求继续。

### 输入与接口

实现 `generate_batch(model, input_ids, attention_mask, eos, pad, max_new, method="greedy", temperature=1.0, top_k=None, top_p=1.0, allowed_fn=None, generator=None)`。

- `input_ids` 是 long `[B,P]`，B、P>0，含 left padding；`attention_mask` 是同设备 bool `[B,P]`，每行先 False 后 True，至少一个 True。禁止 right padding 和中间空位，padding 由 mask 定义，不从 token ID 推断。
- `eos`、`pad` 是合法 token IDs，可以相等。Prompt 中即使出现 EOS 也不表示已经结束；只有新生成的 EOS 才终止。`max_new` 是非负整数，统一规定最大新增 token 数。
- selection 参数与 [[apple-batched-token-selection]] 相同，可按 row 分别指定；此卡包含同一份 selector，无需导入其他卡。
- `allowed_fn(step, rows, prefix)` 可选，返回 bool `[A,V]`。A 是本轮 active 请求数；rows 为它们原始 batch row IDs `[A]`；prefix 为已经生成的 `[A,step]`，不含 prompt。可以依据这些信息构造动态合法集合。本题不要求实现 JSON grammar compiler。

### 给定的 model adapter 合同

`model.prefill(input_ids, attention_mask, position_ids)` 返回 `(next_logits, cache)`，next logits 为 `[B,V]`，表示每行最后一个有效 prompt token 后的分布。

`model.decode(token_ids, attention_mask, position_ids, cache)` 接收 `[B,1]` 新 token、覆盖旧 cache 与新物理 slot 的 `[B,L+1]` mask、当前新 token 的逻辑 position `[B,1]`，返回下一轮 logits `[B,V]` 和更新后的 cache。Adapter 必须使用传入 positions 和 mask，并由调用方设置模型为 eval。下方提供不下载权重的小型真实 causal attention 模型作为测试 adapter，面试时可视为给定代码。

### 输出与状态规则

返回字典：`tokens` 为 `[B,max_new]`，只含新增 tokens，EOS 包含在内，未使用位置填 pad；`lengths` 为 long `[B]`，计入 EOS、不计 padding；`finished` 为 bool `[B]`，只有实际生成 EOS 才为 True。顶到 max_new 的请求可以 finished=False。max_new=0 时返回空 tokens、全零 lengths、全 False finished，且不调用模型。

不修改输入。已结束请求不再参加 token selection，不再增加长度；保留 static batch slot，后续填充 slot 的 mask 为 False。Cache 的物理长度随整个 batch 增长，但 position ID 按每条请求有效 token 数增长。返回的是生成结果，不返回 cache；最后一个选中的 token 不一定已经送入 decode。

### 输入输出示例

```text
input_ids=[[0,0,4],[2,3,4]]
attention_mask=[[False,False,True],[True,True,True]]
eos=1, pad=0, max_new=4

假设合法集合规定：row 0 第一步只能生成 1；row 1 依次只能生成 5、1。
返回 tokens=[[1,0,0,0],[5,1,0,0]], lengths=[1,2], finished=[True,True]。
prefill 输入宽度 3；只需一次 decode，输入宽度 1；不重算整个前缀。
```

## 解题思路与参考答案

第一条请求只有一个真实 prompt token，第二条有三个。两者虽然都占三列，下一 token 的逻辑 position 分别是 1 和 3，不能直接用矩阵列数当 position ID。

我会先 prefill 一次，再维护 finished 与 lengths。每轮只给 active rows 选 token，记录第一次 EOS，然后用刚选出的 token 更新 cache。已结束请求的旧证据仍保留，后续 filler 被 mask，不会被其他请求使用。

### 给定的 adapter 与真实 attention 测试模型

`TinyCausalLM` 是随机初始化、单层单头的 attention 测试模型，不是有语言能力的预训练模型。它实现真实 Q/K/V、位置和 causal mask，因而能暴露“缓存没重排”“padding position 用错”等问题。真实多层模型需要自己的 adapter；本题接口不是 Hugging Face Cache 类的直接兼容承诺。

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
### Batch token selection

这段与单步卡使用相同接口。Greedy、multinomial 与 Gumbel 都会实际接入下面的生成循环。

```python
import math
import torch


def row_parameter(value, batch, device, dtype, name):
    result = torch.as_tensor(value, device=device, dtype=dtype)
    if result.ndim == 0:
        result = result.expand(batch)
    if result.shape != (batch,):
        raise ValueError(f"{name} must be scalar or [B]")
    return result


@torch.no_grad()
def select_token(
    logits,
    temperature=1.0,
    top_k=None,
    top_p=1.0,
    allowed=None,
    method="multinomial",
    generator=None,
):
    """[B,V] -> [B]; True means allowed. All filtering is per row."""
    if logits.ndim != 2 or logits.shape[1] == 0:
        raise ValueError("logits must have shape [B,V], V > 0")
    batch, vocab = logits.shape
    if method not in ("greedy", "multinomial", "gumbel"):
        raise ValueError("unknown selection method")
    scores = logits.to(torch.float64).clone()
    if torch.isnan(scores).any() or torch.isposinf(scores).any():
        raise ValueError("NaN and +inf logits are unsupported")
    if allowed is not None:
        if allowed.shape != scores.shape or allowed.dtype != torch.bool:
            raise ValueError("allowed must be bool [B,V]")
        scores.masked_fill_(~allowed, -torch.inf)
    if not torch.isfinite(scores).any(dim=-1).all():
        raise ValueError("every active row needs a finite allowed logit")
    temp = row_parameter(temperature, batch, scores.device, scores.dtype, "temperature")
    nucleus = row_parameter(top_p, batch, scores.device, scores.dtype, "top_p")
    if not torch.isfinite(temp).all() or (temp < 0).any():
        raise ValueError("temperature must be finite and >= 0")
    if not torch.isfinite(nucleus).all() or ((nucleus < 0) | (nucleus > 1)).any():
        raise ValueError("top_p must be finite and in [0,1]")
    if top_k is None:
        counts = torch.full((batch,), vocab, dtype=torch.long, device=scores.device)
    else:
        raw = row_parameter(top_k, batch, scores.device, scores.dtype, "top_k")
        if (
            not torch.isfinite(raw).all()
            or (raw < 1).any()
            or (raw != raw.floor()).any()
        ):
            raise ValueError("top_k must contain positive integers")
        counts = raw.clamp(max=vocab).long()
    result = scores.argmax(dim=-1)  # Ties: first (smallest) token ID.
    stochastic = (temp > 0) & (nucleus > 0)
    if method == "greedy" or not stochastic.any():
        return result
    # Only stochastic rows consume RNG; deterministic rows do not.
    rows = stochastic.nonzero(as_tuple=True)[0]
    work = scores[rows]
    work = (work - work.max(dim=-1, keepdim=True).values) / temp[rows, None]
    ordered, ids = torch.sort(work, dim=-1, descending=True, stable=True)
    rank = torch.arange(vocab, device=scores.device)[None, :]
    ordered.masked_fill_(rank >= counts[rows, None], -torch.inf)
    probs = ordered.softmax(dim=-1)  # Normalize AFTER top-k.
    cumulative = probs.cumsum(dim=-1)
    # Keep the crossing token too. p=1 explicitly keeps every top-k survivor.
    before = torch.cat(
        [torch.zeros_like(cumulative[:, :1]), cumulative[:, :-1]], dim=-1
    )
    keep = (before < nucleus[rows, None]) | (nucleus[rows, None] == 1)
    ordered.masked_fill_(~keep, -torch.inf)
    if method == "multinomial":
        picked = torch.multinomial(ordered.softmax(dim=-1), 1, generator=generator)
    else:
        u = torch.rand(
            ordered.shape,
            dtype=ordered.dtype,
            device=ordered.device,
            generator=generator,
        )
        eps = torch.finfo(u.dtype).eps
        noise = -torch.log(-torch.log(u.clamp(min=eps, max=1 - eps)))
        picked = (ordered + noise).argmax(dim=-1, keepdim=True)
    result[rows] = ids.gather(-1, picked).squeeze(-1)
    return result
```
### 完整生成循环

```python
@torch.no_grad()
def generate_batch(
    model,
    input_ids,
    attention_mask,
    eos,
    pad,
    max_new,
    method="greedy",
    temperature=1.0,
    top_k=None,
    top_p=1.0,
    allowed_fn=None,
    generator=None,
):
    """Static batch generation. Returns NEW tokens, lengths, finished."""
    validate_prompt(input_ids, attention_mask, max_new, eos, pad)
    batch = input_ids.shape[0]
    device = input_ids.device
    output = torch.full((batch, max_new), pad, dtype=torch.long, device=device)
    lengths = torch.zeros(batch, dtype=torch.long, device=device)
    finished = torch.zeros(batch, dtype=torch.bool, device=device)
    if max_new == 0:
        return {"tokens": output, "lengths": lengths, "finished": finished}
    mask = attention_mask.clone()
    positions = (mask.long().cumsum(-1) - 1).clamp(min=0)
    logits, cache = model.prefill(input_ids, mask, positions)
    vocab = logits.shape[-1]
    if not 0 <= eos < vocab or not 0 <= pad < vocab:
        raise ValueError("eos and pad must be in vocabulary")
    temp = row_parameter(temperature, batch, device, torch.float64, "temperature")
    nucleus = row_parameter(top_p, batch, device, torch.float64, "top_p")
    counts = (
        None
        if top_k is None
        else row_parameter(top_k, batch, device, torch.float64, "top_k")
    )
    for step in range(max_new):
        active = ~finished
        rows = active.nonzero(as_tuple=True)[0]
        # Callback sees original row IDs and generated prefix (including EOS).
        allowed = (
            None if allowed_fn is None else allowed_fn(step, rows, output[rows, :step])
        )
        chosen = select_token(
            logits[rows],
            temp[rows],
            None if counts is None else counts[rows],
            nucleus[rows],
            allowed,
            method,
            generator,
        )
        next_tokens = torch.full((batch,), pad, dtype=torch.long, device=device)
        next_tokens[rows] = chosen
        output[:, step] = next_tokens
        lengths += active.long()  # Includes the first generated EOS.
        finished |= active & (next_tokens == eos)
        if finished.all() or step + 1 == max_new:
            break
        # Logical position counts real tokens; physical cache also has padding slots.
        next_positions = mask.sum(dim=-1, keepdim=True).long()
        next_positions = torch.where(active[:, None], next_positions, 0)
        mask = torch.cat([mask, active[:, None]], dim=-1)
        logits, cache = model.decode(next_tokens[:, None], mask, next_positions, cache)
    return {"tokens": output, "lengths": lengths, "finished": finished}
```
## 简单测试怎么写

依次复制 adapter、selector、生成循环和以下测试，保存为 `solution.py`，运行 `python solution.py`。除了可手算的两条请求，还用完整前缀重算作独立参考：先逐步比较 logits，再比较三种生成模式的最终结果。

```python
torch.set_num_threads(1)


class FullPrefixLM(TinyCausalLM):
    """Independent recomputation adapter: caches tokens, NOT attention K/V."""

    def prefill(self, input_ids, attention_mask, position_ids):
        logits, _ = self._forward(input_ids, attention_mask, position_ids, None)
        return logits, (input_ids.clone(), position_ids.clone())

    def decode(self, token_ids, attention_mask, position_ids, cache):
        ids = torch.cat([cache[0], token_ids], dim=1)
        positions = torch.cat([cache[1], position_ids], dim=1)
        logits, _ = self._forward(ids, attention_mask, positions, None)
        return logits, (ids, positions)


ids = torch.tensor([[0, 0, 4], [2, 3, 4]])
mask = torch.tensor([[False, False, True], [True, True, True]])
original_ids, original_mask = ids.clone(), mask.clone()
seen = []


def force_tokens(step, rows, prefix):
    seen.append(rows.tolist())
    result = torch.zeros((rows.numel(), 7), dtype=torch.bool)
    for i, row in enumerate(rows.tolist()):
        token = 1 if row == 0 or step == 1 else 5
        result[i, token] = True
    return result


model = TinyCausalLM()
out = generate_batch(model, ids, mask, eos=1, pad=0, max_new=4, allowed_fn=force_tokens)
assert out["tokens"].tolist() == [[1, 0, 0, 0], [5, 1, 0, 0]]
assert out["lengths"].tolist() == [1, 2]
assert out["finished"].tolist() == [True, True]
assert seen == [[0, 1], [1]]
assert model.calls == [3, 1]  # One prefill, then only a single input token.
assert torch.equal(ids, original_ids) and torch.equal(mask, original_mask)
# Same value for pad and EOS must still use explicit masks and lengths.
result = generate_batch(
    TinyCausalLM(),
    ids,
    mask,
    eos=0,
    pad=0,
    max_new=3,
    allowed_fn=lambda step, rows, prefix: torch.nn.functional.one_hot(
        torch.zeros(rows.numel(), dtype=torch.long), 7
    ).bool(),
)
assert result["lengths"].tolist() == [1, 1]
# Zero generation does not invoke the model, even when the prompt contains EOS.
empty_model = TinyCausalLM()
empty = generate_batch(empty_model, ids, mask, eos=4, pad=0, max_new=0)
assert empty["tokens"].shape == (2, 0) and not empty["finished"].any()
assert empty_model.calls == []
# Every step's cached logits must match complete-prefix recomputation.
a, b = TinyCausalLM(), FullPrefixLM()
positions = (mask.long().cumsum(-1) - 1).clamp(min=0)
x, kv = a.prefill(ids, mask, positions)
y, reference = b.prefill(ids, mask, positions)
assert torch.allclose(x, y, atol=1e-6, rtol=1e-6)
current_mask = mask.clone()
for token in (torch.tensor([[3], [5]]), torch.tensor([[2], [1]])):
    pos = current_mask.sum(-1, keepdim=True)
    current_mask = torch.cat([current_mask, torch.ones(2, 1, dtype=torch.bool)], -1)
    x, kv = a.decode(token, current_mask, pos, kv)
    y, reference = b.decode(token, current_mask, pos, reference)
    assert torch.allclose(x, y, atol=1e-6, rtol=1e-6)
# Full loop matches recomputation, including stochastic RNG replay.
for method in ("greedy", "multinomial", "gumbel"):
    options = dict(
        eos=1,
        pad=0,
        max_new=6,
        method=method,
        temperature=[0.7, 1.2],
        top_k=[3, 4],
        top_p=[0.8, 0.95],
    )
    cached = generate_batch(
        TinyCausalLM(),
        ids,
        mask,
        **options,
        generator=torch.Generator().manual_seed(66),
    )
    full = generate_batch(
        FullPrefixLM(),
        ids,
        mask,
        **options,
        generator=torch.Generator().manual_seed(66),
    )
    for key in cached:
        assert torch.equal(cached[key], full[key]), (method, key)
# Greedy batch equals each unpadded prompt run independently.
batched = generate_batch(TinyCausalLM(), ids, mask, eos=1, pad=0, max_new=6)
for row in range(2):
    prompt = ids[row][mask[row]][None, :]
    single = generate_batch(
        TinyCausalLM(),
        prompt,
        torch.ones_like(prompt, dtype=torch.bool),
        eos=1,
        pad=0,
        max_new=6,
    )
    for key in batched:
        assert torch.equal(batched[key][row], single[key][0]), key
# Right padding is explicitly rejected, rather than gathering the wrong logits.
try:
    generate_batch(
        TinyCausalLM(),
        torch.tensor([[4, 0]]),
        torch.tensor([[True, False]]),
        eos=1,
        pad=0,
        max_new=2,
    )
except ValueError:
    pass
else:
    raise AssertionError("right padding should fail")
print("Batched cached generation: tests passed")
```
## 复杂度与面试追问

生成器执行一次 prefill，至多 `max_new-1` 次单 token decode；各调用内部计算量依赖模型。Selection 若完整排序，累计最坏为 `O(max_new B V log V)`；输出空间为 `O(B max_new)`，KV 另按模型层数、heads 与 cache 长度计算。

**为什么这里不直接删掉 finished rows？** 这是 static batching 教学实现，让 row ID 与 cache slot 保持稳定。Active compaction 需要同步 gather tokens、mask、positions、cache 和原请求映射；continuous batching 还要处理新请求加入、不同 prefill 状态与调度，本题不声称已经实现。

**为什么 decode 输入只有一个 token，mask 却越来越长？** Query 来自新 token，keys 包括历史 cache；mask 必须同时覆盖两者。逻辑 position 与 cache physical slot 也不应混用。

**EOS 和 pad 相等会错吗？** 不会。Finished 由本轮 active row 是否新生成 EOS 决定，padding 是否有效由 mask 决定，不能仅凭 token 数值分类。

继续做 [[apple-batched-beam-search]]，检查一个 parent 产生多个 child 时如何复制 cache。
