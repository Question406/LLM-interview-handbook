---
id: dt-sycophancy-data
section: labs
order: 10
level: A
title: Anthropic：RLHF 什么时候会奖励不诚实？数据上怎么拆？
quick: "人评更偏爱客气附和的回答、给简短纠正打低分时，RLHF 就会奖励不诚实。数据上要拆开：用成对样本教模型纠正错误前提（chosen 按证据纠正，rejected 附和），标注协议把事实忠实和礼貌分成不同维度，评测单列谄媚切片。满意度高，单独证明不了模型诚实。"
companies:
  - apple
tags:
  - Anthropic
  - Sycophancy
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Towards Understanding Sycophancy in Language Models
    url: https://arxiv.org/abs/2310.13548
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

当标注员更喜欢「礼貌但错」的回答时，RLHF 就会奖励不诚实。修的办法在数据上：标注协议写明证据正确性优先于附和用户，用成对样本专门教模型纠正错误前提，并把事实和礼貌分成两个打分维度。

比如标注员看到两条回答，用户说某国首都是一个错误的城市，一条回答客气地同意，另一条简短地纠正。很多人会给前一条更高分，因为它礼貌、不顶撞，奖励模型（RM）从这些偏好里学到的就是附和用户。摘要任务里也一样：用户想听好消息，模型删掉限定词，人评觉得「更好读」。问题出在标签上，所以要从数据修。

具体先改标注协议，写明证据正确性优先于附和用户。然后造成对样本，用户前提错误时，chosen 依据证据纠正，rejected 顺着错误回答。摘要任务里补一批对抗题，材料里根本没有好消息，要求模型不编造，见 `dt-grounding-data`。评测时谄媚、有用性和忠实性分开报，免得总体满意度把附和的错误盖过去。回答可以用温和的语气纠正用户，标签上事实、礼貌这些维度要分开打；统一标一个「更好」，又会重新奖励附和。

## 追问

**有证据说明 RLHF 真会奖励附和吗？**
有。Anthropic 写过短文，描述基于人类反馈的强化学习（RLHF）系统性奖励不诚实的场景；Perez、Sharma 等人也测过，模型更愿意附和用户。

**加 KL 约束能挡住吗？**
挡不住。KL 约束只限制模型离参考策略多远，管不了标签本身偏向附和。

**在 Constitutional 原则里写一句「要诚实」够吗？**
不够。没有成对数据配合，它只是一条提示。

**用户就是想被附和怎么办？**
语气可以软，训练标签仍要分维度。混成一个「更好」，就回到了这题开头的问题。
