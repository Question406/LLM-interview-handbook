---
id: code-logprob-gather
section: coding
order: 219
level: A
title: 手写从 logits gather token logprob，并乘 response mask
quick: >-
  因果 LM 用 $\mathrm{logits}_{t}$ 预测 token $t+1$：先对 vocab 做 $\mathrm{log\_softmax}$，再
  `gather` 目标 id，乘 response mask。Prompt、pad 必须为 0。这是 SFT / DPO / GRPO 的同一原语，不要把
  prompt 算进损失，也不要忘记 shift。
tags:
  - Logprob
  - DPO
  - GRPO
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: TRL SFT Trainer
    url: https://huggingface.co/docs/trl/en/sft_trainer
    type: primary
  - title: torch.gather
    url: https://pytorch.org/docs/stable/generated/torch.gather.html
    type: primary
---

DPO 要 sequence logp，GRPO / PPO 要 token logp 再乘优势，SFT 的 token CE 是同一条索引链。本题把原语写对；完整 DPO 见 `code-dpo`，组优势见 `code-grpo`，mask 语义见 `sys-rl-response-mask`。采样引擎上的 logp 不能直接进 ratio，见 `meituan-verl-recompute-logprob`。陷阱有两处：**不 shift**（用 $t$ 的 logits 去打 $t$ 自己），以及 **prompt 没 mask 掉**。

## 对齐：shift 和 mask

自回归约定：位置 $t$ 的隐状态只看见 $1,\ldots,t$，logits 预测的是 **下一个** token。因此

$$
\log\pi(a_{t+1}\mid x_{\le t})=\mathrm{logsoftmax}(\ell_t)_{a_{t+1}}.
$$

实现上取 `logits[:, :-1]` 对 `token_ids[:, 1:]`。两边都 shift 才对齐；只 shift 一边会把监督挪错一格，看起来 loss 在降，学的是「预测当前已经看见的 token」。

`response_mask` 与 shift 后的序列同形：prompt 位 $0$，模型写出的 completion（含作为停止动作的 EOS）为 $1$，EOS 之后的 pad 为 $0$。Agent 里 Thought / Action 为 $1$，工具返回为 $0$。attention mask 必须看见 prompt，**loss mask 不能更新 prompt**，两套从「哪一格开始为 1」分开。用 attention mask 直接当 loss mask，是把题干当动作训。

数值用 `log_softmax`，不要 `log(softmax(...))`。FP16 / BF16 下先 `float()` 再 softmax 更稳，logp 仍可乘回原 dtype。

举一条 $T=6$ 的序列：前 $4$ 个是 prompt，后 $2$ 个是回复（含 EOS）。shift 之后要对齐的是「用位置 $0,\ldots,4$ 的 logits 去打 token $1,\ldots,5$」。response mask 也要 slice 成 `[1:]`，于是 prompt 的 $4$ 个位置里只有「prompt 最后一个 token 去预测回复第一个 token」那一格可能为 $1$，更早的 prompt-to-prompt 必须为 $0$。差一格就会把系统提示的最后一个字训进去。TRL SFT 里常见 `labels` 把 prompt 写成 `-100`，本质是同一条 mask，只是用 ignore index 代替显式乘法。

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

`gather` 的 `index` 必须和 `logp` 同维数：在 vocab 维上取出目标 id 的那一条，不要写成 `logp[:, :, token_ids]` 这类广播。返回值 `[B, T-1]`，prompt 位已经是 $0$。序列 logp 为 `tok.sum(-1)`（DPO 经典）；token-mean 则先 `tok.sum() / mask.sum().clamp_min(1)`（GRPO 常见）。平均方式见损失聚合卡，**先保证 mask 对**。

## 接到 DPO / GRPO

四段 logp（policy / ref $\times$ chosen / rejected）都走同一函数，再做

$$
\beta\bigl[(\log\pi_c-\log\pi_r)-(\log\pi_c^{\mathrm{ref}}-\log\pi_r^{\mathrm{ref}})\bigr].
$$

GRPO 把 `token_logprobs` 当 $\log\pi_\theta$，与 `old` 相减得 ratio，再乘组优势和同一 mask。old / new / ref 都必须是训练图上的 gather 结果，不要混进 vLLM 采样 logp。

现场自检：decode `mask==1` 的片段，人眼应是助手回复；`mask.sum()` 应等于 response 长度（shift 后差 1 要心里有数）。对不上先修数据，再调 $\beta$。HF CausalLM 的 `logits` 与 `input_ids` 同长，**不会在模型内部替你乘 response mask**；`labels` 里的 `-100` 只影响框架自带的 CE，自己写 DPO / GRPO 必须显式 gather。chat template 的 special token 算谁的：系统 / 用户轮次是 prompt，模型这一轮发出的才是 response。

## 追问

- **为什么要 shift？** $\ell_t$ 预测 $a_{t+1}$。不 shift 等于用已经看见的 token 当标签，CE 虚低、策略梯度指错位置。
- **prompt 漏进 mask 的症状？** 系统提示被改、KL 虚高、reward 不动但 prompt 段 logp 涨。抽一条看 mask 比看曲线快。
- **padding 呢？** 必须为 0。否则短答案被 pad 稀释，长度奖励从 pad 漏出。
- **sum 还是 mean？** DPO 常用序列 sum；RL 常用 mask 内 token-mean。先写 gather，再声明聚合。
- **`gather` 和 `take_along_dim`？** 等价，index 都要 `unsqueeze` 到最后一维。不要用 Python 循环扫 vocab。
- **`-100` 能不能代替 mask？** SFT 可以；RL / DPO 还要在有效位上做平均或求和，显式 mask 更不容易漏。两种写法必须和 shift 同一套边界。
- **引擎 logp 能 gather 吗？** 采样侧可以记来监控，不能进 $\rho$。训练图上重新 forward 再走本函数，见 `meituan-verl-recompute-logprob`。
