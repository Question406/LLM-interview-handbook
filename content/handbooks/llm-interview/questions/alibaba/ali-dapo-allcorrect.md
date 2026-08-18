---
id: ali-dapo-allcorrect
section: alibaba
order: 10
level: A
title: Group 里样本全对或全错时 GRPO 会怎样？DAPO 怎么处理？
quick: 组内无相对差异 → advantage≈0，梯度信号消失。DAPO 等通过动态采样、非对称裁剪、或过滤无效 group 等机制保证仍有有效更新。
tags:
  - Alibaba
  - DAPO
  - GSPO
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>组内无相对差异 → advantage≈0，梯度信号消失。DAPO 等通过动态采样、非对称裁剪、或过滤无效 group 等机制保证仍有有效更新。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>这是 reasoning RL 的经典 failure mode：难题全错、简单题全对，相对优势学不到东西。</p>
<p>回答结构：</p>
<ol>
<li>先解释 GRPO 依赖组内相对差异；</li>
<li>指出全对/全错导致 A 塌缩；</li>
<li>引出 DAPO/Dr.GRPO 等对采样、裁剪、标准化的修正；</li>
<li>落到实践：按难度 curriculum、保证 group 多样性、监控空 group 比例。</li>
</ol>
<p>阿里方向额外建议熟悉 Qwen <b>GSPO</b>：序列级重要性比与裁剪视角，和 token-level GRPO 对照着讲。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a></div>
