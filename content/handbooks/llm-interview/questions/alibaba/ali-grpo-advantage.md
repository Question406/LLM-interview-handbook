---
id: ali-grpo-advantage
section: alibaba
order: 4
level: S
title: GRPO 的 Advantage 怎么算？为什么不能直接用 raw reward？
quick: >-
  同 prompt 采一组样本，用组内 reward 均值/方差做相对标准化得到 A。直接用 raw reward
  尺度不稳、同组不可比，且难区分“都还行”和“明显更好”。
tags:
  - Alibaba
  - GRPO
  - Advantage
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>同 prompt 采一组样本，用组内 reward 均值/方差做相对标准化得到 A。直接用 raw reward 尺度不稳、同组不可比，且难区分“都还行”和“明显更好”。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>典型做法：对同一 <code>x</code> 采样 G 条输出，得到奖励 <code>r_1…r_G</code>，令</p>
<p><code>A_i = (r_i - mean(r)) / (std(r) + ε)</code></p>
<p>（细节实现会有 baseline、length 归一、token 广播等变体。）</p>
<p>不用 raw reward 的原因：</p>
<ul>
<li>不同 prompt 难度不同，绝对分不可比；</li>
<li>reward 尺度漂移会让更新过猛或过弱；</li>
<li>相对优势更贴近“在当前组里谁更好”，方差通常更可控。</li>
</ul>
<p>若 group 内全对或全错，A≈0，学习信号消失——这正是 DAPO 等改进要处理的 failure mode。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>
