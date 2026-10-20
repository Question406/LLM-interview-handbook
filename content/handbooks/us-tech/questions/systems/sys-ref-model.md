---
id: sys-ref-model
section: systems
order: 52
level: A
title: 系统：KL 的参考模型放哪，为什么不算第二份 Adam？
quick: >-
  参考模型是冻结的 bf16 权重，只做前向，拿 logprob。没有梯度，也没有优化器状态。
  KL 系数为 0 就可以不加载。它和正在更新的策略不能共用一块会被 step 改掉的存储。
tags:
  - Post-train
  - KL
  - Reference Model
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: verl 配置说明
    url: https://verl.readthedocs.io/en/latest/examples/config.html
    type: primary
---

## 题怎么来的

后训练显存题里，参考模型经常被估成「又一个 16 字节」。按直接偏好优化（DPO）和 PPO 里 $\pi_{\mathrm{ref}}$ 的用法拟的。字节账见 `sys-param-bytes`。

## 它实际占什么

一份 bf16 参数，2 字节一个参数。前向和策略一样要激活，但可以更小的 micro batch，而且不用存反向图。Adam 的 12 字节不要算进去。

策略每步都在变。参考模型在一个训练阶段里不动。把参考模型指向策略的同一组参数，第一步 KL 是 0，step 之后参考也跟着走，KL 就失去了固定的参考。

DPO 不用一份跑得起来的参考模型做在线前向，它要的是采样那一对回答时的参考 logprob，可以提前算好存进数据。PPO / GRPO 若在损失中实时计算 KL，就要在每步前向里跑一次参考模型。

## 放哪

显存紧：参考模型和策略一样用 ZeRO-3，用的时候再拼参数。不要为了省事在每张卡复制一整份 70B。与生成轨迹的 rollout 引擎共置时，参考模型跟训练状态一起卸到 CPU，生成阶段不需要它。

KL 系数为 0：不加载，省掉这次前向。这是产品选择，不是把 KL 项写成 0 还留着模块。

## 代码

```python
import torch
import torch.nn.functional as F

@torch.no_grad()
def ref_logprobs(ref, input_ids, labels, response_mask):
    ref.eval()
    logits = ref(input_ids).logits[:, :-1]
    logp = F.log_softmax(logits.float(), dim=-1)
    tok = logp.gather(-1, labels[:, 1:].unsqueeze(-1)).squeeze(-1)
    return tok * response_mask[:, 1:]

def k3_kl(policy_logp, ref_logp):
    # value is nonnegative; gradient flows only into policy_logp
    delta = ref_logp.detach() - policy_logp
    return torch.exp(delta) - delta - 1
```

## 追问

**参考模型要不要和策略用同一个 dropout？** 不要。参考前向是评估，dropout 关掉。开着的话，同一条回答两次前向的 logprob 不同，KL 在抖。
