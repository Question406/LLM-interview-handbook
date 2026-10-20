---
id: coding-token-logprob
section: coding
order: 42
level: S
title: 白板：从 logits 取 response 的 token logprob，shift、temperature 和显存
quick: "位置 $t$ 的 logits 预测第 $t+1$ 个 token，所以 `logits[:, :-1]` 对 `ids[:, 1:]`；训练端要除以和采样时相同的温度 $T$，再用目标 logit 减 `logsumexp`。"
tags:
  - 完整编程练习
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: torch.gather
    url: https://pytorch.org/docs/stable/generated/torch.gather.html
    type: primary
  - title: torch.logsumexp
    url: https://pytorch.org/docs/stable/generated/torch.logsumexp.html
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `token_logprobs(logits, input_ids, temperature=1.0) -> [B, L-1]`：`logits` 是 `[B, L, V]`，`input_ids` 是 `[B, L]`。输出的第 `t` 列是位置 `t` 的 logits 给 `input_ids[:, t+1]` 的 log 概率，在 float32 里计算。
- `token_logprobs_chunked(logits, input_ids, temperature=1.0, chunk=1024)`：结果相同，但沿序列维每次只把 `chunk` 个位置转成 float32，限制临时显存。
- 要求 `temperature > 0`、`chunk >= 1`，且 `logits` 的前两维和 `input_ids` 形状一致，否则抛 `ValueError`。
- `L <= 1` 时没有可预测的下一个 token，返回形状 `[B, 0]` 的空张量。
- 函数不处理 response mask。调用方要把 mask 也左移一位（`mask[:, 1:]`）再和结果对齐。

### 输入输出示例

```text
logits 全为 0, V = 4    -> 每个位置的 logprob 都是 -ln 4 ≈ -1.386
L = 1                  -> 形状 [B, 0] 的空张量
输出第 t 列             <-> 目标 token input_ids[:, t+1]
```

### 解题思路与正确性

causal LM 在位置 $t$ 的输出是 $p(x_{t+1}\mid x_{\le t})$，所以在时间维上 shift 一次：`logits[:, :-1]` 和 `input_ids[:, 1:]` 一一对应。

温度作用在 logits 上：采样分布是 $\mathrm{softmax}(z/T)$，训练端除以同一个 $T$，算出的 logprob 才和 rollout 时存下的一致。

单个 token 的 log 概率是 $\log p(y)=z_y-\log\sum_v e^{z_v}$。`gather` 取出目标位置的 logit，再减去 `logsumexp`；`logsumexp` 内部会先减最大值，数值稳定，而且不需要物化完整的 `log_softmax`。

分块版本按「预测位置」切块：第 `start` 到 `end` 个预测位置用 `logits[:, start:end]` 和 `targets[:, start:end]`，两者偏移完全相同，分块不会重新引入错位。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def _check_inputs(logits, input_ids, temperature):
    if temperature <= 0:
        raise ValueError(f"temperature must be positive, got {temperature}")
    if logits.dim() != 3 or logits.shape[:2] != input_ids.shape:
        raise ValueError(
            f"expected logits [B, L, V] and input_ids [B, L], "
            f"got {tuple(logits.shape)} and {tuple(input_ids.shape)}"
        )


def token_logprobs(logits, input_ids, temperature=1.0):
    """logits [B, L, V]、input_ids [B, L] -> [B, L-1]；第 t 列是 input_ids[:, t+1] 的 logprob。"""
    _check_inputs(logits, input_ids, temperature)
    scaled = logits[:, :-1].float() / temperature  # [B, L-1, V]，位置 t 预测 t+1
    targets = input_ids[:, 1:]                       # [B, L-1]
    picked = scaled.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return picked - torch.logsumexp(scaled, dim=-1)


def token_logprobs_chunked(logits, input_ids, temperature=1.0, chunk=1024):
    """和 token_logprobs 相同，但每次只把 chunk 个位置转成 float32。"""
    _check_inputs(logits, input_ids, temperature)
    if chunk < 1:
        raise ValueError(f"chunk must be >= 1, got {chunk}")
    batch, length = input_ids.shape
    n_predictions = length - 1
    if n_predictions <= 0:
        return logits.new_zeros((batch, 0), dtype=torch.float32)

    targets = input_ids[:, 1:]  # [B, L-1]
    pieces = []
    for start in range(0, n_predictions, chunk):
        end = min(start + chunk, n_predictions)
        scaled = logits[:, start:end].float() / temperature  # [B, end-start, V]
        picked = scaled.gather(-1, targets[:, start:end].unsqueeze(-1)).squeeze(-1)
        pieces.append(picked - torch.logsumexp(scaled, dim=-1))
    return torch.cat(pieces, dim=1)
```

### 可执行测试

```python
torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(2)
logits = torch.randn(2, 6, 7)
ids = torch.randint(0, 7, (2, 6))
reference = F.log_softmax(logits[:, :-1] / 0.7, -1).gather(-1, ids[:, 1:, None]).squeeze(-1)

# 和 log_softmax + gather 的参考结果一致（含 shift 和温度）
assert torch.allclose(token_logprobs(logits, ids, 0.7), reference, atol=1e-6)

# 分块大小不整除、等于 1、大于长度时都和不分块一致
for chunk in (1, 2, 4, 20):
    assert torch.allclose(token_logprobs_chunked(logits, ids, 0.7, chunk), reference, atol=1e-6)

# L = 1：没有可预测的 token，返回 [B, 0]
assert token_logprobs_chunked(logits[:, :1], ids[:, :1]).shape == (2, 0)
assert token_logprobs(logits[:, :1], ids[:, :1]).shape == (2, 0)

# 均匀 logits：每个位置都是 -ln V
uniform = token_logprobs(torch.zeros(1, 3, 4), torch.tensor([[0, 1, 2]]))
assert torch.allclose(uniform, torch.full((1, 2), -torch.log(torch.tensor(4.0)).item()))

# bf16 logits 在 float32 里计算，结果是 float32
assert token_logprobs(logits.to(torch.bfloat16), ids).dtype == torch.float32

# 非法参数
expect_value_error(lambda: token_logprobs(logits, ids, 0.0))
expect_value_error(lambda: token_logprobs_chunked(logits, ids, 1.0, 0))
expect_value_error(lambda: token_logprobs(logits, ids[:, :5]))
```

### 复杂度与追问

设 batch 为 B、序列长 L、词表 V、分块大小为 C。时间 O(B·L·V)。分块版本每块的 float32 中间量是 O(B·C·V)；但输入的 logits 本身已经占了 O(B·L·V)，分块只能省掉它的 float32 副本。

- 追问「连 logits 都放不下」：不物化完整的 logits，把 lm_head 和这一步融合起来分块计算，见 `coding-fused-ce`。

## 题怎么来的

所有强化学习（RL）损失（loss）的输入都是 `policy_logprobs`，它就是从这一步算出来的。这几行错了，后面的 ratio、KL、clip 全是错的，而且 loss 看起来照样在下降。这道题常和 `coding-tis-mismatch`、`sys-rollout-logprob` 一起问。面试给你的代码是下面这段。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修的错误片段，不是参考答案。对照上方题面，找出它偏离接口约定的地方；正确实现和测试在上面的练习里。

```python
def token_logprobs(logits, input_ids, temperature):
    # logits: [B, L, V]；input_ids: [B, L] = prompt + response
    logp = torch.log_softmax(logits, dim=-1)
    return logp.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)
```

## 错在哪

**没有 shift。** causal LM 在位置 $t$ 输出的是 $p(x_{t+1}\mid x_{\le t})$。这段代码在位置 $t$ 的分布上取的是 $x_t$ 的概率，每个 token 都错开了一位。

**temperature 没用上。** 采样时的分布是 $\mathrm{softmax}(z/T)$，采样轨迹（rollout）里存下的 logprob 也是这个分布下的。训练端用 $\mathrm{softmax}(z)$ 重算，即使权重完全一样，第一步的 ratio 也不是 1，clip 会被无意义地触发。$T$ 必须和采样时完全一致。

**精度和显存。** logits 往往是 bf16，直接做 `log_softmax` 精度不够；先 `.float()` 又会复制一份 `[B, L, V]`。$V$ 在 15 万左右、$L$ 一万时，一条序列的 fp32 logits 就有 6 GB，batch 稍大就是几十 GB。

## 改法

改法就是上面的参考实现：shift 一位、除以温度、用 `gather` 取目标 logit 再减 `logsumexp`，结果只有 `[B, L-1]`。返回的第 $t$ 个位置对应 `input_ids[:, t+1]`，response mask 也要同样左移一位：`mask[:, 1:]`。

`.float()` 仍然会复制一份 logits。显存吃紧时用 `token_logprobs_chunked` 沿序列切块，每次只转一块。验证方法也在上面的测试里：和 `F.log_softmax` + `gather` 的结果对照，并检查不同分块大小结果一致。

## 追问

**采样时还用了 top-p / top-k 呢？** 采样分布是截断后重新归一化的，训练端用完整 softmax 算出的 logprob 和它对不上。要么让推理引擎返回完整分布下的 logprob，要么两端用同一套截断规则。先确认你的推理引擎返回的是哪一种。

**只要 response 的 logprob，输入提示（prompt）部分能不能不算？** lm_head 和 logsumexp 都可以只在 response 的位置上做，prompt 很长时能省很多。不过前向的 hidden state 仍然要对整条序列计算。

**熵要不要顺便算？** 用同一份 `z`，$H = \mathrm{logsumexp}(z) - \sum_v \mathrm{softmax}(z)_v z_v$。这又需要一次 softmax，显存上和前面一样要切块，见 `openai-entropy-l1`。

## 相关题

- [[sys-rollout-logprob]]：这里的 shift 和温度写错时，现象就是那张说的 rollout 与训练 logprob 对不上、ratio 不为 1。
- [[coding-tis-mismatch]]：logprob 本身算对之后，推理引擎和训练端仍有数值差，那张讲用截断重要性权重修正。
- [[openai-entropy-l1]]：同一份 logits 上算熵，OpenAI 真题还追问把损失换成 L1 时怎么求梯度。
- [[coding-fused-ce]]：同样的 `[B, T, V]` 显存问题，那张沿词表分块攒 logsumexp，不物化整份 logits。
- [[openai-logprob]]：口述题，讲 API 返回的 logprob 什么时候能当置信度，以及采样温度和校准温度为什么是两颗旋钮。
- [[coding-topk-nucleus]]：采样端怎么用温度；训练端算 logprob 时要用同一个 $T$。
