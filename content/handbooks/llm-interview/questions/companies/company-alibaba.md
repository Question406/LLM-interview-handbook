---
id: company-alibaba
section: companies
order: 1
level: A
title: 阿里 / Qwen / 淘天：应该重点准备什么？
quick: >-
  算法岗先刷「13 · 阿里 LLM 人才计划真题」：DPO→GRPO→GSPO、淘天 Agent 链、Skill/Memory/RAG、双十一护栏。
  笔试与研发手撕另刷「16 · 阿里校招笔试与研发面」。系统题回 Architecture/Systems。
tags:
  - Alibaba
  - Qwen
  - 真题导航
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
  - title: ↗ Qwen GSPO blog
    url: 'https://qwenlm.github.io/blog/gspo/'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>算法岗先刷「13 · 阿里 LLM 人才计划真题」：DPO→GRPO→DAPO/GSPO、淘天 Agent 链、Skill/Memory/RAG、生产护栏。笔试编程、手撕和研发八股另刷「16 · 阿里校招笔试与研发面」。系统题回 Architecture/Systems。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>算法主线：</b>SFT 数据与 mask → preference/DPO → on-policy reasoning RL → GRPO failure modes → DAPO/Dr.GRPO/<b>GSPO</b>（Qwen 尤相关）。</p>
<p><b>Agent 主线：</b>Tool/MCP/Skill、Memory/RAG 边界、trajectory 与 final-reward credit、评测与 Guardrail、高并发降级。</p>
<p><b>系统主线：</b>RoPE/GQA、LoRA、ZeRO、KV Cache、推理优化。</p>
<p><b>笔试 / 研发面：</b>第 16 章覆盖近年淘天/国际/AI 研发公开机试（不相邻偶数对、环形灯、分糖果、宝石、救援站、模乘循环、下标差 $k$ 重排等）、手撕高频和 Java/Redis/MQ/MySQL/秒杀。</p>
<p>第 13 章按公开淘天/国际/闪购面经拆成独立真题卡；过笔试后再按第 16 章补机试变形题。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a><a href="https://qwenlm.github.io/blog/gspo/" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO blog</a></div>
