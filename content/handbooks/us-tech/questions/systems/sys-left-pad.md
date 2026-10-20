---
id: sys-left-pad
section: systems
order: 61
level: A
title: 系统：生成用左填充，打分为什么会打到 prompt 上？
quick: "一批变长 输入提示（prompt） 左填充，是为了让已生成的 token 在右侧对齐，方便一次 逐 token 生成（decode）。 奖励模型若用「最后一个非 pad」当句尾，左填充时这个位置可能还在 输入提示里。打分位置要和回答的最后一个真实 token 对齐。"
tags:
  - Post-train
  - Padding
  - Reward Model
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: RLHF-pipeline，左填充下奖励打到了 prompt token
    url: https://github.com/TheYellowDuck/RLHF-pipeline
    type: primary
---

## 题怎么来的

一个公开的 基于人类反馈的强化学习（RLHF） 实现记录过这个 bug：PPO 和 GRPO 的生成几乎总是左填充，奖励模型却按右填充的习惯去取「最后一个位置」，取到的是 输入提示（prompt）。这道把这个坑写成题。损失（loss） 的 mask 见 `sys-eos-mask`。

## 为什么生成要左填充

同一批里 prompt 长短不同。逐 token 生成（decode） 一步要一个矩形张量。把 pad 放在左边，各条已经写出的 token 在右边对齐，位置和 KV 的增长方向一致。右填充则每条的「下一个 token」不在同一列，不能一次采样。

训练前向可以右填充。两条路径的 pad 方向不同是正常的。不正常的是用同一套「最后一个下标」去打分。

## 打分位置

句尾是这条回答的最后一个非 pad、并且属于回答而不是 prompt 的位置。左填充时，序列开头的 pad 不算，prompt 的最后一个 token 也不算，除非奖励故意打在问题上。实现上用 attention mask 和 prompt 长度一起算，不要用 `logits[:, -1]`。

取错位置时，奖励和回答内容无关，优势变成噪声，loss 仍会下降，因为模型在拟合一个稳定的错误标签。

## 代码

```python
def last_response_index(attention_mask, prompt_lens):
    # attention_mask: [B, T], 1 on real tokens. Prompts are left-padded.
    lengths = attention_mask.sum(dim=-1)
    last = lengths - 1
    start = attention_mask.size(1) - lengths
    prompt_end = start + prompt_lens
    if (last < prompt_end).any():
        raise RuntimeError("score landed inside the prompt")
    return last
```

## 追问

**tokenizer 的 pad id 和 eos id 相同呢？** 不能靠「等于 eos」判断结尾。用长度。生成停在 eos 之后，回答长度是停之前的 token 数，含不含 eos 与 `sys-eos-mask` 的约定一致。

## 相关题

- [[align-reward-model]]：RM 本身怎么训、为什么只有分差可信；这张只管 RM 在哪个位置取分。
