---
id: ali-grpo-kl-vs-ppo
section: alibaba
order: 6
level: A
title: GRPO 的 KL 和 PPO 的 KL 是一模一样的吗？
quick: >-
  目标都是约束 π 靠近参考/旧策略，但实现细节常不同：参考对象（π_ref vs π_old）、估计位置（token/sequence）、是否进 loss
  或做 early-stop，面试要说清你用的实现。
tags:
  - Alibaba
  - GRPO
  - PPO
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>目标都是约束 π 靠近参考/旧策略，但实现细节常不同：参考对象（π_ref vs π_old）、估计位置（token/sequence）、是否进 loss 或做 early-stop，面试要说清你用的实现。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>相似点：都用 KL 防止更新过猛或奖励劫持。</p>
<p>常见差异：</p>
<ul>
<li><b>参考谁：</b>对齐阶段常用冻结 SFT 作 <code>π_ref</code>；PPO 实现里也常见相对 <code>π_old</code> 的近似 KL。</li>
<li><b>怎么估：</b>token-level 平均 KL、序列级 KL、或近似 KL；系数 β 调度也不同。</li>
<li><b>作用方式：</b>有的进 loss，有的做 target/阈值 early stop。</li>
</ul>
<p>阿里面经喜欢追：你监控哪些指标（KL、entropy、reward、崩坏率）来判断 KL 项是否过强/过弱。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>
