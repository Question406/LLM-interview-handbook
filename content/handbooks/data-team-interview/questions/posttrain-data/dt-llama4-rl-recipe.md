---
id: dt-llama4-rl-recipe
section: posttrain-data
order: 31
level: S
title: Llama 4 博客里的 RL data mixture 是什么？
quick: >-
  Llama 4 走轻量 SFT → 在线 RL → 轻量 DPO，理由是 SFT 太多会限制后续在线探索。数据侧先砍掉过易样本，再按 current
  policy 的 pass@$k$ 动态筛题、丢弃零优势组，batch 里混合能力与提示模板。过滤随 policy update
  反复做，每训一轮就用新策略重筛。
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Llama 4 herd (Meta)
    url: 'https://ai.meta.com/blog/llama-4-multimodal-intelligence/'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Llama 4 公开的流程是轻量 SFT、在线 RL，最后用轻量 DPO 打磨回复细节。核心理由是 SFT 做得太多会限制后续的在线探索，在推理、代码和数学上尤其明显。data mixture 都围着这一点转：砍掉简单题，跟着 current policy 动态筛题，混合不同能力。出处是 2025-04 Llama 4 技术博客里 Maverick 的 post-training 一节。

先说题表为什么要跟着策略动。一道题开训时模型有时做对、有时做错，正好有信号；训了几轮之后每次都对，它再留在队列里，一组回答优势全为零，没有 gradient。简单题本来就占训练步数、几乎不给信号，策略一变，哪些题全对、全错也跟着变，开训前滤一次就冻住的题表，很快会塞满零优势的题。

所以第一步是减少简单的 SFT 样本。他们用 Llama 判断哪些是 easy，small model 丢掉约 50%，Behemoth（约 2T 总参）丢到 95%，剩下的难题做轻量 SFT。这和 `dt-math-passk-band`、`dt-filter-too-hard` 是同一个方向。

进了在线 RL，就跟着策略筛题。用 current policy 算 pass@$k$，只保留中等到难的 prompt；训一轮，再用新策略筛一轮，如此循环，零优势的 prompt 动态丢掉。Behemoth 那节还写了按难度做 curriculum。`dt-agent-passk-zero` 背后就是这套实验室配方。

同时还要混能力和提示模板。同一个 batch 里混数学、推理和代码，避免策略只往一个领域偏；系统提示也要多样，不然推理和代码上的 instruction following 会掉。换到 agent 场景，一个 batch 里要混不同仓库、不同工具 schema。

连续在线 RL 还需要异步基础设施，那属于系统层面。数据岗要讲清楚的是，过滤是训练循环的一部分，每轮都要重跑。

## 追问

**DPO 还要吗？**
要，但放在最后、做得很轻，只处理回复质量上的边角问题。主要的能力来自 RL。

**easy 判官会不会 false rejection 难题？**
会。我会按能力分组统计 false rejection 率，代码桶用针对代码调过的 easy 判官，聊天场景的判官不适用。

**和 R1 的冷启动有什么区别？**
R1 也是少量 SFT 再接 RL。Llama 4 多写了两点，SFT 过多有害，以及在线筛题。我会按后一点来维护题表。

**SWE 环境能照搬这套吗？**
题目怎么进 RL 队列可以照搬：砍 easy、砍零优势、混能力、提示多样。博客没写 SWE 容器的细节，环境本身仍然要有自己的 grader。SWE-RL 走的是另一条路，用 oracle patch 相似度做奖励，见 `dt-agent-reward-spec`。

相关：`dt-math-passk-band`、`dt-filter-too-hard`、`dt-agent-passk-zero`、`dt-agent-reward-spec`
