---
id: company-alibaba
section: companies
order: 1
level: A
title: 阿里 / Qwen / 淘天：应该重点准备什么？
quick: >-
  阿里算法岗的主线是从 DPO 到 GRPO 再到 GSPO，Agent 方向会问淘天 Agent 链、Skill/Memory/RAG
  和双十一护栏。用左侧「按公司」筛阿里能一次看完；笔试和研发手撕另刷「阿里校招笔试与研发面」，系统题回到 Architecture 和 Systems。
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>阿里算法岗的主线是从 DPO 到 GRPO 再到 GSPO，Agent 方向会问淘天 Agent 链、Skill/Memory/RAG 和双十一护栏。用左侧「按公司」筛阿里能一次看完；笔试和研发手撕另刷「阿里校招笔试与研发面」，系统题回到 Architecture 和 Systems。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>阿里的算法真题已经按主题拆进 Post-Training、Agent、系统等章，准备时用「按公司 · 阿里」一次看完就行。整体按三条线走，笔试再单独补。</p>
<p>算法这条线从 SFT 的数据和 mask 讲起，接着是 preference/DPO，再到 on-policy reasoning RL，然后讲 GRPO 的失败模式，以及 DAPO、Dr.GRPO、<b>GSPO</b> 各改了什么。GSPO 和 Qwen 尤其相关，要多准备。</p>
<p>Agent 这条线会问 Tool/MCP/Skill 怎么分，Memory 与 RAG 有何区别，最终奖励怎么归因到轨迹里的各步动作，还有评测和 Guardrail、高并发时怎么降级。</p>
<p>系统这条线主要是 RoPE/GQA、LoRA、ZeRO、KV Cache 和推理优化。</p>
<p>笔试和研发面单独刷「阿里校招笔试与研发面」。那张卡覆盖近年淘天、国际、AI 研发的公开机试（不相邻偶数对、环形灯、分糖果、宝石、救援站、模乘循环、下标差 $k$ 重排等）、手撕高频，以及 Java/Redis/MQ/MySQL/秒杀。过了笔试，再补机试变形题。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a><a href="https://qwenlm.github.io/blog/gspo/" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO blog</a></div>
