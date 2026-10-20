---
id: dt-packed-sft-code
section: tech-screen
order: 6
level: A
title: CoderPad：packed SFT 的 loss mask 怎么写，哪些 token 不能进梯度？
quick: "把 packed 序列中的 prompt、padding 和工具返回排除出监督目标，只计算助手回复的交叉熵。不同样本之间还要切断注意力，避免后一个样本看到前一个答案。漏掉 mask，会让模型同时学习重建用户文本和工具返回。"
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

先定义 packed SFT 的监督范围：prompt、padding 和工具返回默认不计入 loss，只对助手回复计算交叉熵。样本边界还要切断注意力，防止跨样本读取。不能整段计算 CE，也不能只屏蔽 prompt 却遗漏工具 observation，否则训练会包含重建用户邮件和工具 JSON 的目标。

SFT 的目标是 $p(\text{assistant}\mid\text{context})$。用户话、系统提示、工具返回是条件，不是标签。预训练文档 CE 可以几乎全开；对话和工具轨迹必须按角色 mask。AFM 的工具数据是带执行返回的轨迹，observation 进 损失（loss） 等于背数据库。

## 先定哪些 文本处理单位（token） 是监督

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

### 可执行测试

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

口播这几处：

- 归一化。除以有效 token 数，不要除以 $T$。否则短完成被长 pad 稀释。
- 边界。packed 必须在样本交界切断注意力或至少切断 loss。只切 loss、不切注意力，会让下一条看见上一条答案。
- 工具。`tool` 角色永远不进 `superv`。最终对用户的那句 assistant 才进。
- 隐私。即使用户文本出现在条件里，梯度也不该重建用户原文。苹果默认用户邮件不进全球 FM；就算研究集里有，也只监督摘要侧，见 `dt-privacy-feedback`。

## 和数据质量的接头

mask 错了，再好的 验证器（verifier） 也没用：模型在背 prompt。抽查一条 packed 样本，打印 `superv` 的位置是否只落在答案。这是 data team 该会的，不一定要 kernel 岗才会。

## 追问

- **多轮对话 mask 哪一轮？** 默认只监督当前助手回复，历史当条件。把历史助手话也打开，等于重复旧示范。
- **思维链要不要 mask 掉最终答之前的 token？** 过程门过了就开；过程假只开最终答，见 `dt-synth-reasoning`。
- **预训练 packed 呢？** 文档 CE，只去掉 pad 和文档边界。不要把 SFT mask 套到 core pretrain 上。
