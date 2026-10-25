---
id: sys-ref-model
section: systems
order: 52
level: A
title: 系统：KL 的参考模型放哪，为什么不算第二份 Adam？
quick: "参考模型冻结 bf16 权重，只做前向取 logprob，每参数权重约 2 字节，没有梯度和 Adam 状态。显存紧可分片或卸载；DPO 还可预计算参考 logprob，实时 KL 则需要参考前向，且参考参数不能随策略更新。"
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

KL 参考模型只需要冻结的权重和前向临时空间，不需要再算一份 Adam 的 12 字节状态。以 bf16 为例，权重每参数 2 字节，前向有激活，但可以减小 micro batch，也不用保存反向图。把它按另一个每参数 16 字节的训练副本估算，会多算很多。

参考模型在一个训练阶段中保持不变，策略则每步更新。因此两者不能指向同一块会被 step 改写的参数存储。否则第一步 KL 为 0，之后参考也跟着策略变化，固定参照就丢了。完整的字节账见 `sys-param-bytes`。

DPO 需要的是那对回答的参考 logprob，可以提前计算并存入数据，不必在线保留可运行的参考模型。PPO / GRPO 如果在损失中实时计算 KL，每步就需要一次参考前向。这道题按这些算法中 $\pi_{\mathrm{ref}}$ 的用法拟成。

显存紧时，可以像策略一样用 ZeRO-3 分片，只在需要时拼参数，避免每张卡复制一整份 70B。若与 rollout 引擎共置，生成阶段不需要参考模型，可以随训练状态一起卸到 CPU。若该 KL 项的系数为 0 且不再需要参考前向，就不加载它，省去权重和计算。

下面关闭参考模型的梯度和 dropout，取回答 token 的 logprob，再计算 KL 项：

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

**参考模型的 dropout 要和策略一样开着吗？**
不需要。参考前向用评估模式。开着 dropout，同一回答两次的 logprob 就可能不同，KL 会随之抖动。
