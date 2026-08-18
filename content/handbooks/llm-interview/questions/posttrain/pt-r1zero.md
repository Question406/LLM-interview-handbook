---
id: pt-r1zero
section: posttrain
order: 17
level: S
title: R1-Zero 为什么重要？RL 是否真的“创造”了推理？
quick: >-
  R1-Zero 展示了 strong base model 在可验证 reward 的 RL 下，即使没有传统 long-CoT cold-start
  SFT，也能显著强化 reasoning behavior；但这不能证明 RL 从零创造了 pretraining 中完全不存在的新算法。
tags:
  - DeepSeek-R1
  - Reasoning RL
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>R1-Zero 展示了 strong base model 在可验证 reward 的 RL 下，即使没有传统 long-CoT cold-start SFT，也能显著强化 reasoning behavior；但这不能证明 RL 从零创造了 pretraining 中完全不存在的新算法。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>一个更稳妥的机制解释是：</p><ol><li><b>Search：</b>base policy 的长尾分布中偶尔采到成功 reasoning。</li><li><b>Selection：</b>verifier 给成功 trajectory 更高 reward。</li><li><b>Amplification：</b>policy gradient 提高成功轨迹及相关 token/action 的概率。</li><li><b>Better search：</b>新 policy 更常进入有用 reasoning region，形成正反馈。</li></ol><p>这可能放大 latent capability、增加 test-time computation、重新组合已有 primitive；要证明“新算法学习”需要更强实验，例如控制 pretraining exposure、寻找 genuinely novel algorithmic generalization、分析可压缩程序结构或 causal intervention。</p><p>最终 R1 仍使用 cold-start data，说明 SFT 仍对 readability、语言一致性、输出格式与行为 prior 有重要作用。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么 math/code 特别适合这种 RL？</summary><div class="follow-answer"><p>有 cheap、objective、scalable verifier，reward 信号更干净，能做大规模 on-policy search。</p></div></details><details class="followup"><summary>怎么区分“更多 token”与“更好 algorithm”？</summary><div class="follow-answer"><p>固定 token budget、同长度匹配、截断/压缩 counterfactual、测试更高难度/分布外算法组合。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2501.12948" target="_blank" rel="noopener noreferrer">↗ DeepSeek-R1</a></div>
