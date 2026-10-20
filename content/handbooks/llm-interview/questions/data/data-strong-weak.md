---
id: data-strong-weak
section: data
order: 12
level: A
title: Strong-to-Weak Distillation 什么时候有效？什么时候会失败？
quick: "当教师提供的高质量轨迹是学生自己难以找到、但仍能模仿的，蒸馏才有效。如果教师推理超出学生能力、过程过长、依赖学生没有的工具或知识，或与部署任务分布不一致，直接模仿可能失败。"
tags:
  - Distillation
  - Data
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: MiniLLM — knowledge distillation of large language models
    url: https://arxiv.org/abs/2306.08543
    type: primary
---

Teacher 最终答案好，不代表每个 token 都适合作为学生模型的监督。强模型轨迹有效，当它提供 student 自己搜不到、但仍落在可模仿 frontier 上的路径；一旦推理长度、隐含知识或不可见工具超出容量，直接 监督微调（SFT） 会失败。学生可能只学到措辞，却无法复现决策。常见误区是：把「教师越强、数据越好」当公理。这和 教师模型（teacher） bias（`data-teacher-bias`）相连：即使可学，也可能把风格 shortcut 一并蒸进去。

## 有效条件：信号可学，别只看正确

蒸馏有效需要 teacher signal 可学。可用 student 在该轨迹上的 likelihood、teacher-forced 成功率、或「student 自己采样能否在 $k$ 次内碰到等价答案」衡量可学性。完全不可能复现的很长的推理过程，先压缩 rationale、拆子任务、或做 curriculum，而不是整段塞进 SFT。

可尝试的方法包括：simplification / 长度截断、difficulty filtering、student-aware rejection sampling（只留 student 能部分复现的轨迹）、on-policy 蒸馏（用 student 自己的分布当提议，teacher 只打分或改写）。分布要匹配部署：teacher 用了检索/代码解释器而 student 线上没有，这条轨迹是不可见工具泄漏，不是能力。

## 失败怎么用实验拆开

对照至少四组：原始 teacher 轨迹、压缩后轨迹、student 自采样 + 过滤、人类/弱教师混合。看 student holdout、长度、格式服从，以及 分布外数据（OOD，即与训练数据明显不同的数据） 是否回归。若只有「原样 imitation」涨、压缩版不涨，说明你在蒸风格而不是决策；若压缩版涨、原样掉，说明超容量。token budget 对齐再比，否则长 teacher 会赢在长度而不是正确。

失败常见四因：超出容量；风格过长占满梯度；依赖不可见工具/私有知识；teacher 与线上 query 分布不匹配。弱模型教弱模型或无验证回流，会滑向自污染（`data-synthetic-self-contamination`）。SFT pipeline（`data-sft-pipeline`）里 teacher 只是候选生成器，过门靠 验证器（verifier） 和 student 边际增益。

可学性过滤本身要做成实验：按 student likelihood 分位切成易/中/难三档，分别训一小步，看哪一档边际最高。全难档掉点说明超容量；全易档不涨说明没有新信息。不要把「过滤后条数变少」当成质量下降，token 效率才是目标。有效蒸馏是把 teacher 轨迹推回 student 的可学边界，别把最强模型的思维链原样粘贴。

## 追问

- **答案对、过程不可学怎么办？** 只监督 final answer、重写短 rationale，或拆成可验证子题；整段 CoT 进 损失（loss） 会蒸假推理。
- **一定要最强 teacher 吗？** 不必。中等、可复现、带 verifier 的轨迹，往往比超长闭源思维链更适合小模型。
- **和 Weak-to-Strong 什么关系？** 那是弱监督训强模型；本题是强轨迹教弱模型。两者都怕不可学信号，但容量瓶颈方向相反。
- **怎么证明蒸馏有效？** 同等 token 下对比「可学子集 vs 全量 imitation」，看 holdout 与 OOD，而不是只看 teacher 自己的分。
