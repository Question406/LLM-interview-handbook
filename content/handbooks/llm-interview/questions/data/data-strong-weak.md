---
id: data-strong-weak
section: data
order: 12
level: A
title: Strong-to-Weak Distillation 什么时候有效？什么时候会失败？
quick: >-
  Teacher 能提供 student 自己难以搜索到但仍可模仿的高质量 trajectory 时有效；若 teacher reasoning 超出
  student capacity、风格过长、依赖不可见工具/知识或分布不匹配，直接 imitation 可能失败。
tags:
  - Distillation
  - Data
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: MiniLLM — knowledge distillation of large language models
    url: https://arxiv.org/abs/2306.08543
    type: primary
---

Teacher 最终答案好，不代表每个 token 都是 student 的最佳监督。强模型轨迹有效，当它提供 student 自己搜不到、但仍落在可模仿 frontier 上的路径；一旦推理长度、隐含知识或不可见工具超出容量，直接 SFT 会失败——student 背腔调、复现不了决策。陷阱是把「教师越强、数据越好」当公理。这和 teacher bias（`data-teacher-bias`）相连：即使可学，也可能把风格 shortcut 一并蒸进去。

## 有效条件：信号可学，而不是只正确

蒸馏有效需要 **teacher signal 可学**。可用 student 在该轨迹上的 likelihood、teacher-forced 成功率、或「student 自己采样能否在 $k$ 次内碰到等价答案」衡量可学性。完全不可能复现的长链，先压缩 rationale、拆子任务、或做 curriculum，而不是整段塞进 SFT。

实践旋钮：simplification / 长度截断、difficulty filtering、student-aware rejection sampling（只留 student 能部分复现的轨迹）、on-policy 蒸馏（用 student 自己的分布当提议，teacher 只打分或改写）。分布要匹配部署：teacher 用了检索/代码解释器而 student 线上没有，这条轨迹是不可见工具泄漏，不是能力。

## 失败怎么用实验拆开

对照至少四组：原始 teacher 轨迹、压缩后轨迹、student 自采样 + 过滤、人类/弱教师混合。看 student holdout、长度、格式服从，以及 OOD 是否回归。若只有「原样 imitation」涨、压缩版不涨，说明你在蒸风格而不是决策；若压缩版涨、原样掉，说明超容量。token budget 对齐再比，否则长 teacher 会赢在长度而不是正确。

失败常见四因：超出容量；风格过长占满梯度；依赖不可见工具/私有知识；teacher 与线上 query 分布不匹配。弱模型教弱模型或无验证回流，会滑向自污染（`data-synthetic-self-contamination`）。SFT pipeline（`data-sft-pipeline`）里 teacher 只是候选生成器，过门靠 verifier 和 student 边际增益。

可学性过滤本身要做成实验：按 student likelihood 分位切成易/中/难三档，分别训一小步，看哪一档边际最高。全难档掉点说明超容量；全易档不涨说明没有新信息。不要把「过滤后条数变少」当成质量下降——token 效率才是目标。面试收口：有效蒸馏是把 teacher 轨迹推回 student 的可学边界，而不是把最强模型的思维链原样粘贴。

## 追问

- **答案对、过程不可学怎么办？** 只监督 final answer、重写短 rationale，或拆成可验证子题；整段 CoT 进 loss 会蒸假推理。
- **一定要最强 teacher 吗？** 不必。中等、可复现、带 verifier 的轨迹，往往比超长闭源思维链更适合小模型。
- **和 Weak-to-Strong 什么关系？** 那是弱监督训强模型；本题是强轨迹教弱模型。两者都怕不可学信号，但容量瓶颈方向相反。
- **怎么证明蒸馏有效？** 同等 token 下对比「可学子集 vs 全量 imitation」，看 holdout 与 OOD，而不是只看 teacher 自己的分。
