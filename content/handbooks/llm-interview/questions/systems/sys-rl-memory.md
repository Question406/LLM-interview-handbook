---
id: sys-rl-memory
section: systems
order: 19
level: S
title: 7B 模型做 GRPO，显存主要花在哪里？怎么优化？
quick: >-
  GRPO 虽去掉 Critic，却不等于“显存只剩一个 7B”。训练侧仍有
  policy/reference/optimizer/activation，rollout 侧还有多条长序列与
  KV；应先按训练、rollout、通信三类峰值拆账，再选 ZeRO、checkpoint、长度/G、colocation 或 disaggregation。
tags:
  - GRPO
  - Memory
  - 真实面经
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: 2025 美团大模型面经
    url: 'https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>先拒绝背一个固定 GB 数。峰值取决于精度、optimizer、ZeRO stage、sequence length、group size、并行策略，以及训练与 rollout 是否 colocate。</p><ul><li><b>训练侧：</b>policy 参数、gradient、optimizer states、activation 和临时通信 buffer；reference 可冻结但仍要参与 KL/log-prob 计算。</li><li><b>rollout 侧：</b>每个 prompt 的 G 条长 completion 都会占用 KV cache 与采样 buffer。GRPO 省掉 critic，并没有消除 group rollout 的乘数。</li><li><b>优化顺序：</b>先缩无效长尾、控制 group size/并发；再用 activation checkpoint、ZeRO/FSDP、合适的 TP/PP；最后根据集群拓扑决定 colocate、异步 weight sync 或 rollout/训练解耦。</li></ul><p>要把“训练 OOM”和“serving KV OOM”分开，它们的最佳解不同。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0" target="_blank" rel="noreferrer">2025 美团大模型面经</a><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noreferrer">DeepSeekMath / GRPO</a></div></div>
