---
id: sys-left-pad
section: systems
order: 61
level: A
title: 系统：生成用左填充，打分为什么会打到 prompt 上？
quick: "生成的左填充和奖励模型的打分索引必须一起检查，分数要取在回答最后一个真实 token 上。变长 prompt 左填充后，不能沿用右填充的长度减一规则；要结合 attention mask、prompt 长度和回答边界定位。取到 prompt 上，奖励就可能与回答内容无关。"
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

左填充时，奖励模型要按回答的实际边界取分，不能直接沿用右填充的索引习惯。比如前面补了 pad，却只按真实长度减一定位，位置就可能落回 prompt。一个公开 RLHF 实现记录过生成用左填充、奖励打到 prompt 上的 bug，这道题据此整理；loss mask 见 `sys-eos-mask`。

同一批里 prompt 长短不同。逐 token 生成（decode） 一步要一个矩形张量。把 pad 放在左边，各条已经写出的 token 在右边对齐，位置和 KV 的增长方向一致。右填充则每条的「下一个 token」不在同一列，不能一次采样。

训练前向可以右填充。两条路径的 pad 方向不同是正常的。打分索引则要按对应路径的 padding 和回答边界重新计算。

句尾是这条回答的最后一个非 pad、并且属于回答而不是 prompt 的位置。左填充时，序列开头的 pad 不算，prompt 的最后一个 token 也不算，除非奖励故意打在问题上。实现上用 attention mask 和 prompt 长度一起算，不要用 `logits[:, -1]`。

取错位置时，奖励和回答内容无关，优势变成噪声，loss 仍会下降，因为模型在拟合一个稳定的错误标签。

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

**tokenizer 的 pad id 和 eos id 相同呢？**
不能靠「等于 eos」判断结尾。用长度。生成停在 eos 之后，回答长度是停之前的 token 数，含不含 eos 与 `sys-eos-mask` 的约定一致。

## 相关题

- [[align-reward-model]]：RM 本身怎么训、为什么只有分差可信；这张只管 RM 在哪个位置取分。
