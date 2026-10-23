---
id: dt-packed-sft-code
section: tech-screen
order: 6
level: A
title: CoderPad：packed SFT 的 loss mask 怎么写，哪些 token 不能进梯度？
quick: "SFT 学的是给定上下文时助手怎么回答，所以只对助手回复算交叉熵，prompt、padding 和工具返回都不进监督目标。packed 序列里不同样本之间还要切断注意力，不然后一个样本能看到前一个的答案。漏掉 mask，模型就会同时学着重建用户文本和工具返回。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - SFT
  - Loss Mask
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "LLaMA: Open and Efficient Foundation Language Models"
    url: https://arxiv.org/abs/2302.13971
    type: primary
---

我只对助手回复算交叉熵，prompt、padding 和工具返回都不进 loss，样本边界上的预测也不算。SFT 的目标是 $p(\text{assistant}\mid\text{context})$，用户的话、系统提示和工具返回都只是条件。

常见写错有两种：整段算 CE，或者只屏蔽了 prompt、漏掉工具 observation。比如一条工具轨迹里，数据库返回了一大段 JSON，observation 进了 loss，就等于让模型背数据库；邮件摘要任务里用户原文进了 loss，模型就在学重建用户邮件。预训练文档的 CE 可以几乎全开，对话和工具轨迹必须按角色 mask。

## 先定哪些 token 是监督目标

角色用整数编码，因为张量装不了字符串。`superv` 先只留下一个 token 是 assistant 的位置，再去掉跨样本的预测，最后按有效 token 数归一化。

```python
import torch
import torch.nn.functional as F

# 张量不能装字符串，角色用整数编码
ROLE = {"bos": 0, "system": 1, "user": 2, "assistant": 3, "tool": 4, "pad": 5}


def sft_ce(logits, targets, roles, same_doc):
    """packed SFT 的交叉熵，只监督 assistant token。

    logits: [T, V]；targets: [T]，位置 t 的 logits 预测 targets[t + 1]；
    roles: [T] 整数角色（见 ROLE）；same_doc: [T] 每个 token 所属样本 id。
    返回有效 token 上的平均负对数似然；没有有效 token 时返回 0。
    """
    if not (logits.shape[0] == targets.shape[0] == roles.shape[0] == same_doc.shape[0]):
        raise ValueError("logits, targets, roles and same_doc must share length T")
    logp = F.log_softmax(logits[:-1].float(), dim=-1)
    gold = targets[1:]
    role_next = roles[1:]
    doc = same_doc[:-1]
    doc_next = same_doc[1:]

    superv = role_next == ROLE["assistant"]  # tool、user、system、pad 都不进 loss
    # 跨样本边界不预测：packed 时上一条的尾不能当这一条的条件
    superv = superv & (doc == doc_next)

    n_tokens = superv.sum().clamp_min(1)
    token_lp = logp.gather(-1, gold.unsqueeze(-1)).squeeze(-1)
    return -(token_lp * superv).sum() / n_tokens
```

测试覆盖均匀 logits、非 assistant 位置不影响 loss、跨边界、归一化和没有 assistant 的情况：

```python
import math

V = 4
# 两条样本拼在一起：样本 0 = user, assistant, assistant；样本 1 = tool, assistant；最后 pad
role_names = ["user", "assistant", "assistant", "tool", "assistant", "pad"]
roles = torch.tensor([ROLE[name] for name in role_names])
same_doc = torch.tensor([0, 0, 0, 1, 1, -1])
targets = torch.tensor([0, 1, 2, 3, 1, 0])

# 均匀 logits：每个被监督 token 的 NLL 都是 log V
uniform = torch.zeros(6, V)
assert math.isclose(sft_ce(uniform, targets, roles, same_doc).item(), math.log(V), rel_tol=1e-6)

# 只有 assistant token 进 loss：改 user / tool / pad 目标对应的 logits 不影响结果
logits = torch.randn(6, V, generator=torch.Generator().manual_seed(0))
base_loss = sft_ce(logits, targets, roles, same_doc)
perturbed = logits.clone()
perturbed[2] += 5.0  # 位置 2 预测位置 3 的 tool token
perturbed[4] += 5.0  # 位置 4 预测位置 5 的 pad
assert torch.allclose(sft_ce(perturbed, targets, roles, same_doc), base_loss)

# 跨样本边界不监督：位置 3（tool）预测位置 4（assistant），同一样本时进 loss；
# 把位置 4 标成另一条样本的开头后，这次预测跨了边界，不再进 loss
boundary_doc = torch.tensor([0, 0, 0, 1, 2, -1])
logits_peak = torch.zeros(6, V)
logits_peak[3, targets[4]] = 10.0  # 只让位置 3 -> 4 这次预测很准
loss_same_doc = sft_ce(logits_peak, targets, roles, same_doc)
loss_split_doc = sft_ce(logits_peak, targets, roles, boundary_doc)
assert loss_same_doc < loss_split_doc

# 按有效 token 数归一化：样本 0 的两个 assistant + 样本 1 的一个 assistant = 3 个
manual = -torch.log_softmax(logits[:-1], -1)[[0, 1, 3], targets[[1, 2, 4]]].mean()
assert torch.allclose(base_loss, manual)

# 没有 assistant token 时返回 0，而不是除零得到 nan
no_assistant = torch.tensor([ROLE["user"]] * 6)
assert sft_ce(logits, targets, no_assistant, same_doc).item() == 0.0
```

讲代码时我会点四处。归一化除以有效 token 数，别除以 $T$，不然短回复会被长 pad 稀释。packed 序列在样本交界处必须切断注意力，至少要切断 loss；只切 loss、不切注意力，下一条样本还是能看见上一条的答案。`tool` 角色永远不进 `superv`，只有最终对用户说的那句 assistant 才进。隐私上，用户文本只出现在条件里，梯度只落在助手输出上，比如邮件摘要只监督摘要那一侧，模型就不会学着重建用户原文，见 `dt-privacy-feedback`。复杂度就是一次 `log_softmax` 加 gather，和普通 CE 一样是 $O(TV)$。

mask 错了，再好的 verifier 也没用，因为模型在背 prompt。检查方法很简单：抽一条 packed 样本，打印 `superv` 的位置，看是不是只落在答案上。这是 data team 自己就该会做的检查。

## 追问

**多轮对话监督哪一轮？**
默认只监督当前这轮助手回复，历史当条件。把历史里的助手话也打开，等于重复训练旧示范。

**思维链要不要 mask 掉最终答案之前的 token？**
过程检查通过就打开；过程是假的，就只打开最终答案，见 `dt-synth-reasoning`。

**预训练的 packed 序列呢？**
用文档级 CE，只去掉 pad 并处理文档边界，别把 SFT 的 mask 套到 core pretrain 上。

**只切 loss 不切注意力够不够？**
不够。下一条样本还是能注意到上一条的答案，样本交界处要把注意力也切断。

相关：`dt-privacy-feedback`、`dt-synth-reasoning`
