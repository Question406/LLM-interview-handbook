---
id: code-logprob-gather
section: rl-coding
order: 1
level: A
title: 手写从 logits gather token logprob，并乘 response mask
quick: "取 `logits[:, :-1]` 做 `log_softmax`，用 `token_ids[:, 1:]` 去 `gather`，再乘 shift 后的 response mask，prompt 和 pad 位都是 0。SFT、DPO、GRPO 都用这个原语，最容易错的是忘了 shift 和 prompt 没 mask 掉。"
tags:
  - Logprob
  - DPO
  - GRPO
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: TRL SFT Trainer
    url: https://huggingface.co/docs/trl/en/sft_trainer
    type: primary
  - title: torch.gather
    url: https://pytorch.org/docs/stable/generated/torch.gather.html
    type: primary
---

## 题目描述

从自回归模型logits中取出实际生成token的log概率，并仅保留目标token属于response的部分。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `token_logprobs(logits,token_ids,response_mask)`。logits为[B,T,V]浮点张量，`token_ids`为[B,T]合法词表编号，`response_mask`为[B,T]的0/1张量，T≥2。logits在位置t预测`token_ids`的位置t+1。

### 输出与约束

返回[B,T-1]的float32张量。第t项是`log_softmax`(logits[:,t])在`token_ids`[:,t+1]处的值，乘`response_mask`[:,t+1]；prompt及padding目标位置为0。最后一格logits和首个token编号不用于预测配对。

### 示例

```text
logits是[1,3,2]全零张量，token_ids=[[0,1,0]]，response_mask=[[0,0,1]]
输出 [[0,-ln(2)]]≈[[0,-0.693147]]。
```

## 解题思路与参考答案

思路就三步：用位置 $t$ 的 logits 去打第 $t+1$ 个 token，所以 logits 取 `[:, :-1]`、目标取 `[:, 1:]`；在 vocab 维上 `gather` 出目标 id 的 logp；再乘同样 shift 过的 response mask，把输入提示（prompt）和 pad 清零。直接偏好优化（DPO）要的 sequence logp、GRPO / PPO 要乘优势的 token logp、监督微调（SFT）的 token 交叉熵损失（CE），用的都是同一套索引和对齐。现场最常栽的两处，一是不 shift，用 $t$ 的 logits 去打 $t$ 自己；二是 prompt 没 mask 掉。

## 对齐：shift 和 mask

自回归的约定是，位置 $t$ 的隐状态只看得见 $1,\ldots,t$，logits 预测的是下一个 token。所以

$$
\log\pi(a_{t+1}\mid x_{\le t})=\mathrm{logsoftmax}(\ell_t)_{a_{t+1}}.
$$

实现上取 `logits[:, :-1]` 对 `token_ids[:, 1:]`，两边都 shift 才对齐。只 shift 一边，监督就挪错了一格，loss 看着在降，学的却是「预测当前已经看见的 token」。

`response_mask` 和 shift 后的序列同形：prompt 位为 $0$，模型写出的 completion（包括作为停止动作的 EOS）为 $1$，EOS 之后的 pad 为 $0$。Agent 场景里 Thought / Action 为 $1$，工具返回为 $0$。attention mask 要看见 prompt，损失计算范围却不能更新 prompt，两套 mask 从「哪一格开始为 1」就要分开。拿 attention mask 直接当损失计算范围，等于把题干当成动作来训。

举一条 $T=6$ 的序列，前 $4$ 个是 prompt，后 $2$ 个是回复（含 EOS）。shift 之后要对齐的是「用位置 $0,\ldots,4$ 的 logits 去打 token $1,\ldots,5$」。response mask 也要 slice 成 `[1:]`，这样 prompt 的 $4$ 个位置里，只有「prompt 最后一个 token 去预测回复第一个 token」那一格可能为 $1$，更早的 prompt-to-prompt 必须为 $0$。差一格，就会把系统提示的最后一个字训进去。TRL SFT 里常见的写法是 `labels` 把 prompt 写成 `-100`，和显式 mask 是同一套索引和对齐，只是用 ignore index 代替了乘法。

数值上用 `log_softmax`，别写 `log(softmax(...))`。FP16 / BF16 下先 `float()` 再 softmax 更稳，算完的 logp 可以再转回原 dtype。

## 手写

```python
import torch
import torch.nn.functional as F

def token_logprobs(logits, token_ids, response_mask):
    # logits: [B, T, V]  at t predicts token t+1
    # token_ids, response_mask: [B, T]
    logp = F.log_softmax(logits[:, :-1].float(), dim=-1)
    target = token_ids[:, 1:].unsqueeze(-1)
    tok = logp.gather(dim=-1, index=target).squeeze(-1)
    mask = response_mask[:, 1:].to(tok.dtype)
    return tok * mask
```

`gather` 的 `index` 要和 `logp` 维数相同，在 vocab 维上取出目标 id 那一条，别写成 `logp[:, :, token_ids]` 这种广播。返回 `[B, T-1]`，prompt 位已经是 $0$。序列 logp 是 `tok.sum(-1)`（DPO 的经典做法）；token-mean 就先 `tok.sum() / mask.sum().clamp_min(1)`（GRPO 常见）。具体怎么平均见损失聚合卡，先保证 mask 是对的。整个计算是一次 `log_softmax` 加一次 `gather`，开销在 $B\times T\times V$ 的 softmax 上，不用任何 Python 循环。

## 接到 DPO / GRPO

DPO 的四段 logp（policy / ref $\times$ chosen / rejected）都走这一个函数，然后算

$$
\beta\bigl[(\log\pi_c-\log\pi_r)-(\log\pi_c^{\mathrm{ref}}-\log\pi_r^{\mathrm{ref}})\bigr].
$$

GRPO 把 `token_logprobs` 当 $\log\pi_\theta$，和 `old` 相减得到 ratio，再乘组优势和同一个 mask。old / new / ref 都得是训练图上 gather 出来的结果，别混进 vLLM 采样时的 logp，见 `meituan-verl-recompute-logprob`。

写完我会现场自检一下：把 `mask==1` 的片段逐 token 解码（decode）出来，人眼看应该是助手回复；`mask.sum()` 应该等于 response 长度（shift 后差 1 要心里有数）。对不上就先修数据，再去调 $\beta$。HF CausalLM 的 `logits` 和 `input_ids` 同长，模型内部不会替你乘 response mask；`labels` 里的 `-100` 只影响框架自带的 CE，自己写 DPO / GRPO 必须显式 gather。chat template 里的 special token 归谁也要分清：系统和用户轮次算 prompt，模型这一轮发出的才算 response。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用非均匀 logits 和非重复 token 检查右移对齐。第一个预测位置的 response_mask 为零，输出应归零；第二个位置应取 token 0 的概率 0.75。

```python
import math
logits = torch.tensor([[[0., math.log(3)], [math.log(3), 0.], [0., 0.]]])
ids = torch.tensor([[0, 1, 0]])
mask = torch.tensor([[0, 0, 1]])
result = token_logprobs(logits, ids, mask)
torch.testing.assert_close(result, torch.tensor([[0., math.log(0.75)]]))
assert result.shape == (1, 2)
print("simple tests passed")
```

## 追问

**为什么要 shift？**
$\ell_t$ 预测的是 $a_{t+1}$。不 shift 就等于拿已经看见的 token 当标签，CE 虚低，策略梯度也指错了位置。

**prompt 漏进 mask 会有什么症状？**
系统提示被改、KL 虚高、奖励分数（reward）不动但 prompt 段的 logp 在涨。抽一条看 mask，比看曲线快。

**padding 呢？**
必须为 0。否则短答案会被 pad 稀释，长度奖励也会从 pad 那里漏出去。

**sum 还是 mean？**
DPO 常用序列 sum，强化学习（RL）常用 mask 内的 token-mean。先把 gather 写对，再说明怎么聚合。

**`gather` 和 `take_along_dim` 有区别吗？**
等价，index 都要 `unsqueeze` 到最后一维。别用 Python 循环去扫 vocab。

**`-100` 能不能代替 mask？**
SFT 可以。RL 和 DPO 还要在有效位上做平均或求和，显式 mask 更不容易漏。两种写法都要和 shift 用同一套边界。

**引擎给的 logp 能直接用吗？**
采样侧可以记下来做监控，但不能进 $\rho$。要在训练图上重新 forward，再走这个函数。

相关：`code-dpo`（完整 DPO）、`code-grpo`（组优势）、`sys-rl-response-mask`（mask 语义）
