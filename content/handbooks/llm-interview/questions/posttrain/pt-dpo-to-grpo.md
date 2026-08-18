---
id: pt-dpo-to-grpo
section: posttrain
order: 24
level: S
title: DPO 后模型分布变尖，还能直接接 GRPO 吗？
quick: >-
  可以，但先确认当前 policy 还有足够 rollout diversity。若同题采样几乎相同，组内 reward 方差接近 0，GRPO
  的相对优势会失去信号；应先恢复可控探索并监控能力漂移。
tags:
  - DPO
  - GRPO
  - 真实面经
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: 2026 淘天 Agent 面经
    url: 'https://www.nowcoder.com/discuss/909920471301226496'
    type: legacy-reference
  - title: DPO 原论文
    url: 'https://arxiv.org/abs/2305.18290'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>可以把它看成一个合理的 warm start：DPO 先把策略带到较好的偏好区域，GRPO 再用当前策略的在线采样继续探索。但“DPO 一定让熵变低”并不成立；真正要检查的是同一 prompt 的候选是否还存在有效差异。</p><ul><li><b>先看信号：</b>组内 reward std、unique response rate、pass@k、token entropy 和 chosen/rejected margin。若一组全对或全错，relative advantage 近似为 0。</li><li><b>再恢复探索：</b>适度调高 rollout temperature/top-p，使用熵约束或更保守的学习率；必要时混入 SFT/DPO replay，避免格式和通用能力漂移。</li><li><b>别忘了 reference：</b>以 DPO checkpoint 为锚更偏局部改进；以更早的 SFT 为锚会给探索更大空间，也会带来更强优化张力。</li></ul><p>不能只看训练 reward，要同时看组内方差、长度和独立 held-out eval。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://www.nowcoder.com/discuss/909920471301226496" target="_blank" rel="noreferrer">2026 淘天 Agent 面经</a><a href="https://arxiv.org/abs/2305.18290" target="_blank" rel="noreferrer">DPO 原论文</a><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noreferrer">DeepSeekMath / GRPO</a></div></div>
