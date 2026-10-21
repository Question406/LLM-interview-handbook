---
id: dt-llama4-rl-recipe
section: posttrain-data
order: 31
level: S
title: Llama 4 博客里的 RL 数据配方是什么？
quick: "公开流程是轻量 SFT → 在线 RL → 轻量 DPO，理由是 SFT 太多会限制后续在线探索。数据侧三步：先砍掉过易样本，再按当前策略的 pass@$k$ 动态筛题、丢弃零优势组，同时在 batch 里混合能力与提示模板。过滤随策略更新反复做，每训一轮就用新策略重筛。"
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
updatedAt: 2026-10-12
sources:
  - title: "The Llama 4 herd (Meta)"
    url: https://ai.meta.com/blog/llama-4-multimodal-intelligence/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Llama 4 公开的流程是轻量 SFT、在线 RL，最后用轻量 DPO 打磨回复细节。核心理由是 SFT 做得太多会限制后续的在线探索，在推理、代码和数学上尤其明显。数据配方围绕这一点展开：砍掉简单题，跟着当前策略动态筛题，并混合不同能力。出处是 2025-04 Llama 4 技术博客里 Maverick 的后训练一节。

## 为什么 SFT 要轻、题表要动

简单题会占掉训练步数，却几乎不提供信号；在 RL 阶段，一组回答全对或全错的 prompt 优势为零，也没有梯度。策略在变，哪些题全对、全错也跟着变，开训前滤一次就冻住的题表，很快会塞满零优势的题。

## 数据侧的三步

第一步，减少简单的 SFT 样本。用 Llama 判断哪些是 easy，小模型丢掉约 50%，Behemoth（约 2T 总参）丢到 95%，剩下的难题做轻量 SFT。这和 `dt-math-passk-band`、`dt-filter-too-hard` 是同一个方向。

第二步，在线 RL 跟着策略筛题。用当前策略算 pass@$k$，只保留中等到难的输入提示（prompt）；训一轮，再用新策略筛一轮，如此循环，零优势的 prompt 动态丢掉。Behemoth 那节还写了按难度做 curriculum。这就是 `dt-agent-passk-zero` 背后的实验室配方。

第三步，混合能力和提示模板。同一个 batch 里混数学、推理和代码，避免策略只往一个领域偏。系统提示也要多样，不然推理和代码上的指令跟随会掉。换到 agent 场景，一个 batch 里要混不同仓库、不同工具 schema。

连续在线 RL 还需要异步基础设施，这属于系统层面的事。数据岗要讲清楚的是，过滤是训练循环的一部分，每轮都要重跑。

## 用到 agent 上

博客没写 SWE 容器的细节。SWE-RL 走的是另一条路，用 oracle patch 相似度做奖励，见 `dt-agent-reward-spec`。现场可以把 Llama 4 当作「题目怎么进 RL 队列」的范本：砍 easy、砍零优势、混能力、提示多样。环境本身仍然要有自己的 grader。

## 追问

- **DPO 还要吗？** 要，但放在最后、做得很轻，只处理回复质量上的边角问题。主要的能力来自 RL。
- **easy 判官会不会误杀难题？** 会。我会按能力分组统计误杀率，代码桶用针对代码调过的 easy 判官，聊天场景的判官不适用。
- **和 R1 的冷启动有什么区别？** R1 也是少量 SFT 再接 RL。Llama 4 多写了两点：SFT 过多有害，以及在线筛题。我会按后一点来维护题表。
