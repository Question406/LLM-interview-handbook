---
id: company-alibaba
section: companies
order: 1
level: A
title: 阿里 / Qwen / 淘天：应该重点准备什么？
quick: >-
  算法岗先刷「13 · 阿里 LLM 人才计划真题」：从 DPO 到 GRPO 再到 GSPO、淘天 Agent
  链、Skill/Memory/RAG、双十一护栏。笔试和研发手撕另刷「16 · 阿里校招笔试与研发面」。系统题回到 Architecture 和
  Systems。
tags:
  - Alibaba
  - Qwen
  - 真题导航
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>算法岗先刷「13 · 阿里 LLM 人才计划真题」：从 DPO 到 GRPO 再到 GSPO、淘天 Agent 链、Skill/Memory/RAG、双十一护栏。笔试和研发手撕另刷「16 · 阿里校招笔试与研发面」。系统题回到 Architecture 和 Systems。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>算法主线：</b>SFT 数据和 mask，再到 preference/DPO，再到 on-policy reasoning RL，然后是 GRPO 的失败模式，以及 DAPO、Dr.GRPO、<b>GSPO</b>（Qwen 尤其相关）。</p>
<p><b>Agent 主线：</b>Tool/MCP/Skill、Memory 和 RAG 的边界、trajectory 与最终 reward 的 credit、评测和 Guardrail、高并发怎么降级。</p>
<p><b>系统主线：</b>RoPE/GQA、LoRA、ZeRO、KV Cache、推理优化。</p>
<p><b>笔试 / 研发面：</b>第 16 章覆盖近年淘天、国际、AI 研发公开机试（不相邻偶数对、环形灯、分糖果、宝石、救援站、模乘循环、下标差 $k$ 重排等）、手撕高频，以及 Java/Redis/MQ/MySQL/秒杀。</p>
<p>第 13 章按公开淘天、国际、闪购面经拆成独立真题卡。过了笔试，再按第 16 章补机试变形题。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a><a href="https://qwenlm.github.io/blog/gspo/" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO blog</a></div>
