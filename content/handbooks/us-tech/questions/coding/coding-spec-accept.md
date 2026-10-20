---
id: coding-spec-accept
section: coding
order: 31
level: S
title: 白板：投机解码接受规则，拒绝后从哪一步重采样
quick: "草稿 token 按 $\\min(1,p/q)$ 从左到右接受；第一次在第 $i$ 步拒绝时，在第 $i$ 步从残差 $\\max(0,p-q)$ 抽一个 token 并丢掉后续草稿，全部接受则从 $p$ 多抽一个。"
tags:
  - 完整编程练习
  - Coding
  - Speculative Decoding
  - Sampling
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
  - title: Accelerating Large Language Model Decoding with Speculative Sampling
    url: https://arxiv.org/abs/2302.01318
    type: primary
  - title: Speculative Decoding — vLLM
    url: https://docs.vllm.ai/en/latest/features/spec_decode.html
    type: secondary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证；不模拟模型前向，也不做 KV 回滚。

### 题面、接口与约束

- `residual_probs(p_logits, q_logits) -> [V]`：返回归一化的 $\max(p-q,0)$。残差全为 0 时抛 `ValueError`，不能把全 0 向量当成合法分布。
- `spec_accept(draft_ids, log_p, log_q, p_logits, q_logits, bonus_logits) -> (tokens, reject_at)`：从左到右验证草稿。第一次拒绝时从残差抽一个修正 token 并停止；全部接受时再从 `bonus_logits` 追加一个 bonus token。`reject_at` 是拒绝位置，全部接受时为 `None`。
- 输入：`draft_ids: [G]` 确实是从 $q$ 采样的；`log_p`、`log_q: [G]` 是草稿 token 在目标模型和草稿模型下的 logprob；`p_logits`、`q_logits: [G, V]` 是每个已提出前缀下的条件分布；`bonus_logits: [V]` 是全部接受后下一个 token 的分布。
- 约束：$G=0$ 时仍要抽一个 bonus token。

### 输入输出示例

```text
p == q，草稿 [0, 1]，bonus 只能抽到 0     -> ([0, 1, 0], None)
p 给草稿 token 的概率是 0                 -> 第 0 步拒绝，([残差里抽的 token], 0)
单步：p = [0.8, 0.2]，q = [0.2, 0.8]      -> 多次采样后，输出为 0 的比例约 0.8
```

### 解题思路与正确性

第 $i$ 步以 $\min(1, p(\hat y_i)/q(\hat y_i))$ 接受草稿 token。对任意 token $v$，它被「草稿提出并接受」的概率是 $q(v)\min(1,p(v)/q(v))=\min(p(v),q(v))$；总的拒绝概率是 $1-\sum_v\min(p,q)=\sum_v\max(0,p-q)$，拒绝后再按残差抽，又补上 $\max(0,p(v)-q(v))$。两部分相加正好是 $p(v)$，所以输出的边际分布就是目标分布。

$p=q$ 时接受概率恒为 1，不会走到残差这一步；如果真的走到了全 0 残差，说明 $p$、$q$ 算错了，参考实现直接报错。

### 完整参考实现（Python 3）

```python
import math

import torch
import torch.nn.functional as F


def residual_probs(p_logits, q_logits):
    """拒绝后重采样用的残差分布 normalize(max(p - q, 0))。[V] -> [V]。

    p == q 时残差全为 0，按规则此时不可能发生拒绝，所以直接报错，不返回假分布。
    """
    p = F.softmax(p_logits.float(), dim=-1)
    q = F.softmax(q_logits.float(), dim=-1)
    residual = (p - q).clamp(min=0)
    total = residual.sum()
    if total <= 0:
        raise ValueError("no residual mass: rejection is impossible when p == q")
    return residual / total


def spec_accept(draft_ids, log_p, log_q, p_logits, q_logits, bonus_logits):
    """投机解码的验证步：从左到右按 min(1, p/q) 接受草稿 token。

    draft_ids, log_p, log_q: [gamma]，草稿 token 及其在目标 / 草稿模型下的 logprob。
    p_logits, q_logits: [gamma, V]，每个草稿位置的条件分布；bonus_logits: [V]，全部接受后的下一步。
    返回 (输出 token 列表, 拒绝位置 i 或 None)。第一次拒绝时在位置 i 从残差抽一个 token 并停止；
    全部接受（包括 gamma == 0）时再从 bonus 分布多抽一个。
    """
    output = []
    for i in range(draft_ids.numel()):
        accept_prob = torch.exp(log_p[i] - log_q[i]).clamp(max=1.0)   # 在 log 域相减
        if torch.rand(()) < accept_prob:
            output.append(int(draft_ids[i]))
            continue
        corrected = int(torch.multinomial(residual_probs(p_logits[i], q_logits[i]), 1))
        output.append(corrected)
        return output, i
    bonus = int(torch.multinomial(F.softmax(bonus_logits.float(), dim=-1), 1))
    output.append(bonus)
    return output, None
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
torch.manual_seed(2)
uniform = torch.tensor([[0.0, 0.0], [0.0, 0.0]])
half = torch.tensor([-math.log(2)] * 2)
only_token_0 = torch.tensor([0.0, -float("inf")])

# p == q：草稿全部接受，再追加 bonus（bonus 分布只能抽到 0）
tokens, reject_at = spec_accept(torch.tensor([0, 1]), half, half, uniform, uniform, only_token_0)
assert tokens == [0, 1, 0]
assert reject_at is None

# gamma = 0：没有草稿，仍从 bonus 分布抽一个
tokens, reject_at = spec_accept(torch.tensor([], dtype=torch.long), torch.zeros(0), torch.zeros(0),
                                torch.zeros(0, 2), torch.zeros(0, 2), only_token_0)
assert tokens == [0]
assert reject_at is None

# p 对草稿 token 的概率为 0：第 0 步必拒绝，从残差抽到 token 0，后面的草稿丢弃
p_row = torch.tensor([0.0, -float("inf")])
q_row = torch.tensor([0.0, 0.0])
tokens, reject_at = spec_accept(torch.tensor([1, 1]), torch.tensor([-float("inf"), 0.0]), half,
                                torch.stack([p_row, p_row]), torch.stack([q_row, q_row]), only_token_0)
assert tokens == [0]
assert reject_at == 0

# 单步采样的输出分布服从 p，而不是 q
p = torch.tensor([0.8, 0.2])
q = torch.tensor([0.2, 0.8])
samples = []
for _ in range(5000):
    draft = torch.multinomial(q, 1)
    token = int(draft[0])
    out, _ = spec_accept(draft, p[token].log()[None], q[token].log()[None], p.log()[None], q.log()[None], p.log())
    samples.append(out[0])
assert abs(samples.count(0) / len(samples) - 0.8) < 0.025

# p == q 时残差全 0，不能当成合法分布
expect_value_error(residual_probs, torch.zeros(2), torch.zeros(2))
```

### 复杂度与追问

设草稿长度为 $G$（即 $\gamma$）、词表大小为 $V$。验证后的处理最坏 $O(GV)$：只有拒绝那一步要对整个词表算残差，但 `p_logits`、`q_logits` 本身是 $G\times V$。输出最多 $G+1$ 个 token。

- 追问「cache 怎么回滚」：这里只返回拒绝位置，不处理 KV；需要回滚 cache 的独立练习见 `openai-speculative-decoding`。

## 题怎么来的

这是 Leviathan et al. 和 DeepMind 的 speculative sampling：小模型一次提出 $\gamma$ 个 token，大模型做一次前向，给出这些位置的 logits，再用拒绝采样保证边际分布仍然是 $p$。Google / OpenAI 的推理白板题要你写出接受不等式，并讲清「拒绝后从哪一步重采样」，而不是算加速比。KV 回滚见 `openai-speculative-decoding`、`sys-spec-sys`。本题把规则写成代码。前缀记作 $x_{1:t-1}$。

## 从左到右，第一次拒绝就停

草稿模型 $q$ 依次采样 $\hat y_1,\ldots,\hat y_\gamma$。目标模型 $p$ 在一次并行前向里给出每个位置的条件分布 $p(\cdot\mid x_{1:t-1},\hat y_{1:i-1})$，以及全部接受时下一步的分布 $p(\cdot\mid x_{1:t-1},\hat y_{1:\gamma})$。对 $i=1,\ldots,\gamma$，接受概率是

$$
\alpha_i=\min\bigl(1,\,p(\hat y_i)/q(\hat y_i)\bigr).
$$

抽 $u_i\sim\mathrm{Unif}(0,1)$。若 $u_i\le\alpha_i$，接受 $\hat y_i$，继续下一步。若拒绝，就在同一个位置 $i$ 从残差分布

$$
n(v)\propto\max\bigl(0,\,p(v)-q(v)\bigr)
$$

采样 $y_i$，输出 $\hat y_{1:i-1},y_i$，丢掉 $\hat y_{i+1:\gamma}$。若全部接受，再从 $p(\cdot\mid x_{1:t-1},\hat y_{1:\gamma})$ 多抽一个 bonus token，这保证每轮至少产出一个 token，期望产出长度大于 1。

残差必须在被拒绝的那一步求，条件是已接受的前缀，而不是草稿的第 $i+1$ 步。常见错误有两种：拒绝后直接从 $p$ 采样，却把后面的草稿留着；或者拒绝后从第 1 步重来。数值上用 logprob 计算 $\alpha=\min(1,\exp(\log p-\log q))$，在 log 域相减，避免先 $\exp$ 再相除。

参考实现返回的 `reject_at`（从 0 开始）就是拒绝位置 $i$：KV cache 从 $S+\gamma$ 截回 $S+i$，再写入重采样出的那个 token。`None` 表示全部接受，这一轮后序列长度是 $S+\gamma+1$，其中 bonus token 的 KV 要到下一次前向才写入。用 greedy 做对照测试：令 $p=q$ 应该全部接受；让草稿总是给出错误 token、且 $p$ 很尖，应该在 $i=0$ 就走残差采样。

## 和系统、采样栈的接口

$p$ 和 $q$ 必须用同一个 tokenizer、同一套词表约束。非法 token 要在两边都设成 $-\infty$，再比较 $\log p-\log q$，不要只 mask 一边。如果有温度、top-k、nucleus，要规定清楚是只改 $p$、只改 $q$，还是两边用同一套；混用会破坏「边际仍是 $p$」的证明，见 `coding-topk-nucleus`。树状草稿只是把这条规则沿多条前缀执行，最终接受的仍然是从根出发的一条链。

不要把 $\gamma$ 个草稿的 logprob 加起来，只做一次接受判断：那是整段接受或整段拒绝，不是论文里的算法，期望长度和方差都会变。

理论上 $p=q$ 时残差全为 0，但这时也不会发生拒绝。如果数值误差把 $p-q$ 全变成非正数，clamp 后就没有残差。练习版直接抛错，方便暴露问题；生产代码通常退回到直接从 $p$ 采样，同时检查两边的 softmax 温度是否一致。

## 追问

- **拒绝后为什么不从第 $i+1$ 步抽？** 位置 $i$ 还没有合法的 token。第 $i+1$ 步的草稿以被拒绝的 token 为条件，它的分布已经作废。
- **残差全为 0 怎么办？** $p=q$ 时不会拒绝。如果数值误差让残差全为 0，退回到从 $p$ 采样，并检查两边的 logprob 是否来自同一套 softmax。
- **bonus token 算不算投机产出？** 算。全部接受时目标模型已经完成了这次前向，顺手多抽一个，论文的原算法就包含这一步。
- **什么时候和 greedy 逐 token 解码的结果逐字相同？** $p$ 取 $\arg\max$、$q$ 也用 greedy，且草稿总被接受时。随机采样只保证分布一致，不保证生成的字符串相同；排查 KV 回滚时用 greedy。

## 相关题

- [[p3a-cursor-speculative-decoding-acceptance]]：同一条接受规则和残差采样，Cursor 题面要求写出完整的 draft / target 循环，并统计 target 调用了几次。
- [[google-spec-decode]]：口述为什么这样接受是无损的，以及和 Medusa / EAGLE 的区别。
- [[openai-speculative-decoding]]：拒绝之后 KV cache 怎么截断，是接受规则之外的工程部分。
- [[p3a-xai-speculative-edits]]：greedy 版本，用原代码当草稿，只接受和模型预测一致的前缀，用不到 $p/q$。
- [[nvidia-spec-medusa]]：草稿换成 Medusa 头或 EAGLE 之后，验证这一步仍然是本卡的接受规则。
- [[sys-spec-sys]]：系统侧：平均接受长度怎样决定草稿长度和吞吐，拒绝后 KV 怎么截。
