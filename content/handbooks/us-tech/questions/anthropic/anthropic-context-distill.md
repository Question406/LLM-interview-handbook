---
id: anthropic-context-distill
section: anthropic
order: 15
level: S
title: Anthropic：context distillation 把原则压进模型，和 system prompt 差在哪？
quick: >-
  System prompt 每次推理都占窗口，改一句立刻生效。Context distillation 用 KL 让学生在无原则条件下模仿「带原则的教师」，原则进权重、推理不再付那笔 token。换条款要重训；prompt
  改完当下就换。CAI 的 SL 改写是亲戚，不是同一个损失。
tags:
  - Anthropic
  - Distillation
  - Constitutional AI
  - System prompt
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: A General Language Assistant as a Laboratory for Alignment
    url: https://arxiv.org/abs/2112.00861
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
---

Askell 等人 2021 年的 *General Language Assistant* 把 context distillation 写进 Anthropic 早期对齐工具箱：长人格 / 原则 prompt 很有效，但占窗口、每步都算一遍。蒸馏想把「看见 $C$ 才有的行为」写进参数。面试对比的是现在人人会写的 system prompt，以及后来的 CAI。

## 损失是条件分布的 KL，不是把 $C$ 当监督文本

记 $p_0$ 为冻结教师，$C$ 为固定上下文（人格、条款、少样本），$x$ 来自一个大语料（常接近预训练分布）。学生 $p_\theta$ **看不到** $C$，目标是

$$
\mathcal{L}(\theta)=\mathbb{E}_{x}\bigl[D_{\mathrm{KL}}\bigl(p_0(\cdot\mid C,x)\big\|p_\theta(\cdot\mid x)\bigr)\bigr].
$$

实现上对 $p_0(\cdot\mid C,x)$ 采样或用教师 token 分布，对学生做 CE / KL。关键差别：直接在 $C$ 上 SFT，学的是 $p(C)$ 的续写，会把模型拉向「接下来还在背条款」；蒸馏学的是 $p(x\mid C)$ 在 $C$ 消失之后的行为。论文用数数的玩具例子说明过：finetune 在 $1{,}2,\ldots,63$ 上，不会立刻输出 64；prompt 会。蒸馏要对齐的是后者那种条件。

推理：学生不再把 $C$ 放进窗口，省 token、省 KV，也能消化「比窗口还长的原则」。代价是 $C$ 改一个标点，学生不会跟着变，除非再蒸一轮。

## 和 system prompt 的产品差

| | System prompt | Context distillation |
| --- | --- | --- |
| 生效 | 下次请求 | 训完部署 |
| 可检查 | 日志里能看见全文 | 进了权重，难审计某一条 |
| 窗口 | 每序列扣 $|C|$ | 推理时 $|C|=0$ |
| 个性化 | 每用户一段 prompt | 每用户蒸一次不现实 |
| 热更新 | 改文本 | 重训 / 再蒸馏 |

产品结论： **会变的、要审计的、按用户不同的** 放 prompt（安全政策热修、企业定制语气）。**稳定、长、每请求都付费的** 才值得蒸（通用无害原则、固定人格）。Claude 的公开 constitution 更适合当训练信号和对外说明，而不是每轮把全文贴进 200k 窗口——长窗口也有位置偏差，见 `anthropic-long-context`。

System prompt 还可以按请求切换：同一模型，一个会话严、一个会话松。蒸馏后的权重同时只带一套。要两套行为，要么两份学生，要么蒸馏只压公共核、差异仍留 prompt。

## 和 CAI / RLAIF 别并成一句话

CAI 的 SL 阶段：模型按条款批评、改写，再在改写上 SFT。那是 **离散的示范**，损失是普通 CE，不是对带 $C$ 教师分布的 KL。RLAIF 更远：对比 + PM + PPO，人在环的位置见 `anthropic-rlaif`。

可以说 CAI 的 SL 是「原则 → 数据 → 权重」，和蒸馏同一方向；不要说 CAI 就是 context distillation。蒸馏不需要对比，也不显式优化无害 Elo。它可能把教师 prompt 里的讨好、啰嗦一并压进去，因为 KL 对齐的是整分布。

失败模式：教师 $p_0(\cdot\mid C)$ 本身不稳，学生学会平均答案；语料 $x$ 和上线分布差太远，原则在 OOD 上掉；蒸完之后再叠一层冲突的 system prompt，行为以谁为准不清楚。我会在评测上同时跑「无 prompt 学生」和「有 $C$ 的教师」，看无害 / 有用缺口，而不是只看蒸馏损失。

论文还提过迭代蒸馏：蒸完再加一小段 prompt，等于把旧原则冻进权重、新原则仍可热插。这比每次把历史条款全贴进窗口更像长期记忆，但也更难回滚——权重里的旧 $C$ 不会因为你删了文本就消失。

## 追问

- **KL 方向？** 教师在前：$\mathrm{KL}(p_0(\cdot\mid C)\|p_\theta)$，学生去盖教师会的模式，避免反向 KL 那种模式寻求。和 RLHF 里 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$ 不是同一个位置，别混。
- **能不能蒸 tool 用法？** 能蒸「何时该调用」的倾向，不能蒸权限。权限必须留在宿主，见 `anthropic-tool-use`。
- **和 LoRA 一起用吗？** 实务上常蒸到 adapter，便于回滚。条款版本和 adapter 版本要钉在一起。
- **为什么不全部靠超长 system prompt？** 贵、有位置偏差、难保证中间条款被读到。蒸馏是把稳定部分预付进训练。
