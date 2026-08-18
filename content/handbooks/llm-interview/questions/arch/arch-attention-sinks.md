---
id: arch-attention-sinks
section: arch
order: 20
level: A
title: Attention Sink 是什么？滑动窗口长上下文为什么不能简单删除最早 token？
quick: >-
  有些模型会持续给开头少数 token 分配注意力质量，即使它们语义信息很少。直接裁掉这些“锚点”可能让 softmax 分布失稳；streaming
  方案常保留少量 sink token 再滑动近期窗口。
tags:
  - Long Context
  - Attention
  - KV Cache
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: StreamingLLM / attention sinks
    url: 'https://arxiv.org/abs/2309.17453'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>在无限流式输入中，KV cache 不能无限增长。朴素 FIFO eviction 看似合理，却可能突然损坏模型习惯使用的注意力锚点。Attention sink 指的正是这类长期吸收注意力质量的位置。</p><ul><li><b>现象：</b>首 token/特殊 token 即使语义贡献小，也可能反复得到较高 attention mass。</li><li><b>工程策略：</b>保留固定数量的初始 sink token，加上最近窗口；若用专门 sink，需要与训练/位置编码策略匹配。</li><li><b>别过度泛化：</b>是否存在、保留多少、是否影响任务质量都要做长流 eval；它不是所有模型都同样有效的通用定律。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2309.17453" target="_blank" rel="noreferrer">StreamingLLM / attention sinks</a></div></div>
