---
id: anthropic-context-distill
section: anthropic
order: 15
level: S
title: Anthropic：context distillation 把原则压进模型，和 system prompt 差在哪？
quick: "Context distillation 让不带原则上下文的学生，用 KL 模仿带原则的教师，把固定行为压进权重。推理能省 token 和 KV，原则改变却需要重训；变化频繁、要审计或按用户定制的规则仍适合 system prompt。"
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

Context distillation 把稳定的上下文影响学进参数，system prompt 则在每次请求时提供规则。比如固定人格每轮都很长，可以让学生模仿带人格的教师，推理时省去这段输入；但规则临时改了，学生权重不会自动跟着改。

Askell 等人 2021 年的 General Language Assistant 把它用于早期对齐。长 prompt 能描述人格、原则和少样本，却占窗口且反复计算，蒸馏的目标是保留看到 $C$ 后的行为。

## 学教师行为，而非续写原则

记 $p_0$ 为冻结教师，$C$ 为固定上下文，$x$ 来自大语料、常接近预训练分布。学生 $p_\theta$ 看不到 $C$，用下面的目标对齐分布：

$$
\mathcal{L}(\theta)=\mathbb{E}_{x}\bigl[D_{\mathrm{KL}}\bigl(p_0(\cdot\mid C,x)\big\|p_\theta(\cdot\mid x)\bigr)\bigr].
$$

可以从 $p_0(\cdot\mid C,x)$ 采样，或使用教师 token 概率，计算学生的 CE 或 KL。若直接拿 $C$ 做 SFT，优化的是 $p(C)$ 的续写；蒸馏想保留的是 $p(x\mid C)$ 的条件行为。论文用数数说明：在 $1{,}2,\ldots,63$ 上 finetune 不会立刻输出 64，prompt 却能，目标是学后者。

学生推理不再输入 $C$，省 token 和 KV，也可以吸收比窗口长的原则。代价是 $C$ 改一个标点，仍要重新蒸馏才会改变权重。

| | System prompt | Context distillation |
| --- | --- | --- |
| 生效 | 下次请求 | 训完部署 |
| 可检查 | 日志里能看见全文 | 进了权重，难审计某一条 |
| 窗口 | 每序列扣 $|C|$ | 推理时 $|C|=0$ |
| 个性化 | 每用户一段 prompt | 每用户蒸一次不现实 |
| 热更新 | 改文本 | 重训 / 再蒸馏 |

所以安全政策热修、企业语气和按用户变化的要求可放 prompt；稳定、长、每请求重复的通用无害原则或固定人格才值得蒸。公开 constitution 也可作为训练信号与对外说明，无须每轮贴进 200k 窗口，长上下文本身还有位置偏差，见 `anthropic-long-context`。

同一模型可用不同 prompt 切换行为，蒸馏权重通常同时只带一套。需要两套时，可以维护两个学生，或只蒸公共部分，把差异留在 prompt。

## 和 CAI 的训练步骤分清

CAI 的 SL 阶段按条款批评、改写，再对离散示范做普通 CE；context distillation 对齐带 $C$ 的教师分布，用 KL。RLAIF 还包括比较、PM、PPO，见 `anthropic-rlaif`。两者都能把原则影响写进权重，但蒸馏无需偏好比较，也不显式优化无害 Elo，教师的讨好和啰嗦也可能一并被学到。

教师 $p_0(\cdot\mid C)$ 不稳时，学生可能学到平均行为；训练语料 $x$ 与上线 OOD 差得远时，原则可能失效；蒸馏后再加冲突 system prompt，也会造成行为不清。评测应同时运行无 prompt 学生和有 $C$ 教师，比较无害、有用缺口，不能只看训练损失。

论文还提到迭代蒸馏：旧原则进权重，新原则用短 prompt 加上。这样减少重复上下文，也增加回滚难度，删掉文本并不会删掉权重里的旧 $C$。

## 追问

**KL 方向是什么？**
教师在前，$\mathrm{KL}(p_0(\cdot\mid C)\|p_\theta)$，让学生覆盖教师模式。它与 RLHF 的 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}})$ 位置不同，后者会有模式寻求特性。

**能蒸工具调用吗？**
可以学何时调用的倾向，权限仍留在宿主，见 `anthropic-tool-use`。

**可以和 LoRA 配合吗？**
可以蒸到 adapter 便于回滚，条款版本与 adapter 版本一起记录。

**为何不全放超长 prompt？**
每次付输入成本，也有位置偏差；稳定部分蒸进权重可以预先承担训练成本。
