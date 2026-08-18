---
id: pt-online-preference-loop
section: posttrain
order: 26
level: S
title: 为什么 Offline DPO 做到后面常要引入 Online Preference Loop？
quick: >-
  固定偏好数据只覆盖旧策略会生成的区域。policy 变强后会走出 dataset support，离线 pair
  的边际信息下降；在线循环通过“当前策略采样→标注/打分→更新”持续补齐新分布，但也把 reward hacking 和标注质量带回系统。
tags:
  - DPO
  - Online RLHF
  - Data
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: Iterative Preference Learning
    url: 'https://arxiv.org/abs/2312.11456'
    type: legacy-reference
  - title: DPO 原论文
    url: 'https://arxiv.org/abs/2305.18290'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>Offline DPO 稳定又便宜，但它只能比较数据集已有的回答。模型更新后会把概率质量推向未被标注的新区域；此时继续重复旧 pair，既可能没有信息，也可能把数据中的长度/风格偏差放大。</p><ol><li>用当前或近期 policy 为同一 prompt 采样多个候选；</li><li>用人工、RM 或 verifier 生成带置信度的偏好；</li><li>以严格版本化的 policy、prompt、labeler 记录数据，再做受 KL/质量门控的更新；</li><li>保留固定 held-out human eval，检查 online reward 是否与真正质量一起提升。</li></ol><p>关键风险是“自己的 judge 给自己打分”。因此 online loop 需要独立审计集、对抗样本和数据去重，而不只是更频繁地训练。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2312.11456" target="_blank" rel="noreferrer">Iterative Preference Learning</a><a href="https://arxiv.org/abs/2305.18290" target="_blank" rel="noreferrer">DPO 原论文</a></div></div>
