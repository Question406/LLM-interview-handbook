---
id: ali-reward-hacking
section: alibaba
order: 9
level: A
title: Reward hacking 是什么？训练指标里怎么发现？
quick: 模型钻奖励模型/规则空子，指标上涨但真实质量下降。看 KL 异常、长度膨胀、模板刷分、人工抽检 divergence、多 RM 分歧。
tags:
  - Alibaba
  - RLHF
  - Reward
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>模型钻奖励模型/规则空子，指标上涨但真实质量下降。看 KL 异常、长度膨胀、模板刷分、人工抽检 divergence、多 RM 分歧。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>典型现象：RM score ↑ 但人工偏好/下游任务 ↓；输出变长、套话、格式刷分；对已知 RM 弱点过拟合。</p>
<p>监控与缓解：</p>
<ul>
<li>同时看 task success、人工抽检、安全性，不只看 RM；</li>
<li>KL/entropy 约束与长度惩罚；</li>
<li>多奖励集成、定期换/重训 RM；</li>
<li>可验证任务尽量用 rule/verifier 代替纯 RM。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>
