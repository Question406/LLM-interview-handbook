---
id: sys-eos-mask
section: systems
order: 59
level: B
title: 系统：一条回答在 EOS 之后的 token，还进不进后训练 loss？
quick: "不进。EOS 本身进不进要和采样、奖励对齐，全队用同一个约定。 EOS 之后的垫片若计入 loss，模型会被推向把 pad id 的概率抬高，长度和奖励都会歪。"
tags:
  - Post-train
  - Mask
  - EOS
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

和 `sys-adv-bcast` 是同一条 mask。这道单独问结束符，因为采样、奖励和 loss 经常各写各的。

## 约定

生成在遇到 EOS 或达到最大长度时停。loss 的 mask 在停之后是 0。最大长度截断、没有 EOS 的那条，截断前的 token 仍然是模型生成的，应该进 loss，同时奖励里可以有一笔长度惩罚，两者不要混成「截断的整条都丢掉」。

EOS 这个 token 若进 loss，模型在学「在这里停止」。若不进，停止只靠采样规则。两种都能训，但不能采样时把 EOS 算进 logprob、训练时又 mask 掉。重要性采样的两边 mask 必须相同。

## 奖励用的字符串

解码给沙箱或匹配答案时，不要把 pad 和 EOS 后面的碎片解码进去。奖励看到的文本应和 mask 为 1 的那段一致。否则测试失败是因为多了一个垫片字符，梯度却在改前面的正文。

## 代码

```python
import torch

def response_mask(token_ids, prompt_len, eos_id, include_eos=True):
    # token_ids: [T], prompt occupies [0, prompt_len)
    mask = torch.zeros_like(token_ids, dtype=torch.float)
    hits = (token_ids[prompt_len:] == eos_id).nonzero()
    if len(hits) == 0:
        end = token_ids.numel()
    else:
        end = prompt_len + int(hits[0]) + (1 if include_eos else 0)
    mask[prompt_len:end] = 1
    return mask
```

## 追问

**pack 好几条回答到一条序列里呢？** 每条自己的 EOS 和文档边界都要切断注意力，也要切断 loss。用一条序列的最后一个 EOS 当全部回答的结尾，前面几条的 pad 会进损失。边界见 `coding-packed-lm`。

## 相关题

- [[sys-adv-bcast]]：同一条 response mask，那题问序列级优势怎么乘到 token 上、prompt 和工具返回为什么是 0。
- [[p3a-openai-masked-cross-entropy-loss]]：NumPy 手写带 mask 的交叉熵，练的是 SFT 侧「只在有效 token 上求平均」。
- [[coding-packed-lm]]：追问里多条回答 pack 在一起时，注意力边界怎么用 `cu_seqlens` 和块对角 mask 切。
- [[meta-pack-seq]]：packing 时文档之间为什么要隔离，以及拼上 EOS 为什么不等于隔离。
