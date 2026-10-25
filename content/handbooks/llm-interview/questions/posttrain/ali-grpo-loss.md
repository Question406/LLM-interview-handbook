---
id: ali-grpo-loss
section: posttrain
order: 3
level: S
title: 阿里算法面：请写出 GRPO Loss，并解释每一项
quick: "GRPO Loss 是 PPO 式的裁剪目标加一项 KL：用同题回答的评分差异算优势，鼓励正优势回答、抑制负优势回答。$\\rho_t$ 衡量当前模型相对采样模型的概率变化，clip 防止一次更新过大，$\\beta \\cdot \\mathrm{KL}$ 约束模型别离参考策略太远。"
tags:
  - Alibaba
  - GRPO
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>GRPO Loss 是 PPO 式的裁剪目标加一项 KL：用同题回答的评分差异算优势，鼓励正优势回答、抑制负优势回答。$\rho_t$ 衡量当前模型相对采样模型的概率变化，clip 防止一次更新过大，$\beta \cdot \mathrm{KL}$ 约束模型别离参考策略太远。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>这条损失做三件事：提高较好回答的生成概率，限制一次更新的幅度，保留参考模型已有的行为。白板上按 PPO 风格写出来就够用，前面的负号表示训练时最小化损失，相当于最大化后面的目标。</p>
$$L = -\mathbb{E}\bigl[ \min(\rho_t A_t, \mathrm{clip}(\rho_t, 1-\varepsilon, 1+\varepsilon) A_t) \bigr] + \beta \cdot \mathrm{KL}(\pi \,\|\, \pi_{\mathrm{ref}})$$
<p>其中 $\rho_t = \pi_\theta(y_t|x,y_{\lt t}) / \pi_{\mathrm{old}}(y_t|x,y_{\lt t})$。</p>
<ol>
<li><b>$\rho_t$</b> 是当前策略相对采样策略的概率比，衡量这一步更新有多大。</li>
<li><b>$A_t$</b> 在 GRPO 里通常由同组样本的奖励分数（reward）做相对标准化得到，决定更新的方向和强度。</li>
<li><b>clip</b> 限制单步更新，防止策略崩溃；min 取更保守的那一侧。</li>
<li><b>$\beta\,\mathrm{KL}$</b> 约束策略别偏离 SFT / 参考策略太远，抑制钻奖励规则的空子和语言崩坏。</li>
</ol>
<p>讲的时候我会强调，GRPO 的「相对」发生在 group 里，不依赖单独的价值评估模型（critic）或 value model，这是它相对 PPO 的工程简化。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>$\varepsilon$ 一般取多少？</summary><div class="follow-answer"><p>常见从 0.1 到 0.2 起步。太大更新不稳，太小学得慢，要结合 KL、奖励方差和崩坏率一起调。</p></div></details><details class="followup"><summary>为什么要 $\pi_{\mathrm{ref}}$？</summary><div class="follow-answer"><p>防止策略为了提高奖励分数，偏离原本可用的语言和行为分布。对齐阶段它也是安全锚点。</p></div></details></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>
