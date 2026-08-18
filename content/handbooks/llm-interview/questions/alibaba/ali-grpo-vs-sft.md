---
id: ali-grpo-vs-sft
section: alibaba
order: 2
level: S
title: 阿里国际算法面：为什么选 GRPO 而不是继续 SFT / 蒸馏？
quick: SFT 适合教格式与示范轨迹；蒸馏适合逼近 teacher 分布；GRPO 适合有可验证/可打分目标、需要探索与相对优势更新时。选型看信号类型，不是谁更新。
tags:
  - Alibaba
  - GRPO
  - SFT
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>SFT 适合教格式与示范轨迹；蒸馏适合逼近 teacher 分布；GRPO 适合有可验证/可打分目标、需要探索与相对优势更新时。选型看信号类型，不是谁更新。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>公开阿里国际大模型算法面常开场就问技术选型：</p>
<ul>
<li><b>继续 SFT：</b>有高质量示范、格式/工具协议要稳定、需要快速对齐行为分布时优先。局限是缺乏探索，容易模仿 teacher 的平均行为，难突破上限。</li>
<li><b>蒸馏：</b>有强 teacher、希望小模型逼近其输出分布；仍是监督学习，突破 teacher 上限更难。</li>
<li><b>GRPO：</b>同 prompt 多样本、组内相对优势，适合数学/代码/可验证任务，或有明确 reward/verifier 的 Agent 场景；能做 on-policy 探索。</li>
</ul>
<p>面试回答要点：先说任务奖励是否可验证、数据是否成对 preference、是否需要探索；再落到你项目里为何选这条线。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>什么时候三者可以串行？</summary><div class="follow-answer"><p>常见流水线是 SFT 打底 → DPO/偏好对齐 → on-policy GRPO 做 reasoning/工具成功率；蒸馏可穿插在压缩或部署模型阶段。</p></div></details></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>
